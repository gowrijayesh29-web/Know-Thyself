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
def show(label, status, ok_codes, body, fatal=True):
    global all_ok
    ok = status in ok_codes
    print(('PASS ' if ok else ('FAIL ' if fatal else 'INFO ')) + label + ' -> ' + str(status))
    if not ok:
        if fatal:
            all_ok = False
        text = body if isinstance(body, str) else json.dumps(body)
        print('     ' + text[:600])
    return ok

rnd = ''.join(random.choices(string.ascii_lowercase, k=6))
email, pw = 'smoke_%s@example.com' % rnd, 'Smoke1234!xy'
now = datetime.datetime.now(datetime.timezone.utc)
today = datetime.date.today().isoformat()

s, b = call('POST', '/auth/register', {'email': email, 'password': pw, 'full_name': 'Smoke Test', 'timezone': 'UTC', 'locale': 'en', 'accept_terms': True, 'marketing_consent': False})
if not show('register', s, (200, 201), b):
    sys.exit(1)
tok = b['access_token']

act = {'date': today, 'activity_type': 'running', 'start_time': now.isoformat(),
       'end_time': (now + datetime.timedelta(minutes=30)).isoformat(), 'duration_minutes': 30,
       'intensity': 'moderate', 'calories_burned': 300, 'steps': 4000, 'distance_km': 4.5, 'tags': [], 'muscle_groups': []}
s, b = call('POST', '/physical/activity', act, tok)
aid = b.get('id') if show('create workout', s, (201,), b) and isinstance(b, dict) else None

meal = {'date': today, 'meal_type': 'lunch', 'timestamp': now.isoformat(), 'food_name': 'Smoke test meal',
        'quantity': 1, 'unit': 'serving', 'calories': 500, 'protein_g': 30, 'carbs_g': 50, 'fat_g': 15, 'fiber_g': 5}
s, b = call('POST', '/physical/nutrition', meal, tok)
nid = b.get('id') if show('create meal', s, (201,), b) and isinstance(b, dict) else None

water = {'date': today, 'timestamp': now.isoformat(), 'amount_ml': 250, 'beverage_type': 'water'}
s, b = call('POST', '/physical/hydration', water, tok)
hid = b.get('id') if show('create water', s, (201,), b) and isinstance(b, dict) else None

q = '?date_from=%s&date_to=%s&page=1&page_size=50' % (today, today)
for name, path in (('workouts', '/physical/activity'), ('meals', '/physical/nutrition'), ('water', '/physical/hydration')):
    s, b = call('GET', path + q, token=tok)
    if show('list ' + name, s, (200,), b) and isinstance(b, dict):
        print('     items returned:', len(b.get('items', [])))

s, b = call('GET', '/physical/activity?page=1&page_size=100', token=tok)
show('list with page_size=100 (info only)', s, (200,), b, fatal=False)

for label, path, rid in (('delete workout', '/physical/activity/', aid), ('delete meal', '/physical/nutrition/', nid), ('delete water', '/physical/hydration/', hid)):
    if rid:
        s, b = call('DELETE', path + rid, token=tok)
        show(label, s, (204,), b)

print('\nALL BACKEND CHECKS PASSED' if all_ok else '\nSOME CHECKS FAILED - paste this output to Claude')
