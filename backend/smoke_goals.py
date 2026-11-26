import json, random, string, sys, datetime, urllib.request, urllib.error, urllib.parse

BASE = 'http://127.0.0.1:8000/api/v1'

def call(method, path, body=None, token=None, form=None):
    headers, data = {}, None
    if form is not None:
        data = urllib.parse.urlencode(form).encode()
        headers['Content-Type'] = 'application/x-www-form-urlencoded'
    elif body is not None:
        data = json.dumps(body).encode()
        headers['Content-Type'] = 'application/json'
    if token:
        headers['Authorization'] = 'Bearer ' + token
    req = urllib.request.Request(BASE + path, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
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

all_ok = True
def show(label, status, ok_codes, body):
    global all_ok
    ok = status in ok_codes
    print(('PASS ' if ok else 'FAIL ') + label + ' -> ' + str(status))
    if not ok:
        all_ok = False
        text = body if isinstance(body, str) else json.dumps(body)
        print('     ' + text[:700])
    return ok

rnd = ''.join(random.choices(string.ascii_lowercase, k=6))
email, pw = 'smoke_%s@example.com' % rnd, 'Smoke1234!xy'
today = datetime.date.today().isoformat()

s, b = call('POST', '/auth/register', {'email': email, 'password': pw, 'full_name': 'Smoke Test', 'timezone': 'UTC', 'locale': 'en', 'accept_terms': True, 'marketing_consent': False})
if not show('register', s, (200, 201), b):
    sys.exit(1)
token = b['access_token']

s, b = call('POST', '/auth/login', {'email': email, 'password': pw})
if s == 422:
    s, b = call('POST', '/auth/login', form={'username': email, 'password': pw})
    print('     (login needs form fields, not JSON)')
show('login', s, (200,), b)

goal = {'title': 'Smoke test goal', 'description': None, 'category': 'digital_wellbeing', 'frequency': 'daily',
        'target_value': 5, 'target_unit': 'hours', 'start_date': today, 'priority': 1, 'tags': [], 'reminder_enabled': False}
s, b = call('POST', '/goals', goal, token)
gid = b.get('id') if show('create goal', s, (201,), b) and isinstance(b, dict) else None

s, b = call('GET', '/goals?page=1&page_size=50', token=token)
if show('list goals', s, (200,), b) and isinstance(b, dict):
    print('     list response keys:', list(b.keys()))

if gid:
    s, b = call('POST', '/goals/%s/progress' % gid, {'date': today, 'value': 3, 'target_value': 5, 'achieved': False, 'source': 'manual'}, token)
    show('log progress', s, (201,), b)
    s, b = call('PUT', '/goals/%s' % gid, {'status': 'completed'}, token)
    show('complete goal', s, (200,), b)
    s, b = call('DELETE', '/goals/%s' % gid, token=token)
    show('delete goal', s, (204,), b)

print('\nALL BACKEND CHECKS PASSED' if all_ok else '\nSOME CHECKS FAILED - paste this output to Claude')
