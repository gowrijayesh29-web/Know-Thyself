'use client';

import { useMemo, useState, FormEvent } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import toast from 'react-hot-toast';
import { Moon, Bed, Battery, Heart, Plus, Trash2, Loader2, TrendingUp, Brain, Coffee, Wine, Dumbbell, Smartphone } from 'lucide-react';
import { cn } from '@/lib/utils';
import { errorMessage } from '@/lib/api';
import { Modal, inputClass, selectClass, labelClass } from '@/components/modal';
import type { SleepRecord } from '@/lib/sleep-api';
import { listSleep, createSleep, deleteSleep } from '@/lib/sleep-api';
import { dayStr, toDate } from '@/lib/health-api';

const QUALITY = [
  { id: 'very_poor', label: 'Very poor' },
  { id: 'poor', label: 'Poor' },
  { id: 'fair', label: 'Fair' },
  { id: 'good', label: 'Good' },
  { id: 'excellent', label: 'Excellent' },
];
const Q_LABEL: Record<string, string> = Object.fromEntries(QUALITY.map((q) => [q.id, q.label]));
const Q_STYLE: Record<string, string> = {
  very_poor: 'bg-red-500/15 text-red-500',
  poor: 'bg-orange-500/15 text-orange-500',
  fair: 'bg-yellow-500/15 text-yellow-500',
  good: 'bg-blue-500/15 text-blue-500',
  excellent: 'bg-green-500/15 text-green-500',
};
const TARGET_MIN = 480;

function hm(m: number): string {
  const r = Math.round(m);
  return `${Math.floor(r / 60)}h ${r % 60}m`;
}
function clock(iso: string): string {
  return new Date(iso).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}
function dayLabel(d: string): string {
  return new Date(`${d}T00:00:00`).toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' });
}
function eff(r: SleepRecord): number {
  return r.time_in_bed_minutes > 0 ? Math.round((r.total_sleep_minutes / r.time_in_bed_minutes) * 100) : 0;
}
function bedOffset(r: SleepRecord): number {
  const d = new Date(r.bedtime);
  return (d.getHours() * 60 + d.getMinutes() - 18 * 60 + 1440) % 1440;
}
function avg(a: number[]): number {
  return a.length ? a.reduce((s, x) => s + x, 0) / a.length : 0;
}

function MetricCard({ title, value, subtitle, icon: Icon, color }: any) {
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
    </div>
  );
}

export function SleepPage() {
  const qc = useQueryClient();
  const [tab, setTab] = useState<'overview' | 'trends' | 'factors'>('overview');
  const [showLog, setShowLog] = useState(false);

  const { data = [], isLoading, isError, error, refetch } = useQuery({
    queryKey: ['sleep'],
    queryFn: () => listSleep(dayStr(-29), dayStr(0)),
  });

  const delMut = useMutation({
    mutationFn: (id: string) => deleteSleep(id),
    onSuccess: () => { toast.success('Sleep entry deleted'); qc.invalidateQueries({ queryKey: ['sleep'] }); },
    onError: (e) => toast.error(errorMessage(e)),
  });

  const v = useMemo(() => {
    const last = data[0];
    const week = data.filter((r) => r.date >= dayStr(-6));
    const offs = week.map(bedOffset);
    const mean = avg(offs);
    const sd = offs.length >= 3 ? Math.round(Math.sqrt(avg(offs.map((o) => (o - mean) ** 2)))) : null;
    const bm = (18 * 60 + Math.round(mean)) % 1440;
    const compare = (key: 'caffeine_after_noon' | 'alcohol_before_bed' | 'exercise_before_bed') => {
      const w = data.filter((r) => r[key]);
      const wo = data.filter((r) => !r[key]);
      return { n: w.length, nNo: wo.length, withAvg: avg(w.map((r) => r.total_sleep_minutes)), withoutAvg: avg(wo.map((r) => r.total_sleep_minutes)) };
    };
    const screen = data.filter((r) => r.screen_time_before_bed_minutes != null).map((r) => r.screen_time_before_bed_minutes as number);
    return {
      last, week,
      avgSleep: avg(week.map((r) => r.total_sleep_minutes)),
      avgEff: Math.round(avg(week.map(eff))),
      debt: week.reduce((s, r) => s + Math.max(0, TARGET_MIN - r.total_sleep_minutes), 0),
      sd,
      avgBed: offs.length ? `${String(Math.floor(bm / 60)).padStart(2, '0')}:${String(bm % 60).padStart(2, '0')}` : '--',
      caffeine: compare('caffeine_after_noon'),
      alcohol: compare('alcohol_before_bed'),
      exercise: compare('exercise_before_bed'),
      avgScreen: Math.round(avg(screen)),
      screenN: screen.length,
    };
  }, [data]);

  const night = (r: SleepRecord) => (
    <div key={r.id} className="flex items-center justify-between gap-3 p-4 glass-subtle rounded-xl">
      <div className="flex items-center gap-4 min-w-0">
        <div className={cn('p-3 rounded-xl', Q_STYLE[r.quality_rating || ''] || 'bg-slate-500/15 text-slate-400')}><Moon className="w-5 h-5" /></div>
        <div className="min-w-0">
          <p className="font-medium text-foreground">{dayLabel(r.date)}</p>
          <p className="text-sm text-muted-foreground">{clock(r.bedtime)} to {clock(r.wake_time)}{r.quality_rating ? ` · ${Q_LABEL[r.quality_rating] || r.quality_rating}` : ''}</p>
        </div>
      </div>
      <div className="flex items-center gap-5 text-right">
        <div><p className="font-semibold text-foreground">{hm(r.total_sleep_minutes)}</p><p className="text-xs text-muted-foreground">Asleep</p></div>
        <div className="hidden sm:block"><p className="font-semibold text-foreground">{eff(r)}%</p><p className="text-xs text-muted-foreground">Efficiency</p></div>
        <button title="Delete" disabled={delMut.isPending} onClick={() => { if (window.confirm('Delete this sleep entry?')) delMut.mutate(r.id); }}
          className="p-2 rounded-xl glass-subtle hover:bg-red-500/10 transition-colors"><Trash2 className="w-4 h-4 text-red-500" /></button>
      </div>
    </div>
  );

  const factorRow = (label: string, icon: any, c: { n: number; nNo: number; withAvg: number; withoutAvg: number }) => {
    const Icon = icon;
    const ok = c.n > 0 && c.nNo > 0;
    return (
      <div key={label} className="flex items-start gap-4 p-4 glass-subtle rounded-xl">
        <div className="p-3 rounded-xl bg-primary-500/15 text-primary-500"><Icon className="w-5 h-5" /></div>
        <div>
          <p className="font-medium text-foreground">{label}: {c.n} of {c.n + c.nNo} nights</p>
          <p className="text-sm text-muted-foreground">
            {ok ? `Average sleep ${hm(c.withAvg)} with it vs ${hm(c.withoutAvg)} without. Based on your own logs, so treat it as a hint, not proof.` : 'Log nights both with and without this to see a comparison.'}
          </p>
        </div>
      </div>
    );
  };

  const last = v.last;
  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="heading-1">Sleep & Recovery</h1>
          <p className="body-md text-muted-foreground mt-1">Log your nights and see what is helping or hurting your sleep.</p>
        </div>
        <button className="btn-primary" onClick={() => setShowLog(true)}><Plus className="w-4 h-4 mr-2" /> Log Sleep</button>
      </div>

      {isLoading ? (
        <div className="flex items-center justify-center py-16 text-muted-foreground"><Loader2 className="w-6 h-6 animate-spin mr-3" /> Loading your sleep...</div>
      ) : isError ? (
        <div className="rounded-2xl border border-red-500/30 bg-red-500/10 p-6 text-center">
          <p className="text-red-500 font-medium mb-1">Could not load sleep</p>
          <p className="text-sm text-muted-foreground mb-4">{errorMessage(error)}</p>
          <button className="btn-primary btn-sm" onClick={() => refetch()}>Try again</button>
        </div>
      ) : (
        <>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <MetricCard title="Last night" value={last ? hm(last.total_sleep_minutes) : '--'} subtitle="Target: 7 to 9 hours" icon={Moon} color="bg-primary-500/15 text-primary-500" />
            <MetricCard title="Efficiency" value={last ? `${eff(last)}%` : '--'} subtitle="Asleep / in bed" icon={Battery} color="bg-green-500/15 text-green-500" />
            <MetricCard title="Quality" value={last?.quality_rating ? Q_LABEL[last.quality_rating] : '--'} subtitle="Self-reported" icon={Heart} color="bg-secondary-500/15 text-secondary-500" />
            <MetricCard title="Bedtime" value={last ? clock(last.bedtime) : '--'} subtitle={last ? dayLabel(last.date) : 'No entries yet'} icon={Bed} color="bg-accent-500/15 text-accent-500" />
          </div>

          <div className="card overflow-hidden">
            <div className="border-b border-white/10">
              <nav className="flex overflow-x-auto px-4">
                {[{ id: 'overview', label: 'Overview', icon: Moon }, { id: 'trends', label: 'Weekly Trends', icon: TrendingUp }, { id: 'factors', label: 'Sleep Factors', icon: Brain }].map((tb) => (
                  <button key={tb.id} onClick={() => setTab(tb.id as any)}
                    className={cn('flex items-center gap-2 px-4 py-3 text-sm font-medium border-b-2 transition-colors hover:bg-white/5',
                      tab === tb.id ? 'text-primary-500 border-primary-500' : 'text-muted-foreground border-transparent')}>
                    <tb.icon className="w-4 h-4" /> {tb.label}
                  </button>
                ))}
              </nav>
            </div>
            <div className="p-6">
              {data.length === 0 ? (
                <div className="glass-subtle p-8 rounded-2xl text-center">
                  <Moon className="w-12 h-12 mx-auto text-muted-foreground/50 mb-4" />
                  <p className="text-foreground mb-4">No sleep logged yet</p>
                  <button className="btn-primary" onClick={() => setShowLog(true)}><Plus className="w-4 h-4 mr-2" /> Log Sleep</button>
                </div>
              ) : tab === 'overview' ? (
                <div className="space-y-6">
                  {last && (
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                      {[
                        { l: 'In bed', t: clock(last.bedtime) },
                        { l: 'Fell asleep', t: clock(last.sleep_start) },
                        { l: 'Woke up', t: clock(last.wake_time) },
                        { l: 'Awake in night', t: `${last.awake_minutes ?? 0} min` },
                      ].map((x) => (
                        <div key={x.l} className="glass-subtle p-4 rounded-xl text-center">
                          <p className="text-sm text-foreground/60">{x.l}</p>
                          <p className="text-xl font-bold text-foreground mt-1">{x.t}</p>
                        </div>
                      ))}
                    </div>
                  )}
                  <div><h2 className="heading-6 mb-4">Recent nights</h2><div className="space-y-3">{data.slice(0, 10).map(night)}</div></div>
                </div>
              ) : tab === 'trends' ? (
                <div className="space-y-6">
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <MetricCard title="Avg sleep" value={v.week.length ? hm(v.avgSleep) : '--'} subtitle="Last 7 days" icon={Moon} color="bg-primary-500/15 text-primary-500" />
                    <MetricCard title="Avg efficiency" value={v.week.length ? `${v.avgEff}%` : '--'} subtitle="Last 7 days" icon={Battery} color="bg-green-500/15 text-green-500" />
                    <MetricCard title="Bedtime spread" value={v.sd == null ? '--' : `±${v.sd} min`} subtitle={v.sd == null ? 'Needs 3+ nights' : `Avg bedtime ${v.avgBed}`} icon={Bed} color="bg-accent-500/15 text-accent-500" />
                    <MetricCard title="Sleep debt" value={hm(v.debt)} subtitle="Vs 8h per night, 7 days" icon={TrendingUp} color="bg-red-500/15 text-red-500" />
                  </div>
                  <div className="space-y-3">
                    {Array.from({ length: 7 }, (_, i) => dayStr(-i)).map((d) => {
                      const r = data.find((x) => x.date === d);
                      return (
                        <div key={d}>
                          <div className="flex justify-between text-sm mb-1">
                            <span className="text-foreground">{dayLabel(d)}</span>
                            <span className="text-muted-foreground">{r ? hm(r.total_sleep_minutes) : 'Not logged'}</span>
                          </div>
                          <div className="h-2 bg-muted-foreground/10 rounded-full overflow-hidden">
                            <div className="h-full rounded-full bg-primary-500 transition-all duration-700" style={{ width: `${r ? Math.min(100, (r.total_sleep_minutes / 600) * 100) : 0}%` }} />
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              ) : (
                <div className="space-y-3">
                  {factorRow('Caffeine after noon', Coffee, v.caffeine)}
                  {factorRow('Alcohol before bed', Wine, v.alcohol)}
                  {factorRow('Exercise before bed', Dumbbell, v.exercise)}
                  <div className="flex items-start gap-4 p-4 glass-subtle rounded-xl">
                    <div className="p-3 rounded-xl bg-primary-500/15 text-primary-500"><Smartphone className="w-5 h-5" /></div>
                    <div>
                      <p className="font-medium text-foreground">Screen time before bed</p>
                      <p className="text-sm text-muted-foreground">{v.screenN ? `Averaging ${v.avgScreen} min across ${v.screenN} logged night${v.screenN > 1 ? 's' : ''}.` : 'Add it when you log a night to see your average.'}</p>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </>
      )}

      {showLog && <LogSleepModal onClose={() => setShowLog(false)} />}
    </div>
  );
}

function LogSleepModal({ onClose }: { onClose: () => void }) {
  const qc = useQueryClient();
  const [date, setDate] = useState(dayStr(0));
  const [bedT, setBedT] = useState('23:00');
  const [wakeT, setWakeT] = useState('07:00');
  const [latency, setLatency] = useState('15');
  const [awake, setAwake] = useState('0');
  const [quality, setQuality] = useState('good');
  const [screen, setScreen] = useState('');
  const [caffeine, setCaffeine] = useState(false);
  const [alcohol, setAlcohol] = useState(false);
  const [exercise, setExercise] = useState(false);
  const [error, setError] = useState('');

  const mut = useMutation({
    mutationFn: createSleep,
    onSuccess: () => { toast.success('Sleep logged'); qc.invalidateQueries({ queryKey: ['sleep'] }); onClose(); },
    onError: (e) => setError(errorMessage(e, 'Could not log sleep')),
  });

  function onSubmit(e: FormEvent) {
    e.preventDefault();
    setError('');
    if (!date || !bedT || !wakeT) return setError('Please fill in the date, bedtime and wake time.');
    const wake = toDate(date, wakeT);
    let bed = toDate(date, bedT);
    if (Number.isNaN(wake.getTime()) || Number.isNaN(bed.getTime())) return setError('Please choose valid times.');
    if (bed.getTime() >= wake.getTime()) bed = new Date(bed.getTime() - 86400000);
    const tib = Math.round((wake.getTime() - bed.getTime()) / 60000);
    const lat = Math.round(Number(latency || 0));
    const aw = Math.round(Number(awake || 0));
    if (!Number.isFinite(lat) || lat < 0 || !Number.isFinite(aw) || aw < 0) return setError('Minutes to fall asleep and minutes awake must be 0 or more.');
    const total = tib - lat - aw;
    if (tib > 1200) return setError('Time in bed is over 20 hours. Check your bedtime and wake time.');
    if (total < 0) return setError('Time to fall asleep plus time awake is longer than the time in bed.');
    const payload: any = {
      date,
      source: 'manual',
      bedtime: bed.toISOString(),
      sleep_start: new Date(bed.getTime() + lat * 60000).toISOString(),
      sleep_end: wake.toISOString(),
      wake_time: wake.toISOString(),
      time_in_bed_minutes: tib,
      total_sleep_minutes: total,
      awake_minutes: aw,
      sleep_latency_minutes: lat,
      quality_rating: quality,
      caffeine_after_noon: caffeine,
      alcohol_before_bed: alcohol,
      exercise_before_bed: exercise,
      tags: [],
      interruption_details: [],
    };
    if (screen.trim() !== '') {
      const sc = Math.round(Number(screen));
      if (!Number.isFinite(sc) || sc < 0) return setError('Screen time must be 0 or more minutes.');
      payload.screen_time_before_bed_minutes = sc;
    }
    mut.mutate(payload);
  }

  const check = (id: string, label: string, val: boolean, set: (b: boolean) => void) => (
    <label key={id} htmlFor={id} className="flex items-center gap-3 text-sm text-foreground cursor-pointer">
      <input id={id} type="checkbox" className="w-4 h-4" checked={val} onChange={(e) => set(e.target.checked)} /> {label}
    </label>
  );

  return (
    <Modal title="Log sleep" onClose={onClose}>
      <form onSubmit={onSubmit} className="space-y-4">
        <div className="grid grid-cols-3 gap-4">
          <div>
            <label className={labelClass} htmlFor="s-date">Morning you woke</label>
            <input id="s-date" type="date" className={inputClass} value={date} onChange={(e) => setDate(e.target.value)} />
          </div>
          <div>
            <label className={labelClass} htmlFor="s-bed">Went to bed</label>
            <input id="s-bed" type="time" className={inputClass} value={bedT} onChange={(e) => setBedT(e.target.value)} />
          </div>
          <div>
            <label className={labelClass} htmlFor="s-wake">Woke up</label>
            <input id="s-wake" type="time" className={inputClass} value={wakeT} onChange={(e) => setWakeT(e.target.value)} />
          </div>
        </div>
        <div className="grid grid-cols-3 gap-4">
          <div>
            <label className={labelClass} htmlFor="s-lat">Minutes to fall asleep</label>
            <input id="s-lat" type="number" min="0" step="1" className={inputClass} value={latency} onChange={(e) => setLatency(e.target.value)} />
          </div>
          <div>
            <label className={labelClass} htmlFor="s-aw">Minutes awake in night</label>
            <input id="s-aw" type="number" min="0" step="1" className={inputClass} value={awake} onChange={(e) => setAwake(e.target.value)} />
          </div>
          <div>
            <label className={labelClass} htmlFor="s-q">Quality</label>
            <select id="s-q" className={selectClass} value={quality} onChange={(e) => setQuality(e.target.value)}>
              {QUALITY.map((q) => <option key={q.id} value={q.id}>{q.label}</option>)}
            </select>
          </div>
        </div>
        <div>
          <label className={labelClass} htmlFor="s-scr">Screen time before bed, minutes (optional)</label>
          <input id="s-scr" type="number" min="0" step="1" className={inputClass} value={screen} onChange={(e) => setScreen(e.target.value)} />
        </div>
        <div className="space-y-2">
          {check('s-caf', 'Caffeine after noon', caffeine, setCaffeine)}
          {check('s-alc', 'Alcohol before bed', alcohol, setAlcohol)}
          {check('s-exe', 'Exercise before bed', exercise, setExercise)}
        </div>
        {error && <div className="rounded-xl bg-red-500/10 border border-red-500/30 text-red-500 text-sm px-4 py-3" role="alert">{error}</div>}
        <div className="flex justify-end gap-3 pt-2">
          <button type="button" className="btn-ghost" onClick={onClose}>Cancel</button>
          <button type="submit" className="btn-primary" disabled={mut.isPending}>{mut.isPending ? 'Saving...' : 'Save sleep'}</button>
        </div>
      </form>
    </Modal>
  );
}
