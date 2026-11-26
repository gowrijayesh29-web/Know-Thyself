import json, random, string, sys, datetime, urllib.request, urllib.error

BASE = 'http://127.0.0.1:8000/api/v1'

def call(method, path, body=None, token=None):
    headers, data = {}, None
    if body is not None:
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
s, b = call('POST', '/auth/register', {'email': 'smoke_%s@example.com' % rnd, 'password': 'Smoke1234!xy', 'full_name': 'Smoke Test', 'timezone': 'UTC', 'locale': 'en', 'accept_terms': True, 'marketing_consent': False})
if not show('register', s, (200, 201), b):
    sys.exit(1)
tok = b['access_token']

wake = datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0)
bed = wake - datetime.timedelta(hours=8)
start = bed + datetime.timedelta(minutes=15)
rec = {'date': wake.date().isoformat(), 'source': 'manual', 'bedtime': bed.isoformat(), 'sleep_start': start.isoformat(),
       'sleep_end': wake.isoformat(), 'wake_time': wake.isoformat(), 'time_in_bed_minutes': 480, 'total_sleep_minutes': 450,
       'awake_minutes': 15, 'sleep_latency_minutes': 15, 'quality_rating': 'good', 'screen_time_before_bed_minutes': 30,
       'caffeine_after_noon': True, 'alcohol_before_bed': False, 'exercise_before_bed': False, 'tags': [], 'interruption_details': []}
s, b = call('POST', '/physical/sleep', rec, tok)
sid = b.get('id') if show('create sleep', s, (201,), b) and isinstance(b, dict) else None

q = '?date_from=%s&date_to=%s&page=1&page_size=50' % (wake.date().isoformat(), wake.date().isoformat())
s, b = call('GET', '/physical/sleep' + q, token=tok)
if show('list sleep', s, (200,), b) and isinstance(b, dict):
    print('     items returned:', len(b.get('items', [])))

if sid:
    s, b = call('DELETE', '/physical/sleep/' + sid, token=tok)
    show('delete sleep', s, (204,), b)

print('\nALL BACKEND CHECKS PASSED' if all_ok else '\nSOME CHECKS FAILED - paste this output to Claude')
