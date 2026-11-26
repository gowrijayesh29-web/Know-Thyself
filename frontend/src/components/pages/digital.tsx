'use client';

import { useMemo, useState, FormEvent } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import toast from 'react-hot-toast';
import { MousePointerClick, Globe, Clock, Target, CheckCircle, AlertTriangle, Plus, Trash2, Loader2, BarChart3, Sparkles } from 'lucide-react';
import { cn } from '@/lib/utils';
import { errorMessage } from '@/lib/api';
import { Modal, inputClass, selectClass, labelClass } from '@/components/modal';
import type { DigitalRecord } from '@/lib/digital-api';
import { listDigital, createDigital, deleteDigital, analyzeDigital } from '@/lib/digital-api';
import { dayStr, nowTime, toDate } from '@/lib/health-api';

const CATEGORIES = [
  { id: 'work', label: 'Work' },
  { id: 'study', label: 'Study' },
  { id: 'learning', label: 'Learning' },
  { id: 'research', label: 'Research' },
  { id: 'development', label: 'Development' },
  { id: 'design', label: 'Design' },
  { id: 'writing', label: 'Writing' },
  { id: 'reading', label: 'Reading' },
  { id: 'productivity', label: 'Productivity' },
  { id: 'communication', label: 'Communication' },
  { id: 'news', label: 'News' },
  { id: 'shopping', label: 'Shopping' },
  { id: 'video', label: 'Video' },
  { id: 'music', label: 'Music' },
  { id: 'entertainment', label: 'Entertainment' },
  { id: 'social_media', label: 'Social media' },
  { id: 'gaming', label: 'Gaming' },
  { id: 'distraction', label: 'Distraction' },
  { id: 'unclassified', label: 'Other' },
];
const CAT_LABEL: Record<string, string> = Object.fromEntries(CATEGORIES.map((c) => [c.id, c.label]));
const PRODUCTIVE = new Set(['work', 'study', 'learning', 'research', 'development', 'design', 'writing', 'reading', 'productivity']);
const UNPRODUCTIVE = new Set(['entertainment', 'social_media', 'gaming', 'video', 'distraction']);

const DAILY_LIMIT_MIN = 360;

function localDay(iso: string): string {
  const d = new Date(iso);
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
}
function fmt(sec: number): string {
  const m = Math.round(sec / 60);
  if (m < 60) return `${m}m`;
  return `${Math.floor(m / 60)}h ${m % 60}m`;
}
function dayLabel(d: string): string {
  return new Date(`${d}T00:00:00`).toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' });
}
function prodBadge(p: boolean | null | undefined) {
  if (p === true) return { text: 'Productive', cls: 'bg-green-500/15 text-green-500' };
  if (p === false) return { text: 'Unproductive', cls: 'bg-red-500/15 text-red-500' };
  return { text: 'Neutral', cls: 'bg-slate-500/15 text-slate-400' };
}

function MetricCard({ title, value, subtitle, progress, icon: Icon, color }: any) {
  return (
    <div className="card-hover">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm font-medium text-foreground/60 mb-1">{title}</p>
          <p className="text-2xl font-bold text-foreground">{value}</p>
          {subtitle && <p className="text-sm text-muted-foreground mt-1">{subtitle}</p>}
        </div>
        <div className={cn('p-3 rounded-2xl', color)}><Icon className="w-6 h-6" /></div>
      </div>
      {progress !== undefined && (
        <div className="mt-4 h-2 bg-muted-foreground/10 rounded-full overflow-hidden">
          <div className="h-full rounded-full bg-primary-500 transition-all duration-700" style={{ width: `${Math.min(100, Math.max(0, progress))}%` }} />
        </div>
      )}
    </div>
  );
}

function Bars({ rows }: { rows: { label: string; seconds: number }[] }) {
  const max = Math.max(1, ...rows.map((r) => r.seconds));
  if (rows.length === 0) return <p className="text-sm text-muted-foreground">Nothing logged yet.</p>;
  return (
    <div className="space-y-3">
      {rows.map((r) => (
        <div key={r.label}>
          <div className="flex justify-between text-sm mb-1">
            <span className="text-foreground">{r.label}</span>
            <span className="text-muted-foreground">{fmt(r.seconds)}</span>
          </div>
          <div className="h-2 bg-muted-foreground/10 rounded-full overflow-hidden">
            <div className="h-full rounded-full bg-primary-500 transition-all duration-700" style={{ width: `${(r.seconds / max) * 100}%` }} />
          </div>
        </div>
      ))}
    </div>
  );
}

function group(items: DigitalRecord[], key: (r: DigitalRecord) => string) {
  const m: Record<string, number> = {};
  items.forEach((r) => { const k = key(r); m[k] = (m[k] || 0) + r.active_seconds; });
  return Object.entries(m).map(([label, seconds]) => ({ label, seconds })).sort((a, b) => b.seconds - a.seconds);
}

export function DigitalPage() {
  const qc = useQueryClient();
  const today = dayStr(0);
  const [tab, setTab] = useState<'today' | 'week'>('today');
  const [showLog, setShowLog] = useState(false);

  const { data = [], isLoading, isError, error, refetch } = useQuery({
    queryKey: ['digital', today],
    queryFn: () => listDigital(toDate(dayStr(-6), '00:00').toISOString(), toDate(dayStr(0), '23:59').toISOString()),
  });

  const [aiResult, setAiResult] = useState<any>(null);
  const aiMut = useMutation({
    mutationFn: analyzeDigital,
    onSuccess: (r) => { setAiResult(r); qc.invalidateQueries({ queryKey: ['digital'] }); toast.success('AI analysis ready'); },
    onError: (e) => toast.error(errorMessage(e)),
  });
  const delMut = useMutation({
    mutationFn: (id: string) => deleteDigital(id),
    onSuccess: () => { toast.success('Entry deleted'); qc.invalidateQueries({ queryKey: ['digital'] }); },
    onError: (e) => toast.error(errorMessage(e)),
  });

  const v = useMemo(() => {
    const t = data.filter((r) => localDay(r.start_time) === today);
    const sum = (a: DigitalRecord[]) => a.reduce((s, r) => s + r.active_seconds, 0);
    const prod = t.filter((r) => r.is_productive === true).reduce((s, r) => s + r.active_seconds, 0);
    const unprod = t.filter((r) => r.is_productive === false).reduce((s, r) => s + r.active_seconds, 0);
    const days = Array.from({ length: 7 }, (_, i) => dayStr(-i)).map((d) => ({
      d, seconds: sum(data.filter((r) => localDay(r.start_time) === d)),
    }));
    return {
      t, total: sum(t), prod, unprod,
      prodPct: prod + unprod > 0 ? Math.round((prod / (prod + unprod)) * 100) : 0,
      cats: group(t, (r) => CAT_LABEL[r.category] || r.category),
      sites: group(t, (r) => r.domain).slice(0, 6),
      wCats: group(data, (r) => CAT_LABEL[r.category] || r.category),
      wSites: group(data, (r) => r.domain).slice(0, 8),
      days,
      weekTotal: sum(data),
    };
  }, [data, today]);

  const row = (r: DigitalRecord) => {
    const b = prodBadge(r.is_productive);
    const time = new Date(r.start_time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    return (
      <div key={r.id} className="flex items-center justify-between gap-3 p-4 glass-subtle rounded-xl">
        <div className="flex items-center gap-4 min-w-0">
          <div className="p-3 rounded-xl bg-primary-500/15 text-primary-500"><Globe className="w-5 h-5" /></div>
          <div className="min-w-0">
            <p className="font-medium text-foreground truncate">{r.domain}</p>
            <p className="text-sm text-muted-foreground">{CAT_LABEL[r.category] || r.category} Â· {dayLabel(localDay(r.start_time))} {time}</p>
          </div>
        </div>
        <div className="flex items-center gap-4">
          <span className={cn('hidden sm:inline px-2 py-1 rounded-lg text-xs font-medium', b.cls)}>{b.text}</span>
          <div className="text-right">
            <p className="font-semibold text-foreground">{fmt(r.active_seconds)}</p>
            <p className="text-xs text-muted-foreground">Active</p>
          </div>
          <button title="Delete" disabled={delMut.isPending} onClick={() => { if (window.confirm(`Delete ${r.domain}?`)) delMut.mutate(r.id); }}
            className="p-2 rounded-xl glass-subtle hover:bg-red-500/10 transition-colors">
            <Trash2 className="w-4 h-4 text-red-500" />
          </button>
        </div>
      </div>
    );
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="heading-1">Digital Wellbeing</h1>
          <p className="body-md text-muted-foreground mt-1">Log your screen time by site or app and see where your attention goes.</p>
        </div>
        <button className="btn-primary" onClick={() => setShowLog(true)}><Plus className="w-4 h-4 mr-2" /> Log Activity</button>
      </div>

      {isLoading ? (
        <div className="flex items-center justify-center py-16 text-muted-foreground"><Loader2 className="w-6 h-6 animate-spin mr-3" /> Loading your activity...</div>
      ) : isError ? (
        <div className="rounded-2xl border border-red-500/30 bg-red-500/10 p-6 text-center">
          <p className="text-red-500 font-medium mb-1">Could not load activity</p>
          <p className="text-sm text-muted-foreground mb-4">{errorMessage(error)}</p>
          <button className="btn-primary btn-sm" onClick={() => refetch()}>Try again</button>
        </div>
      ) : (
        <>
          <div className="card p-6">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
              <div>
                <h2 className="heading-6 flex items-center gap-2"><Sparkles className="w-5 h-5 text-primary-500" /> AI insights</h2>
                <p className="text-sm text-muted-foreground mt-1">Sorts unknown sites and apps into categories, then finds patterns in your last 7 days (this laptop only).</p>
              </div>
              <button className="btn-primary" disabled={aiMut.isPending} onClick={() => aiMut.mutate()}>
                {aiMut.isPending ? 'Analysing...' : aiResult ? 'Re-run analysis' : 'Analyse with AI'}
              </button>
            </div>
            {aiResult && aiResult.insight && (
              <div className="mt-5 space-y-4">
                <p className="text-foreground">{aiResult.insight.summary}</p>
                {aiResult.insight.patterns.length > 0 && (
                  <ul className="list-disc pl-5 space-y-1 text-sm text-foreground">
                    {aiResult.insight.patterns.map((p: string, i: number) => <li key={i}>{p}</li>)}
                  </ul>
                )}
                {aiResult.insight.action && (
                  <div className="glass-subtle rounded-xl p-4 text-sm"><span className="font-semibold text-primary-500">Action for tomorrow: </span>{aiResult.insight.action}</div>
                )}
                <p className="text-xs text-muted-foreground">
                  {aiResult.classified.length > 0 ? `AI classified ${aiResult.classified.length} site/app(s): ${aiResult.classified.map((c: any) => `${c.domain} -> ${c.category}`).join(', ')}. ` : ''}
                  {aiResult.remaining > 0 ? `${aiResult.remaining} could not be classified confidently. ` : ''}
                  Written by AI from your tracked activity; categories are estimates.
                </p>
              </div>
            )}
            {aiResult && !aiResult.insight && <p className="mt-4 text-sm text-muted-foreground">{aiResult.message || 'No activity in the last 7 days.'}</p>}
          </div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <MetricCard title="Screen time today" value={fmt(v.total)} subtitle={`Soft limit: ${DAILY_LIMIT_MIN / 60}h (default)`} progress={(v.total / 60 / DAILY_LIMIT_MIN) * 100} icon={Clock} color="bg-primary-500/15 text-primary-500" />
            <MetricCard title="Productive share" value={`${v.prodPct}%`} subtitle="Productive vs unproductive" progress={v.prodPct} icon={Target} color="bg-green-500/15 text-green-500" />
            <MetricCard title="Productive time" value={fmt(v.prod)} subtitle="Today" icon={CheckCircle} color="bg-accent-500/15 text-accent-500" />
            <MetricCard title="Sessions" value={v.t.length} subtitle={v.unprod ? `${fmt(v.unprod)} unproductive` : 'Today'} icon={v.unprod > v.prod ? AlertTriangle : MousePointerClick} color="bg-secondary-500/15 text-secondary-500" />
          </div>

          <div className="card overflow-hidden">
            <div className="border-b border-white/10">
              <nav className="flex px-4">
                {[{ id: 'today', label: 'Today', icon: Clock }, { id: 'week', label: 'This Week', icon: BarChart3 }].map((tb) => (
                  <button key={tb.id} onClick={() => setTab(tb.id as any)}
                    className={cn('flex items-center gap-2 px-4 py-3 text-sm font-medium border-b-2 transition-colors hover:bg-white/5',
                      tab === tb.id ? 'text-primary-500 border-primary-500' : 'text-muted-foreground border-transparent')}>
                    <tb.icon className="w-4 h-4" /> {tb.label}
                  </button>
                ))}
              </nav>
            </div>
            <div className="p-6">
              {tab === 'today' ? (
                <div className="space-y-6">
                  <div className="grid md:grid-cols-2 gap-6">
                    <div><h2 className="heading-6 mb-4">By category</h2><Bars rows={v.cats} /></div>
                    <div><h2 className="heading-6 mb-4">Top sites</h2><Bars rows={v.sites} /></div>
                  </div>
                  <div>
                    <h2 className="heading-6 mb-4">Today's entries</h2>
                    {v.t.length === 0 ? (
                      <div className="glass-subtle p-8 rounded-2xl text-center">
                        <Globe className="w-12 h-12 mx-auto text-muted-foreground/50 mb-4" />
                        <p className="text-foreground mb-4">Nothing logged yet today</p>
                        <button className="btn-primary" onClick={() => setShowLog(true)}><Plus className="w-4 h-4 mr-2" /> Log Activity</button>
                      </div>
                    ) : <div className="space-y-3">{v.t.map(row)}</div>}
                  </div>
                </div>
              ) : (
                <div className="space-y-6">
                  <p className="text-sm text-muted-foreground">Last 7 days: <span className="text-foreground font-semibold">{fmt(v.weekTotal)}</span> total</p>
                  <div><h2 className="heading-6 mb-4">Per day</h2><Bars rows={v.days.map((x) => ({ label: dayLabel(x.d) + (x.d === today ? ' (today)' : ''), seconds: x.seconds }))} /></div>
                  <div className="grid md:grid-cols-2 gap-6">
                    <div><h2 className="heading-6 mb-4">By category</h2><Bars rows={v.wCats} /></div>
                    <div><h2 className="heading-6 mb-4">Top sites</h2><Bars rows={v.wSites} /></div>
                  </div>
                  {data.length > 0 && (
                    <div><h2 className="heading-6 mb-4">All entries</h2><div className="space-y-3">{data.map(row)}</div></div>
                  )}
                </div>
              )}
            </div>
          </div>
        </>
      )}

      {showLog && <LogActivityModal onClose={() => setShowLog(false)} />}
    </div>
  );
}

function LogActivityModal({ onClose }: { onClose: () => void }) {
  const qc = useQueryClient();
  const [site, setSite] = useState('');
  const [category, setCategory] = useState('work');
  const [minutes, setMinutes] = useState('');
  const [prod, setProd] = useState('auto');
  const [date, setDate] = useState(dayStr(0));
  const [time, setTime] = useState(nowTime());
  const [error, setError] = useState('');

  const mut = useMutation({
    mutationFn: createDigital,
    onSuccess: () => { toast.success('Activity logged'); qc.invalidateQueries({ queryKey: ['digital'] }); onClose(); },
    onError: (e) => setError(errorMessage(e, 'Could not log activity')),
  });

  function onSubmit(e: FormEvent) {
    e.preventDefault();
    setError('');
    const domain = site.trim().toLowerCase().replace(/^https?:\/\//, '').split('/')[0];
    if (!domain) return setError('Enter a site or app, like youtube.com or VS Code.');
    const safeDomain = domain.replace(/\s+/g, '-');
    const mins = Math.round(Number(minutes));
    if (!minutes.trim() || !Number.isFinite(mins) || mins < 1) return setError('Duration must be at least 1 minute.');
    const start = toDate(date, time);
    if (!date || !time || Number.isNaN(start.getTime())) return setError('Please choose a valid date and time.');
    const secs = mins * 60;
    let isProd: boolean | null = null;
    if (prod === 'yes') isProd = true;
    else if (prod === 'no') isProd = false;
    else if (prod === 'auto') isProd = PRODUCTIVE.has(category) ? true : UNPRODUCTIVE.has(category) ? false : null;
    mut.mutate({
      url: `https://${safeDomain}`,
      domain: safeDomain,
      title: domain,
      category,
      is_productive: isProd,
      start_time: start.toISOString(),
      end_time: new Date(start.getTime() + secs * 1000).toISOString(),
      duration_seconds: secs,
      active_seconds: secs,
      idle_seconds: 0,
      source: 'manual',
    });
  }

  return (
    <Modal title="Log activity" onClose={onClose}>
      <form onSubmit={onSubmit} className="space-y-4">
        <div>
          <label className={labelClass} htmlFor="d-site">Site or app</label>
          <input id="d-site" className={inputClass} value={site} onChange={(e) => setSite(e.target.value)} placeholder="e.g. youtube.com" autoFocus />
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className={labelClass} htmlFor="d-cat">Category</label>
            <select id="d-cat" className={selectClass} value={category} onChange={(e) => setCategory(e.target.value)}>
              {CATEGORIES.map((c) => <option key={c.id} value={c.id}>{c.label}</option>)}
            </select>
          </div>
          <div>
            <label className={labelClass} htmlFor="d-prod">Productivity</label>
            <select id="d-prod" className={selectClass} value={prod} onChange={(e) => setProd(e.target.value)}>
              <option value="auto">Auto (from category)</option>
              <option value="yes">Productive</option>
              <option value="no">Unproductive</option>
              <option value="neutral">Neutral</option>
            </select>
          </div>
        </div>
        <div className="grid grid-cols-3 gap-4">
          <div>
            <label className={labelClass} htmlFor="d-min">Minutes</label>
            <input id="d-min" type="number" min="1" step="1" className={inputClass} value={minutes} onChange={(e) => setMinutes(e.target.value)} placeholder="30" />
          </div>
          <div>
            <label className={labelClass} htmlFor="d-date">Date</label>
            <input id="d-date" type="date" className={inputClass} value={date} onChange={(e) => setDate(e.target.value)} />
          </div>
          <div>
            <label className={labelClass} htmlFor="d-time">Start</label>
            <input id="d-time" type="time" className={inputClass} value={time} onChange={(e) => setTime(e.target.value)} />
          </div>
        </div>
        {error && <div className="rounded-xl bg-red-500/10 border border-red-500/30 text-red-500 text-sm px-4 py-3" role="alert">{error}</div>}
        <div className="flex justify-end gap-3 pt-2">
          <button type="button" className="btn-ghost" onClick={onClose}>Cancel</button>
          <button type="submit" className="btn-primary" disabled={mut.isPending}>{mut.isPending ? 'Saving...' : 'Save activity'}</button>
        </div>
      </form>
    </Modal>
  );
}
