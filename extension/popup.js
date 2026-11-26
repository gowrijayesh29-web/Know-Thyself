const $ = (id) => document.getElementById(id);
const DEFAULT_API = 'http://127.0.0.1:8000/api/v1';

async function render() {
  const o = await chrome.storage.local.get(['cfg', 'cur', 'queue', 'status', 'lastSent']);
  const cfg = o.cfg;
  const signedIn = !!(cfg && cfg.token);
  $('login').style.display = signedIn ? 'none' : 'block';
  $('main').style.display = signedIn ? 'block' : 'none';
  if (!$('api').value) $('api').value = (cfg && cfg.api) || DEFAULT_API;
  if (signedIn) {
    $('who').textContent = cfg.email;
    $('now').textContent = o.cur ? 'Tracking now: ' + o.cur.domain : 'Not tracking right now (idle, another app, or an excluded page).';
    $('queue').textContent = (o.queue || []).length + ' session(s) waiting to upload' + (o.lastSent ? '. Last upload ' + new Date(o.lastSent).toLocaleTimeString() : '.');
  }
  if (o.status) $('err').textContent = o.status;
}

$('go').onclick = async () => {
  $('err').textContent = '';
  const api = $('api').value.trim().replace(/\/+$/, '');
  const email = $('email').value.trim();
  try {
    const res = await fetch(api + '/auth/login', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ email, password: $('pw').value }) });
    const data = await res.json().catch(() => ({}));
    if (!res.ok || !data.access_token) { $('err').textContent = 'Sign in failed (' + res.status + '): ' + JSON.stringify(data).slice(0, 200); return; }
    await chrome.storage.local.set({ cfg: { api, token: data.access_token, email }, status: '' });
    await chrome.runtime.sendMessage({ type: 'sync' });
    render();
  } catch (e) {
    $('err').textContent = 'Cannot reach ' + api + '. Is the backend running?';
  }
};

$('send').onclick = async () => {
  $('send').disabled = true;
  $('err').textContent = '';
  const r = await chrome.runtime.sendMessage({ type: 'flush' }).catch(() => null);
  $('send').disabled = false;
  await render();
  if (r && !r.error) $('err').textContent = 'Uploaded ' + r.sent + ' session(s).';
  else if (r && r.error) $('err').textContent = r.error;
};

$('out').onclick = async () => {
  await chrome.runtime.sendMessage({ type: 'flush' }).catch(() => null);
  await chrome.storage.local.remove(['cfg', 'cur']);
  await chrome.runtime.sendMessage({ type: 'sync' }).catch(() => null);
  render();
};

render();
setInterval(render, 2000);