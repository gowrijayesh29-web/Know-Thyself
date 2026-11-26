'use client';

import { useMemo } from 'react';
import { motion } from 'framer-motion';
import { useQuery } from '@tanstack/react-query';
import { MousePointerClick, HeartPulse, Moon, Apple, Zap, BookOpen, TrendingUp, TrendingDown, Droplets, Loader2 } from 'lucide-react';
import { cn, getGreeting } from '@/lib/utils';
import { WellnessScore } from '@/components/wellness-score';
import { dayStr, toDate, listActivities, listNutrition, listHydration } from '@/lib/health-api';
import type { ActivityRecord, NutritionRecord } from '@/lib/health-api';
import { listSleep } from '@/lib/sleep-api';
import type { SleepRecord } from '@/lib/sleep-api';
import { listDigital } from '@/lib/digital-api';
import type { DigitalRecord } from '@/lib/digital-api';

const TARGETS = { screenMin: 360, sleepMin: 480, steps: 10000, waterMl: 2500, activeMin: 30, protein: 130 };

function nav(page: string) { window.dispatchEvent(new CustomEvent('kt-navigate', { detail: page })); }
function localDay(iso: string): string {
  const d = new Date(iso);
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
}
function hm(min: number): string {
  const r = Math.round(min);
  return `${Math.floor(r / 60)}h ${r % 60}m`;
}
function rel(iso: string): string {
  const mins = Math.round((Date.now() - new Date(iso).getTime()) / 60000);
  if (mins < 1) return 'just now';
  if (mins < 60) return `${mins}m ago`;
  const h = Math.round(mins / 60);
  if (h < 24) return `${h}h ago`;
  return `${Math.round(h / 24)}d ago`;
}
const sumOf = (a: number[]) => a.reduce((s, x) => s + x, 0);
const avgOf = (a: number[]) => (a.length ? sumOf(a) / a.length : 0);

async function loadAll() {
  const today = dayStr(0);
  const res = await Promise.allSettled([
    listActivities(dayStr(-13), today),
    listNutrition(dayStr(-6), today),
    listHydration(today, today),
    listSleep(dayStr(-13), today),
    listDigital(toDate(dayStr(-13), '00:00').toISOString(), toDate(today, '23:59').toISOString()),
  ]);
  const pick = (r: PromiseSettledResult<any[]>): any[] => (r.status === 'fulfilled' ? r.value : []);
  return {
    act: pick(res[0]) as ActivityRecord[],
    nut: pick(res[1]) as NutritionRecord[],
    hyd: pick(res[2]) as { amount_ml: number }[],
    sleep: pick(res[3]) as SleepRecord[],
    dig: pick(res[4]) as DigitalRecord[],
  };
}

function MetricCard({ title, value, subtitle, icon, color, delta, trend }: any) {
  return (
    <div className="card-hover group">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm font-medium text-foreground/60 mb-1">{title}</p>
          <p className="text-3xl font-bold text-foreground">{value}</p>
          {subtitle && <p className="text-sm text-muted-foreground mt-1">{subtitle}</p>}
        </div>
        <div className={cn('p-3 rounded-2xl', color)}>{icon}</div>
      </div>
      {delta && (
        <div className="mt-4 flex items-center gap-1 text-sm font-medium text-muted-foreground">
          {trend === 'up' && <TrendingUp className="w-4 h-4" />}
          {trend === 'down' && <TrendingDown className="w-4 h-4" />}
          {delta}
        </div>
      )}
    </div>
  );
}

function ActivityItem({ icon, title, description, time, color }: any) {
  return (
    <div className="flex items-start gap-4 p-4 glass-subtle rounded-2xl">
      <div className={cn('p-2.5 rounded-xl', color)}>{icon}</div>
      <div className="flex-1 min-w-0">
        <p className="font-medium text-foreground truncate">{title}</p>
        <p className="text-sm text-muted-foreground mt-0.5">{description}</p>
      </div>
      <span className="text-xs text-muted-foreground whitespace-nowrap">{time}</span>
    </div>
  );
}

export function OverviewPage() {
  const greeting = getGreeting();
  const today = dayStr(0);
  const yesterday = dayStr(-1);
  const weekStart = dayStr(-6);
  const { data, isLoading } = useQuery({ queryKey: ['overview-data', today], queryFn: loadAll });

  const v = useMemo(() => {
    const act = data?.act ?? [];
    const nut = data?.nut ?? [];
    const hyd = data?.hyd ?? [];
    const sl = data?.sleep ?? [];
    const dg = data?.dig ?? [];

    const digSec = (a: DigitalRecord[]) => sumOf(a.map((r) => r.active_seconds));
    const screenToday = digSec(dg.filter((r) => localDay(r.start_time) === today)) / 60;
    const screenYday = digSec(dg.filter((r) => localDay(r.start_time) === yesterday)) / 60;
    const screenDelta = screenYday > 0 ? Math.round(((screenToday - screenYday) / screenYday) * 100) : null;
    const digWeek = dg.filter((r) => localDay(r.start_time) >= weekStart);
    const digDays = new Set(digWeek.map((r) => localDay(r.start_time))).size;
    const prod = digSec(digWeek.filter((r) => r.is_productive === true));
    const unprod = digSec(digWeek.filter((r) => r.is_productive === false));

    const lastSleep = sl[0];
    const sleepWeek = sl.filter((r) => r.date >= weekStart);
    const avgSleep = avgOf(sleepWeek.map((r) => r.total_sleep_minutes));

    const actToday = act.filter((a) => a.date === today);
    const actWeek = act.filter((a) => a.date >= weekStart);
    const stepsToday = sumOf(actToday.map((a) => a.steps || 0));
    const activeToday = sumOf(actToday.map((a) => a.duration_minutes || 0));
    const stepsWeek = sumOf(actWeek.map((a) => a.steps || 0));
    const activeWeek = sumOf(actWeek.map((a) => a.duration_minutes || 0));
    const waterMl = sumOf(hyd.map((h) => h.amount_ml || 0));
    const calToday = sumOf(nut.filter((n) => n.date === today).map((n) => n.calories || 0));

    const byDay: Record<string, number> = {};
    nut.forEach((n) => { byDay[n.date] = (byDay[n.date] || 0) + (n.protein_g || 0); });
    const protDays = Object.keys(byDay).filter((k) => byDay[k] > 0);
    const avgProtein = Math.round(avgOf(protDays.map((k) => byDay[k])));

    const ins: { title: string; description: string; severity: 'high' | 'medium' | 'positive'; action: string; page: string }[] = [];
    const cw = sl.filter((r) => r.caffeine_after_noon);
    const cwo = sl.filter((r) => !r.caffeine_after_noon);
    if (cw.length && cwo.length) {
      const a = avgOf(cw.map((r) => r.total_sleep_minutes));
      const b = avgOf(cwo.map((r) => r.total_sleep_minutes));
      if (b - a >= 20) ins.push({ title: 'Late caffeine is costing you sleep', description: `Nights with caffeine after noon average ${hm(a)} vs ${hm(b)} without (${cw.length} vs ${cwo.length} nights logged).`, severity: 'high', action: 'See sleep factors', page: 'sleep' });
    }
    if (sleepWeek.length) {
      ins.push({ title: avgSleep < 420 ? 'Sleep is under 7 hours' : 'Sleep is on track', description: `Averaging ${hm(avgSleep)} over ${sleepWeek.length} logged night${sleepWeek.length > 1 ? 's' : ''}. Target: 7 to 9 hours.`, severity: avgSleep < 420 ? 'medium' : 'positive', action: 'View sleep', page: 'sleep' });
    }
    if (prod + unprod > 0) {
      const pct = Math.round((prod / (prod + unprod)) * 100);
      ins.push({ title: pct < 50 ? 'Most screen time is unproductive' : 'Screen time is mostly productive', description: `${pct}% of your tracked screen time this week was productive.`, severity: pct < 50 ? 'medium' : 'positive', action: 'View digital', page: 'digital' });
    }
    if (protDays.length) {
      const low = avgProtein < TARGETS.protein * 0.8;
      ins.push({ title: low ? 'Protein is below target' : 'Protein is near target', description: `Averaging ${avgProtein} g/day vs a ${TARGETS.protein} g default target.`, severity: low ? 'medium' : 'positive', action: 'View nutrition', page: 'nutrition' });
    }

    const recent: { icon: any; title: string; description: string; time: string; at: number; color: string }[] = [];
    act.slice(0, 5).forEach((a) => recent.push({ icon: <HeartPulse className="w-5 h-5" />, title: `${a.activity_type.replace('_', ' ')} workout`, description: `${a.duration_minutes} min`, time: a.start_time, at: new Date(a.start_time).getTime(), color: 'bg-accent-500/15 text-accent-500' }));
    nut.slice(0, 5).forEach((n) => recent.push({ icon: <Apple className="w-5 h-5" />, title: n.food_name, description: `${n.meal_type.replace('_', ' ')}${n.calories ? ` · ${Math.round(n.calories)} kcal` : ''}`, time: n.timestamp, at: new Date(n.timestamp).getTime(), color: 'bg-amber-500/15 text-amber-500' }));
    sl.slice(0, 3).forEach((s) => recent.push({ icon: <Moon className="w-5 h-5" />, title: 'Sleep logged', description: `${hm(s.total_sleep_minutes)} asleep`, time: s.wake_time, at: new Date(s.wake_time).getTime(), color: 'bg-secondary-500/15 text-secondary-500' }));
    dg.slice(0, 5).forEach((d) => recent.push({ icon: <MousePointerClick className="w-5 h-5" />, title: d.domain, description: `${hm(d.active_seconds / 60)} on ${d.category.replace('_', ' ')}`, time: d.start_time, at: new Date(d.start_time).getTime(), color: 'bg-primary-500/15 text-primary-500' }));
    recent.sort((a, b) => b.at - a.at);

    return {
      screenToday, screenDelta, lastSleep, avgSleep, stepsToday, activeToday, stepsWeek, activeWeek, waterMl, calToday,
      avgScreen: digDays ? digSec(digWeek) / 60 / digDays : 0, digDays, sleepNights: sleepWeek.length,
      insights: ins.slice(0, 3), recent: recent.slice(0, 6),
      hasData: act.length + nut.length + hyd.length + sl.length + dg.length > 0,
    };
  }, [data, today, yesterday, weekStart]);

  const targets = [
    { label: 'Screen time under 6h', value: hm(v.screenToday), pct: (v.screenToday / TARGETS.screenMin) * 100 },
    { label: 'Sleep 8h', value: v.lastSleep ? hm(v.lastSleep.total_sleep_minutes) : '--', pct: v.lastSleep ? (v.lastSleep.total_sleep_minutes / TARGETS.sleepMin) * 100 : 0 },
    { label: '10,000 steps', value: v.stepsToday.toLocaleString(), pct: (v.stepsToday / TARGETS.steps) * 100 },
    { label: 'Water 2.5L', value: `${(v.waterMl / 1000).toFixed(1)}L`, pct: (v.waterMl / TARGETS.waterMl) * 100 },
    { label: '30 active minutes', value: `${v.activeToday} min`, pct: (v.activeToday / TARGETS.activeMin) * 100 },
  ];
  const pill = {
    high: ['bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-300', 'High priority'],
    medium: ['bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-300', 'Recommendation'],
    positive: ['bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300', 'Positive trend'],
  } as const;

  return (
    <div className="space-y-8">
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="heading-1">{greeting}!</h1>
          <p className="body-md text-muted-foreground mt-1">Here is your personal snapshot, built from what you have logged.</p>
        </div>
        <div className="flex items-center gap-3">
          <button className="btn-primary" onClick={() => { try { sessionStorage.setItem('kt_open_goal_form', '1'); } catch {} nav('goals'); }}>
            <Zap className="w-4 h-4" /> Quick Action
          </button>
          <button className="btn-outline" onClick={() => nav('reports')}><BookOpen className="w-4 h-4" /> View Report</button>
        </div>
      </motion.div>

      {isLoading ? (
        <div className="flex items-center justify-center py-16 text-muted-foreground"><Loader2 className="w-6 h-6 animate-spin mr-3" /> Loading your day...</div>
      ) : (
        <>
          <WellnessScore />
          {!v.hasData && (
            <div className="glass-subtle p-6 rounded-2xl">
              <p className="text-foreground font-medium mb-1">Nothing logged yet</p>
              <p className="text-sm text-muted-foreground mb-4">Log a workout, meal, night of sleep or some screen time and this page fills in.</p>
              <div className="flex flex-wrap gap-2">
                {[['physical', 'Log a workout'], ['nutrition', 'Log a meal'], ['sleep', 'Log sleep'], ['digital', 'Log screen time']].map(([p, l]) => (
                  <button key={p} className="btn-outline btn-sm" onClick={() => nav(p)}>{l}</button>
                ))}
              </div>
            </div>
          )}

          <div className="grid-auto-fit">
            <MetricCard title="Screen Time Today" value={hm(v.screenToday)} subtitle="Soft limit: 6h (default)" icon={<MousePointerClick className="w-6 h-6" />} color="bg-primary-500/15 text-primary-500"
              delta={v.screenDelta == null ? null : `${Math.abs(v.screenDelta)}% ${v.screenDelta <= 0 ? 'less' : 'more'} than yesterday`} trend={v.screenDelta == null ? undefined : v.screenDelta <= 0 ? 'down' : 'up'} />
            <MetricCard title="Sleep Last Night" value={v.lastSleep ? hm(v.lastSleep.total_sleep_minutes) : '--'} subtitle={v.lastSleep?.quality_rating ? `Quality: ${v.lastSleep.quality_rating.replace('_', ' ')}` : 'Not logged yet'} icon={<Moon className="w-6 h-6" />} color="bg-secondary-500/15 text-secondary-500"
              delta={v.lastSleep && v.sleepNights > 1 ? `7-day average ${hm(v.avgSleep)}` : null} />
            <MetricCard title="Steps Today" value={v.stepsToday.toLocaleString()} subtitle="From logged workouts" icon={<HeartPulse className="w-6 h-6" />} color="bg-accent-500/15 text-accent-500" delta={`${v.activeToday} active min today`} />
            <MetricCard title="Water Today" value={`${(v.waterMl / 1000).toFixed(1)}L`} subtitle={`${Math.round(v.calToday)} kcal eaten today`} icon={<Droplets className="w-6 h-6" />} color="bg-blue-500/15 text-blue-500" delta="Target: 2.5L (default)" />
          </div>

          <div className="grid-auto-fit">
            {v.insights.length === 0 ? (
              <div className="card p-6"><h3 className="heading-6 mb-1">No insights yet</h3><p className="body-sm text-muted-foreground">Log a few days of sleep, meals and screen time and patterns show up here.</p></div>
            ) : v.insights.map((i) => (
              <div key={i.title} className="card-hover p-6">
                <span className={cn('px-2 py-0.5 rounded-full text-xs font-medium', pill[i.severity][0])}>{pill[i.severity][1]}</span>
                <h3 className="heading-6 mt-3 mb-1">{i.title}</h3>
                <p className="body-sm text-muted-foreground">{i.description}</p>
                <button className="btn-primary btn-sm mt-4" onClick={() => nav(i.page)}>{i.action}</button>
              </div>
            ))}
          </div>

          <div className="grid-auto-fit">
            <div className="card p-6">
              <div className="flex items-center justify-between mb-6">
                <h2 className="heading-5">Recent Activity</h2>
                <button className="btn-ghost btn-sm" onClick={() => nav('notifications')}>View All</button>
              </div>
              <div className="space-y-3">
                {v.recent.length === 0 ? <p className="text-sm text-muted-foreground">Nothing yet.</p> : v.recent.map((r, i) => (
                  <ActivityItem key={i} icon={r.icon} title={r.title} description={r.description} time={rel(r.time)} color={r.color} />
                ))}
              </div>
            </div>

            <div className="card p-6">
              <div className="flex items-center justify-between mb-6">
                <h2 className="heading-5">Today&apos;s Targets</h2>
                <button className="btn-ghost btn-sm" onClick={() => nav('goals')}>Goals</button>
              </div>
              <div className="space-y-4">
                {targets.map((t) => (
                  <div key={t.label}>
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium text-foreground">{t.label}</span>
                      <span className="text-sm text-muted-foreground">{t.value}</span>
                    </div>
                    <div className="h-2 bg-muted-foreground/10 rounded-full overflow-hidden">
                      <div className="h-full rounded-full bg-primary-500 transition-all duration-700" style={{ width: `${Math.min(100, Math.max(0, t.pct))}%` }} />
                    </div>
                  </div>
                ))}
                <p className="text-xs text-muted-foreground pt-1">Targets are defaults, not personalised yet.</p>
              </div>
            </div>
          </div>

          <div className="card p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="heading-5">This Week So Far</h2>
              <button className="btn-primary btn-sm" onClick={() => nav('reports')}><BookOpen className="w-4 h-4 mr-2" /> Full Report</button>
            </div>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {[
                { label: 'Avg screen time / day', value: v.digDays ? hm(v.avgScreen) : '--', icon: MousePointerClick },
                { label: 'Avg sleep / night', value: v.sleepNights ? hm(v.avgSleep) : '--', icon: Moon },
                { label: 'Steps (from workouts)', value: v.stepsWeek.toLocaleString(), icon: HeartPulse },
                { label: 'Active minutes', value: String(v.activeWeek), icon: Zap },
              ].map((s) => (
                <div key={s.label} className="glass-subtle p-4 rounded-2xl">
                  <div className="p-2 rounded-xl bg-primary-500/15 text-primary-500 w-fit mb-2"><s.icon className="w-5 h-5" /></div>
                  <p className="text-2xl font-bold text-foreground">{s.value}</p>
                  <p className="text-xs text-muted-foreground mt-1">{s.label}</p>
                </div>
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  );
}
