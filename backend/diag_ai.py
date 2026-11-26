import httpx
from app.core.config import settings as s
print('base url :', s.NVIDIA_BASE_URL)
print('model    :', s.NVIDIA_MODEL)
print('key set  :', bool(s.NVIDIA_API_KEY), '| key length:', len(s.NVIDIA_API_KEY or ''))
r = httpx.get(s.NVIDIA_BASE_URL.rstrip('/') + '/models', headers={'Authorization': 'Bearer ' + (s.NVIDIA_API_KEY or '')}, timeout=60)
print('GET /models ->', r.status_code)
if r.status_code == 200:
    ids = sorted(m['id'] for m in r.json().get('data', []))
    print('total models:', len(ids))
    print('model name exists:', s.NVIDIA_MODEL in ids)
    print('--- nemotron / llama-3.x models ---')
    for i in ids:
        if 'nemotron' in i.lower() or 'llama-3' in i.lower():
            print(i)
else:
    print(r.text[:300])
