import json, random, string, sys, datetime, urllib.request, urllib.error, urllib.parse

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

now = datetime.datetime.now(datetime.timezone.utc)
start = now - datetime.timedelta(minutes=45)
act = {'url': 'https://github.com', 'domain': 'github.com', 'title': 'Smoke test', 'category': 'development', 'is_productive': True,
       'start_time': start.isoformat(), 'end_time': now.isoformat(), 'duration_seconds': 2700, 'active_seconds': 2700, 'idle_seconds': 0, 'source': 'manual'}
s, b = call('POST', '/digital/activities', act, tok)
aid = b.get('id') if show('create activity', s, (201,), b) and isinstance(b, dict) else None

neutral = dict(act, domain='example.org', url='https://example.org', category='unclassified', is_productive=None)
s, b = call('POST', '/digital/activities', neutral, tok)
nid = b.get('id') if show('create neutral activity', s, (201,), b) and isinstance(b, dict) else None

q = urllib.parse.urlencode({'start_time_from': (now - datetime.timedelta(days=7)).isoformat(), 'start_time_to': (now + datetime.timedelta(days=1)).isoformat(), 'page': 1, 'page_size': 50})
s, b = call('GET', '/digital/activities?' + q, token=tok)
if show('list activities', s, (200,), b) and isinstance(b, dict):
    print('     items returned:', len(b.get('items', [])))

for label, rid in (('delete activity', aid), ('delete neutral activity', nid)):
    if rid:
        s, b = call('DELETE', '/digital/activities/' + rid, token=tok)
        show(label, s, (204,), b)

print('\nALL BACKEND CHECKS PASSED' if all_ok else '\nSOME CHECKS FAILED - paste this output to Claude')
