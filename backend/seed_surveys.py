import json, sys, datetime, urllib.request, urllib.error

BASE = 'http://127.0.0.1:8000/api/v1'
EMAIL = sys.argv[1] if len(sys.argv) > 1 else 'demo@knowthyself.app'
PW = sys.argv[2] if len(sys.argv) > 2 else 'Demo1234!xy'

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

s, b = call('POST', '/auth/login', {'email': EMAIL, 'password': PW})
if s not in (200, 201):
    print('FAIL login ->', s, str(b)[:200])
    sys.exit(1)
tok = b['access_token']

today = datetime.date.today()
monday = today - datetime.timedelta(days=today.weekday())
weeks = [
    (14, dict(fruit_days=2, veg_days=3, protein_days=4, oily_days=4, sugary_days=4, skipped_days=2, water='low', exercise_days=1, sleep_quality=2, stress=4, energy=2)),
    (7, dict(fruit_days=3, veg_days=4, protein_days=5, oily_days=3, sugary_days=3, skipped_days=1, water='ok', exercise_days=2, sleep_quality=3, stress=3, energy=3)),
]
for off, resp in weeks:
    ws = monday - datetime.timedelta(days=off)
    we = ws + datetime.timedelta(days=6)
    s, r = call('POST', '/knowledge/surveys/weekly', {
        'week_start': ws.isoformat(), 'week_end': we.isoformat(), 'survey_version': 'v1',
        'responses': resp, 'completion_time_seconds': 90, 'is_complete': True, 'skipped_sections': [],
    }, tok)
    print(ws.isoformat(), '->', s, '' if s in (200, 201) else str(r)[:200])
