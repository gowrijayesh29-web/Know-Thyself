import json, random, string, sys, urllib.request, urllib.error

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
        with urllib.request.urlopen(req, timeout=120) as r:
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

rnd = ''.join(random.choices(string.ascii_lowercase, k=6))
s, b = call('POST', '/auth/register', {'email': 'smoke_%s@example.com' % rnd, 'password': 'Smoke1234!xy', 'full_name': 'Smoke Test', 'timezone': 'UTC', 'locale': 'en', 'accept_terms': True, 'marketing_consent': False})
if s not in (200, 201):
    print('FAIL register ->', s, str(b)[:300]); sys.exit(1)
tok = b['access_token']
body = {'mode': 'chat', 'context': 'SLEEP:\n- 2026-11-23: 7h 20m asleep, quality good', 'messages': [{'role': 'user', 'content': 'How did I sleep?'}]}
for prefix in ('/ai', '/intelligence'):
    s, b = call('POST', prefix + '/chat', body, tok)
    if s != 404:
        break
print(('PASS' if s == 200 else 'FAIL') + ' ai chat (' + prefix + '/chat) -> ' + str(s))
print('     ' + (str(b.get('reply'))[:300] if s == 200 and isinstance(b, dict) else str(b)[:500]))
