import json, random, sys, datetime, urllib.request, urllib.error

BASE = 'http://127.0.0.1:8000/api/v1'
EMAIL = sys.argv[1] if len(sys.argv) > 1 else 'demo@knowthyself.app'
PW = sys.argv[2] if len(sys.argv) > 2 else 'Demo1234!xy'
random.seed(7)
NOW = datetime.datetime.now().astimezone()
TODAY = NOW.date()

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

def at(off, hhmm):
    d = TODAY - datetime.timedelta(days=off)
    h, m = map(int, hhmm.split(':'))
    return datetime.datetime(d.year, d.month, d.day, h, m, tzinfo=NOW.tzinfo)

s, b = call('POST', '/auth/register', {'email': EMAIL, 'password': PW, 'full_name': 'Demo User', 'timezone': 'UTC', 'locale': 'en', 'accept_terms': True, 'marketing_consent': False})
if s not in (200, 201):
    s, b = call('POST', '/auth/login', {'email': EMAIL, 'password': PW})
    if s not in (200, 201):
        print('FAIL could not register or log in ->', s, str(b)[:300])
        sys.exit(1)
tok = b['access_token']

rng = '?date_from=%s&date_to=%s&page=1&page_size=50' % ((TODAY - datetime.timedelta(days=13)).isoformat(), TODAY.isoformat())
s, b = call('GET', '/physical/sleep' + rng, token=tok)
if s == 200 and isinstance(b, dict) and len(b.get('items', [])) >= 5:
    print('This account already has demo data. Nothing added.')
    sys.exit(0)

counts, fails = {}, []
def post(name, path, body):
    s, r = call('POST', path, body, tok)
    if s in (200, 201):
        counts[name] = counts.get(name, 0) + 1
    else:
        fails.append((name, s, str(r)[:250]))

for off in range(14):
    caf = random.random() < 0.35
    bed_h = random.choice(['22:30', '23:00', '23:15', '23:45', '00:15'])
    wake = at(off, random.choice(['06:45', '07:00', '07:15', '07:30']))
    bed = at(off + 1, bed_h) if int(bed_h[:2]) >= 18 else at(off, bed_h)
    lat = random.choice([10, 15, 20]) + (10 if caf else 0)
    awake = random.choice([5, 10, 15]) + (25 if caf else 0)
    tib = int((wake - bed).total_seconds() // 60)
    total = tib - lat - awake
    q = 'excellent' if total >= 480 and not caf else 'good' if total >= 440 else 'fair' if total >= 390 else 'poor'
    post('sleep', '/physical/sleep', {
        'date': wake.date().isoformat(), 'source': 'manual', 'bedtime': bed.isoformat(),
        'sleep_start': (bed + datetime.timedelta(minutes=lat)).isoformat(), 'sleep_end': wake.isoformat(), 'wake_time': wake.isoformat(),
        'time_in_bed_minutes': tib, 'total_sleep_minutes': total, 'awake_minutes': awake, 'sleep_latency_minutes': lat,
        'quality_rating': q, 'screen_time_before_bed_minutes': random.choice([20, 35, 50, 70]),
        'caffeine_after_noon': caf, 'alcohol_before_bed': False, 'exercise_before_bed': False, 'tags': [], 'interruption_details': []})

plans = {0: 'running', 1: 'weight_training', 2: 'yoga', 4: 'walking', 5: 'running', 7: 'cycling', 8: 'weight_training', 9: 'walking', 11: 'running', 12: 'yoga'}
spec = {'running': (35, 'moderate', 330, 4800, 5.2), 'weight_training': (50, 'vigorous', 280, 0, 0), 'yoga': (35, 'light', 120, 0, 0),
        'walking': (40, 'light', 160, 4800, 3.4), 'cycling': (45, 'moderate', 360, 0, 14.0)}
for off, typ in plans.items():
    dur, inten, cal, steps, dist = spec[typ]
    st = at(off, '07:30')
    if st > NOW:
        continue
    body = {'date': st.date().isoformat(), 'activity_type': typ, 'start_time': st.isoformat(), 'end_time': (st + datetime.timedelta(minutes=dur)).isoformat(),
            'duration_minutes': dur, 'intensity': inten, 'calories_burned': cal, 'tags': [], 'muscle_groups': []}
    if steps: body['steps'] = steps
    if dist: body['distance_km'] = dist
    post('workouts', '/physical/activity', body)

meals = [('breakfast', '08:30', 'Oats with banana and milk', 420, 16, 68, 9, 8), ('lunch', '13:15', 'Dal, rice and paneer curry', 720, 28, 95, 22, 10),
         ('snack', '17:00', 'Roasted chana and tea', 220, 10, 28, 6, 7), ('dinner', '20:30', 'Chapati with chicken curry', 640, 38, 60, 24, 6)]
for off in range(7):
    for mt, t, name, cal, pr, ca, fa, fi in meals:
        ts = at(off, t)
        if ts > NOW:
            continue
        k = random.uniform(0.92, 1.08)
        post('meals', '/physical/nutrition', {'date': ts.date().isoformat(), 'meal_type': mt, 'timestamp': ts.isoformat(), 'food_name': name,
              'quantity': 1, 'unit': 'serving', 'calories': round(cal * k), 'protein_g': round(pr * k), 'carbs_g': round(ca * k), 'fat_g': round(fa * k), 'fiber_g': fi})

for off in range(7):
    for t, ml in (('08:00', 300), ('10:30', 500), ('12:30', 500), ('15:00', 250), ('17:30', 500), ('20:00', 300)):
        ts = at(off, t)
        if ts > NOW:
            continue
        post('water', '/physical/hydration', {'date': ts.date().isoformat(), 'timestamp': ts.isoformat(), 'amount_ml': ml, 'beverage_type': 'water'})

sess = [('github.com', 'development', True, (90, 150), '09:30'), ('docs.google.com', 'work', True, (40, 80), '11:30'),
        ('youtube.com', 'video', False, (30, 70), '14:00'), ('instagram.com', 'social_media', False, (20, 50), '16:30'),
        ('stackoverflow.com', 'development', True, (25, 50), '18:00')]
for off in range(10):
    for dom, cat, prod, (lo, hi), t in sess:
        st = at(off, t)
        if st > NOW:
            continue
        secs = random.randint(lo, hi) * 60
        post('screen time', '/digital/activities', {'url': 'https://' + dom, 'domain': dom, 'title': dom, 'category': cat, 'is_productive': prod,
              'start_time': st.isoformat(), 'end_time': (st + datetime.timedelta(seconds=secs)).isoformat(), 'duration_seconds': secs,
              'active_seconds': secs, 'idle_seconds': 0, 'source': 'manual'})

print('Added:', ', '.join('%s %d' % (k, v) for k, v in counts.items()))
if fails:
    print('FAILED %d requests. First few:' % len(fails))
    for f in fails[:5]:
        print('  ', f)
print('Login: %s / %s' % (EMAIL, PW))
