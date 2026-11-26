import ctypes, ctypes.wintypes as wt, datetime, getpass, json, os, time, urllib.error, urllib.request

API = os.environ.get('KT_API', 'http://127.0.0.1:8000/api/v1')
POLL, IDLE_LIMIT, MIN_SECONDS, MERGE_GAP = 2, 60, 15, 120
BROWSERS = {'brave.exe', 'chrome.exe', 'msedge.exe', 'firefox.exe', 'opera.exe', 'vivaldi.exe', 'iexplore.exe'}
SKIP = {'lockapp.exe', 'logonui.exe', 'searchhost.exe', 'shellexperiencehost.exe', 'startmenuexperiencehost.exe',
        'textinputhost.exe', 'applicationframehost.exe', 'dwm.exe'}
RULES = {
    'code.exe': ('development', True), 'cursor.exe': ('development', True), 'pycharm64.exe': ('development', True),
    'idea64.exe': ('development', True), 'windowsterminal.exe': ('development', True), 'powershell.exe': ('development', True),
    'cmd.exe': ('development', True), 'explorer.exe': ('productivity', None), 'notepad.exe': ('writing', True), 'notepad++.exe': ('development', True),
    'winword.exe': ('work', True), 'excel.exe': ('work', True), 'powerpnt.exe': ('work', True), 'onenote.exe': ('work', True),
    'acrobat.exe': ('reading', True), 'acrord32.exe': ('reading', True), 'figma.exe': ('design', True),
    'slack.exe': ('communication', True), 'teams.exe': ('communication', True), 'ms-teams.exe': ('communication', True),
    'zoom.exe': ('communication', True), 'whatsapp.exe': ('communication', None), 'telegram.exe': ('communication', None),
    'discord.exe': ('social_media', None), 'spotify.exe': ('music', None), 'vlc.exe': ('video', None),
    'steam.exe': ('gaming', False), 'epicgameslauncher.exe': ('gaming', False),
}

user32 = ctypes.WinDLL('user32', use_last_error=True)
kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
user32.GetForegroundWindow.restype = wt.HWND
user32.GetClassNameW.argtypes = [wt.HWND, wt.LPWSTR, ctypes.c_int]
user32.GetClassNameW.restype = ctypes.c_int
user32.GetWindowThreadProcessId.argtypes = [wt.HWND, ctypes.POINTER(wt.DWORD)]
user32.GetWindowThreadProcessId.restype = wt.DWORD
kernel32.OpenProcess.argtypes = [wt.DWORD, wt.BOOL, wt.DWORD]
kernel32.OpenProcess.restype = wt.HANDLE
kernel32.QueryFullProcessImageNameW.argtypes = [wt.HANDLE, wt.DWORD, wt.LPWSTR, ctypes.POINTER(wt.DWORD)]
kernel32.QueryFullProcessImageNameW.restype = wt.BOOL
kernel32.CloseHandle.argtypes = [wt.HANDLE]
kernel32.GetTickCount.restype = wt.DWORD


class LASTINPUTINFO(ctypes.Structure):
    _fields_ = [('cbSize', wt.UINT), ('dwTime', wt.DWORD)]


user32.GetLastInputInfo.argtypes = [ctypes.POINTER(LASTINPUTINFO)]


def idle_seconds():
    li = LASTINPUTINFO()
    li.cbSize = ctypes.sizeof(LASTINPUTINFO)
    if not user32.GetLastInputInfo(ctypes.byref(li)):
        return 0.0
    return ((kernel32.GetTickCount() - li.dwTime) & 0xFFFFFFFF) / 1000.0


def foreground_exe():
    hwnd = user32.GetForegroundWindow()
    if not hwnd:
        return None
    pid = wt.DWORD()
    user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
    if not pid.value:
        return None
    h = kernel32.OpenProcess(0x1000, False, pid.value)
    if not h:
        return None
    try:
        buf = ctypes.create_unicode_buffer(1024)
        size = wt.DWORD(1024)
        if not kernel32.QueryFullProcessImageNameW(h, 0, buf, ctypes.byref(size)):
            return None
        name = os.path.basename(buf.value).lower()
        if name == 'explorer.exe':
            cls = ctypes.create_unicode_buffer(256)
            user32.GetClassNameW(hwnd, cls, 256)
            if cls.value not in ('CabinetWClass', 'ExploreWClass'):
                return None
        return name
    finally:
        kernel32.CloseHandle(h)


def http(method, path, body=None, token=None):
    headers, data = {}, None
    if body is not None:
        data = json.dumps(body).encode()
        headers['Content-Type'] = 'application/json'
    if token:
        headers['Authorization'] = 'Bearer ' + token
    req = urllib.request.Request(API + path, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            raw = r.read().decode()
            return r.status, (json.loads(raw) if raw else None)
    except urllib.error.HTTPError as e:
        raw = e.read().decode()
        try:
            return e.code, json.loads(raw)
        except Exception:
            return e.code, raw
    except Exception as e:
        return 0, str(e)


S = {'email': '', 'pw': '', 'token': '', 'warned': False}


def login():
    s, b = http('POST', '/auth/login', {'email': S['email'], 'password': S['pw']})
    if s in (200, 201) and isinstance(b, dict) and b.get('access_token'):
        S['token'] = b['access_token']
        return True
    print('Login failed (%s): %s' % (s, str(b)[:200]))
    return False


def send(q):
    app = q['app']
    cat, prod = RULES.get(app, ('unclassified', None))
    secs = max(1, int(q['end'] - q['start']))
    act = min(int(q['active']), secs)
    iso = lambda t: datetime.datetime.fromtimestamp(t).astimezone().isoformat()
    body = {'url': 'https://app.local/' + app.replace('.exe', ''), 'domain': app, 'title': app, 'category': cat,
            'is_productive': prod, 'start_time': iso(q['start']), 'end_time': iso(q['end']), 'duration_seconds': secs,
            'active_seconds': act, 'idle_seconds': secs - act, 'source': 'extension'}
    tries = [body, dict(body, source='manual'), dict(body, source='manual', category='unclassified')]
    st, resp = 0, None
    for b in tries:
        st, resp = http('POST', '/digital/activities', b, S['token'])
        if st == 401 and login():
            st, resp = http('POST', '/digital/activities', b, S['token'])
        if st != 422:
            break
    if st == 422 and not S['warned']:
        print('Server rejected a record (422):', str(resp)[:300])
        S['warned'] = True
    return st


def flush(queue, everything):
    cutoff = time.time() - MERGE_GAP
    keep, sent = [], 0
    for i, q in enumerate(queue):
        if not everything and q['end'] > cutoff:
            keep.append(q)
            continue
        st = send(q)
        if st in (200, 201):
            sent += 1
            print('  uploaded %s (%d s)' % (q['app'], q['active']))
        elif st == 0 or st >= 500 or st in (401, 429):
            keep.append(q)
            keep.extend(queue[i + 1:])
            break
    queue[:] = keep
    return sent


def main():
    S['email'] = input('Know Thyself email [demo@knowthyself.app]: ').strip() or 'demo@knowthyself.app'
    S['pw'] = getpass.getpass('Password: ')
    if not login():
        return
    print('Tracking desktop apps (browsers are skipped, the extension covers them). Press Ctrl+C to stop.')
    queue, cur, last_flush = [], None, time.time()

    def finalize(c, end):
        secs = int(end - c['start'])
        if secs < MIN_SECONDS:
            return
        last = queue[-1] if queue else None
        if last and last['app'] == c['app'] and c['start'] - last['end'] < MERGE_GAP:
            last['end'] = end
            last['active'] += secs
        else:
            queue.append({'app': c['app'], 'start': c['start'], 'end': end, 'active': secs})

    try:
        while True:
            now = time.time()
            idle = idle_seconds()
            exe = foreground_exe() if idle < IDLE_LIMIT else None
            if exe in BROWSERS or exe in SKIP:
                exe = None
            if cur and exe != cur['app']:
                finalize(cur, now - idle if idle >= IDLE_LIMIT else now)
                cur = None
            if exe and not cur:
                cur = {'app': exe, 'start': now}
                print('[%s] now using %s' % (time.strftime('%H:%M:%S'), exe))
            if now - last_flush > 60:
                flush(queue, False)
                last_flush = now
            time.sleep(POLL)
    except KeyboardInterrupt:
        if cur:
            finalize(cur, time.time())
        print('Stopping, uploading what is left...')
        print('Uploaded %d session(s).' % flush(queue, True))


if __name__ == '__main__':
    main()
