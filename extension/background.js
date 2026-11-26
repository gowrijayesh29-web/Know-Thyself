const MIN_SECONDS = 15;
const MERGE_GAP_MS = 120000;
const IGNORE_HOSTS = ['localhost', '127.0.0.1'];
const RULES = [
  ['github.com', 'development', true], ['gitlab.com', 'development', true], ['stackoverflow.com', 'development', true],
  ['developer.mozilla.org', 'development', true], ['vercel.com', 'development', true], ['render.com', 'development', true],
  ['claude.ai', 'work', true], ['chatgpt.com', 'work', true], ['docs.google.com', 'work', true], ['drive.google.com', 'work', true],
  ['notion.so', 'work', true], ['mail.google.com', 'work', true], ['outlook.office.com', 'work', true],
  ['youtube.com', 'video', null], ['netflix.com', 'video', false], ['primevideo.com', 'video', false], ['hotstar.com', 'video', false],
  ['instagram.com', 'social_media', false], ['facebook.com', 'social_media', false], ['x.com', 'social_media', false],
  ['twitter.com', 'social_media', false], ['tiktok.com', 'social_media', false], ['reddit.com', 'social_media', false],
  ['snapchat.com', 'social_media', false],
];

function setBadge(on) {
  try {
    chrome.action.setBadgeText({ text: on ? 'REC' : '' });
    if (on) chrome.action.setBadgeBackgroundColor({ color: '#16a34a' });
  } catch (e) {}
}
let chain = Promise.resolve();
function run(fn) { chain = chain.then(fn).catch((e) => console.warn('kt-tracker', e)); return chain; }
async function get(k) { const o = await chrome.storage.local.get(k); return o[k]; }
function set(o) { return chrome.storage.local.set(o); }

function domainOf(url) {
  try {
    const u = new URL(url);
    if (u.protocol !== 'http:' && u.protocol !== 'https:') return null;
    const host = u.hostname.replace(/^www\./, '');
    return IGNORE_HOSTS.includes(host) ? null : host;
  } catch (e) { return null; }
}

function classify(domain) {
  for (const [d, category, prod] of RULES) {
    if (domain === d || domain.endsWith('.' + d)) return { category, is_productive: prod };
  }
  return { category: 'unclassified', is_productive: null };
}

async function finalize(endMs) {
  const cur = await get('cur');
  if (!cur) return;
  await set({ cur: null });
  setBadge(false);
  const end = Math.max(cur.start, endMs);
  const secs = Math.round((end - cur.start) / 1000);
  if (secs < MIN_SECONDS) return;
  const queue = (await get('queue')) || [];
  const last = queue[queue.length - 1];
  if (last && last.domain === cur.domain && cur.start - last.end < MERGE_GAP_MS) {
    last.end = end;
    last.active += secs;
  } else {
    queue.push({ domain: cur.domain, url: cur.url, title: cur.title, start: cur.start, end, active: secs });
  }
  await set({ queue: queue.slice(-2000) });
}

async function doSync() {
  const cfg = await get('cfg');
  const now = Date.now();
  if (!cfg || !cfg.token) { await finalize(now); return; }
  const idle = await chrome.idle.queryState(60);
  let tab = null;
  if (idle === 'active') {
    const w = await chrome.windows.getLastFocused({ populate: true }).catch(() => null);
    if (w && w.focused) tab = (w.tabs || []).find((t) => t.active) || null;
  }
  if (tab && tab.incognito) tab = null;
  const dom = tab ? domainOf(tab.url) : null;
  const cur = await get('cur');
  if (cur && dom && cur.domain === dom) { setBadge(true); return; }
  if (cur) await finalize(now);
  if (dom) setBadge(true);
  if (dom) await set({ cur: { domain: dom, url: tab.url.slice(0, 500), title: tab.title || dom, start: now, last: now } });
}

async function post(cfg, body) {
  const res = await fetch(cfg.api + '/digital/activities', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', Authorization: 'Bearer ' + cfg.token },
    body: JSON.stringify(body),
  });
  return res.status;
}

async function sendOne(cfg, q) {
  const secs = Math.max(1, Math.round((q.end - q.start) / 1000));
  const active = Math.min(q.active, secs);
  const c = classify(q.domain);
  const body = {
    url: q.url, domain: q.domain, title: String(q.title || q.domain).slice(0, 200),
    category: c.category, is_productive: c.is_productive,
    start_time: new Date(q.start).toISOString(), end_time: new Date(q.end).toISOString(),
    duration_seconds: secs, active_seconds: active, idle_seconds: secs - active, source: 'extension',
  };
  const tries = [body, { ...body, source: 'manual' }, { ...body, source: 'manual', category: 'unclassified' }];
  let st = 0;
  for (const b of tries) {
    st = await post(cfg, b);
    if (st !== 422) break;
  }
  return st;
}

async function doFlush(all) {
  const cfg = await get('cfg');
  if (!cfg || !cfg.token) return { sent: 0, error: 'Not signed in' };
  const queue = (await get('queue')) || [];
  const cutoff = Date.now() - MERGE_GAP_MS;
  const keep = [];
  let sent = 0, error = '', stop = false;
  for (const q of queue) {
    if (stop || (!all && q.end > cutoff)) { keep.push(q); continue; }
    let st = 0;
    try { st = await sendOne(cfg, q); }
    catch (e) { stop = true; error = 'Cannot reach the server'; keep.push(q); continue; }
    if (st === 200 || st === 201) sent++;
    else if (st === 401) { stop = true; error = 'Session expired: sign in again'; keep.push(q); }
    else if (st >= 500 || st === 429) { stop = true; error = 'Server error (HTTP ' + st + ')'; keep.push(q); }
    else { error = 'Some records were rejected (HTTP ' + st + ')'; }
  }
  const patch = { queue: keep, status: error };
  if (sent) patch.lastSent = Date.now();
  await set(patch);
  return { sent, error };
}

chrome.idle.setDetectionInterval(60);
chrome.alarms.get('tick', (a) => { if (!a) chrome.alarms.create('tick', { periodInMinutes: 1 }); });

chrome.runtime.onInstalled.addListener(() => run(doSync));
chrome.runtime.onStartup.addListener(() => run(async () => {
  const cur = await get('cur');
  if (cur) await finalize(cur.last || cur.start);
  await doSync();
}));
chrome.tabs.onActivated.addListener(() => run(doSync));
chrome.tabs.onUpdated.addListener((id, info) => { if (info.url || info.status === 'complete') run(doSync); });
chrome.windows.onFocusChanged.addListener(() => run(doSync));
chrome.idle.onStateChanged.addListener((state) => run(async () => {
  if (state !== 'active') await finalize(Date.now() - 60000);
  else await doSync();
}));
chrome.alarms.onAlarm.addListener((a) => {
  if (a.name !== 'tick') return;
  run(async () => {
    await doSync();
    const cur = await get('cur');
    if (cur) await set({ cur: { ...cur, last: Date.now() } });
    await doFlush(false);
  });
});
chrome.runtime.onMessage.addListener((msg, _sender, reply) => {
  if (!msg) return;
  if (msg.type === 'flush') {
    run(async () => {
      try {
        if (await get('cur')) await finalize(Date.now());
        await doSync();
        reply(await doFlush(true));
      } catch (e) { reply({ sent: 0, error: String(e) }); }
    });
    return true;
  }
  if (msg.type === 'sync') {
    run(async () => { try { await doSync(); } catch (e) {} reply({ ok: true }); });
    return true;
  }
});
