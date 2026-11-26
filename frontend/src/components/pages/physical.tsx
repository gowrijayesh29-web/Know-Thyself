'use client';

import { useEffect, useMemo, useState, FormEvent } from 'react';
import { motion } from 'framer-motion';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import toast from 'react-hot-toast';
import { Activity, Dumbbell, Flame, Zap, Trophy, Calendar, Clock, Plus, Trash2, Loader2, Footprints, Bike, Waves, Sparkles } from 'lucide-react';
import { cn } from '@/lib/utils';
import { StepsCard } from '@/components/steps-card';
import { errorMessage } from '@/lib/api';
import { Modal, inputClass, selectClass, labelClass } from '@/components/modal';
import type { ActivityRecord } from '@/lib/health-api';
import { listActivities, createActivity, deleteActivity, dayStr, nowTime, toDate } from '@/lib/health-api';

const ACTIVITY_TYPES = [
  { id: 'walking', label: 'Walking' },
  { id: 'running', label: 'Running' },
  { id: 'cycling', label: 'Cycling' },
  { id: 'swimming', label: 'Swimming' },
  { id: 'weight_training', label: 'Strength training' },
  { id: 'bodyweight', label: 'Bodyweight' },
  { id: 'yoga', label: 'Yoga' },
  { id: 'pilates', label: 'Pilates' },
  { id: 'hiit', label: 'HIIT' },
  { id: 'crossfit', label: 'CrossFit' },
  { id: 'rowing', label: 'Rowing' },
  { id: 'elliptical', label: 'Elliptical' },
  { id: 'stair_climbing', label: 'Stair climbing' },
  { id: 'hiking', label: 'Hiking' },
  { id: 'sports', label: 'Sports' },
  { id: 'dance', label: 'Dance' },
  { id: 'martial_arts', label: 'Martial arts' },
  { id: 'stretching', label: 'Stretching' },
  { id: 'mobility', label: 'Mobility' },
  { id: 'other', label: 'Other' },
];
const TYPE_LABEL: Record<string, string> = Object.fromEntries(ACTIVITY_TYPES.map((t) => [t.id, t.label]));

const INTENSITIES = [
  { id: 'very_light', label: 'Very light' },
  { id: 'light', label: 'Light' },
  { id: 'moderate', label: 'Moderate' },
  { id: 'vigorous', label: 'Vigorous' },
  { id: 'very_vigorous', label: 'Very vigorous' },
];
const INTENSITY_STYLE: Record<string, string> = {
  very_light: 'bg-green-500/15 text-green-500',
  light: 'bg-emerald-500/15 text-emerald-500',
  moderate: 'bg-blue-500/15 text-blue-500',
  vigorous: 'bg-orange-500/15 text-orange-500',
  very_vigorous: 'bg-red-500/15 text-red-500',
};

const DAILY_STEPS = 10000;
const DAILY_ACTIVE_MIN = 30;
const WEEKLY_MIN = 150;
const WEEKLY_WORKOUTS = 4;

function typeIcon(type: string) {
  switch (type) {
    case 'running': case 'hiit': return Activity;
    case 'weight_training': case 'bodyweight': case 'crossfit': return Dumbbell;
    case 'yoga': case 'pilates': case 'stretching': case 'mobility': return Sparkles;
    case 'cycling': return Bike;
    case 'walking': case 'hiking': return Footprints;
    case 'swimming': return Waves;
    default: return Dumbbell;
  }
}

const sum = (arr: ActivityRecord[], f: (a: ActivityRecord) => number | null | undefined) =>
  arr.reduce((t, a) => t + (f(a) || 0), 0);

function dayLabel(d: string): string {
  return new Date(`${d}T00:00:00`).toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' });
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

function ActivityRow({ a, onDelete, disabled, showDate }: { a: ActivityRecord; onDelete: () => void; disabled: boolean; showDate?: boolean }) {
  const Icon = typeIcon(a.activity_type);
  const time = new Date(a.start_time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  return (
    <div className="flex items-center justify-between gap-3 p-4 glass-subtle rounded-xl">
      <div className="flex items-center gap-4 min-w-0">
        <div className={cn('p-3 rounded-xl', INTENSITY_STYLE[a.intensity || ''] || 'bg-slate-500/15 text-slate-400')}>
          <Icon className="w-5 h-5" />
        </div>
        <div className="min-w-0">
          <p className="font-medium text-foreground truncate">{TYPE_LABEL[a.activity_type] || a.activity_type}</p>
          <p className="text-sm text-muted-foreground capitalize">
            {showDate ? `${dayLabel(a.date)} · ` : ''}{time}{a.intensity ? ` · ${a.intensity.replace('_', ' ')}` : ''}
          </p>
        </div>
      </div>
      <div className="flex items-center gap-5 text-right">
        <div>
          <p className="font-semibold text-foreground">{a.duration_minutes} min</p>
          <p className="text-xs text-muted-foreground">Duration</p>
        </div>
        {a.calories_burned ? (
          <div className="hidden sm:block">
            <p className="font-semibold text-foreground">{Math.round(a.calories_burned)} kcal</p>
            <p className="text-xs text-muted-foreground">Burned</p>
          </div>
        ) : null}
        {a.steps ? (
          <div className="hidden md:block">
            <p className="font-semibold text-foreground">{a.steps.toLocaleString()}</p>
            <p className="text-xs text-muted-foreground">Steps</p>
          </div>
        ) : null}
        <button title="Delete" disabled={disabled} onClick={onDelete} className="p-2 rounded-xl glass-subtle hover:bg-red-500/10 transition-colors">
          <Trash2 className="w-4 h-4 text-red-500" />
        </button>
      </div>
    </div>
  );
}

export function PhysicalPage() {
  const qc = useQueryClient();
  const today = dayStr(0);
  const [tab, setTab] = useState<'today' | 'week' | 'history'>('today');
  const [showLog, setShowLog] = useState(false);
  const [preset, setPreset] = useState('running');

  useEffect(() => {
    try {
      if (sessionStorage.getItem('kt_open_workout_form')) {
        sessionStorage.removeItem('kt_open_workout_form');
        setShowLog(true);
      }
    } catch {}
    const open = () => {
      try { sessionStorage.removeItem('kt_open_workout_form'); } catch {}
      setShowLog(true);
    };
    window.addEventListener('kt-open-workout-form', open);
    return () => window.removeEventListener('kt-open-workout-form', open);
  }, []);

  const { data = [], isLoading, isError, error, refetch } = useQuery({
    queryKey: ['activities', today],
    queryFn: () => listActivities(dayStr(-29), dayStr(0)),
  });

  const delMut = useMutation({
    mutationFn: (id: string) => deleteActivity(id),
    onSuccess: () => { toast.success('Workout deleted'); qc.invalidateQueries({ queryKey: ['activities'] }); },
    onError: (e) => toast.error(errorMessage(e)),
  });

  const view = useMemo(() => {
    const weekStart = dayStr(-6);
    const todayItems = data.filter((a) => a.date === today);
    const weekItems = data.filter((a) => a.date >= weekStart);
    const days = new Set(data.map((a) => a.date));
    let streak = 0;
    let off = days.has(today) ? 0 : -1;
    while (days.has(dayStr(off)) && streak < 30) { streak++; off--; }
    return { todayItems, weekItems, streak };
  }, [data, today]);

  const openLog = (type = 'running') => { setPreset(type); setShowLog(true); };
  const confirmDelete = (a: ActivityRecord) => {
    if (window.confirm('Delete this workout?')) delMut.mutate(a.id);
  };

  const t = view.todayItems;
  const w = view.weekItems;

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="heading-1">Physical Health</h1>
          <p className="body-md text-muted-foreground mt-1">Log your workouts and see how your week is shaping up.</p>
        </div>
        <button className="btn-primary" onClick={() => openLog()}>
          <Plus className="w-4 h-4 mr-2" /> Log Workout
        </button>
      </div>

      <StepsCard />

      {isLoading ? (
        <div className="flex items-center justify-center py-16 text-muted-foreground">
          <Loader2 className="w-6 h-6 animate-spin mr-3" /> Loading your workouts...
        </div>
      ) : isError ? (
        <div className="rounded-2xl border border-red-500/30 bg-red-500/10 p-6 text-center">
          <p className="text-red-500 font-medium mb-1">Could not load workouts</p>
          <p className="text-sm text-muted-foreground mb-4">{errorMessage(error)}</p>
          <button className="btn-primary btn-sm" onClick={() => refetch()}>Try again</button>
        </div>
      ) : (
        <>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <MetricCard title="Steps today" value={sum(t, (a) => a.steps).toLocaleString()} subtitle={`Target: ${DAILY_STEPS.toLocaleString()} (from logged workouts)`}
              progress={(sum(t, (a) => a.steps) / DAILY_STEPS) * 100} icon={Activity} color="bg-primary-500/15 text-primary-500" />
            <MetricCard title="Active minutes" value={sum(t, (a) => a.duration_minutes)} subtitle={`Target: ${DAILY_ACTIVE_MIN} min`}
              progress={(sum(t, (a) => a.duration_minutes) / DAILY_ACTIVE_MIN) * 100} icon={Clock} color="bg-accent-500/15 text-accent-500" />
            <MetricCard title="Calories burned" value={Math.round(sum(t, (a) => a.calories_burned))} subtitle="Today" icon={Flame} color="bg-red-500/15 text-red-500" />
            <MetricCard title="Workouts today" value={t.length} subtitle={`${sum(t, (a) => a.duration_minutes)} min total`} icon={Dumbbell} color="bg-secondary-500/15 text-secondary-500" />
          </div>

          <div className="card overflow-hidden">
            <div className="border-b border-white/10">
              <nav className="flex overflow-x-auto px-4" aria-label="Physical health tabs">
                {[
                  { id: 'today', label: 'Today', icon: Calendar },
                  { id: 'week', label: 'This Week', icon: Trophy },
                  { id: 'history', label: 'History', icon: Clock },
                ].map((tb) => (
                  <button key={tb.id} onClick={() => setTab(tb.id as any)}
                    className={cn('flex items-center gap-2 px-4 py-3 text-sm font-medium border-b-2 transition-colors hover:bg-white/5',
                      tab === tb.id ? 'text-primary-500 border-primary-500' : 'text-muted-foreground border-transparent')}>
                    <tb.icon className="w-4 h-4" /> {tb.label}
                  </button>
                ))}
              </nav>
            </div>

            <div className="p-6">
              {tab === 'today' && (
                <div className="space-y-6">
                  <div>
                    <h2 className="heading-6 mb-4">Today's workouts</h2>
                    {t.length === 0 ? (
                      <div className="glass-subtle p-8 rounded-2xl text-center">
                        <Dumbbell className="w-12 h-12 mx-auto text-muted-foreground/50 mb-4" />
                        <p className="text-foreground mb-2">No workouts logged yet</p>
                        <p className="text-sm text-muted-foreground mb-4">Log one to start today's totals.</p>
                        <button className="btn-primary" onClick={() => openLog()}><Plus className="w-4 h-4 mr-2" /> Log Workout</button>
                      </div>
                    ) : (
                      <div className="space-y-3">
                        {t.map((a) => <ActivityRow key={a.id} a={a} disabled={delMut.isPending} onDelete={() => confirmDelete(a)} />)}
                      </div>
                    )}
                  </div>
                  <div>
                    <h2 className="heading-6 mb-4">Quick log</h2>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                      {[
                        { label: 'Run', type: 'running', icon: Activity },
                        { label: 'Strength', type: 'weight_training', icon: Dumbbell },
                        { label: 'Yoga', type: 'yoga', icon: Sparkles },
                        { label: 'Walk', type: 'walking', icon: Footprints },
                      ].map((q) => (
                        <button key={q.label} onClick={() => openLog(q.type)} className="glass-subtle p-4 rounded-xl text-center hover:bg-white/5 transition-colors">
                          <q.icon className="w-6 h-6 mx-auto mb-2 text-primary-500" />
                          <p className="text-sm font-medium text-foreground">{q.label}</p>
                        </button>
                      ))}
                    </div>
                  </div>
                </div>
              )}

              {tab === 'week' && (
                <div className="space-y-6">
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <MetricCard title="Weekly workouts" value={w.length} subtitle={`Target: ${WEEKLY_WORKOUTS}`} progress={(w.length / WEEKLY_WORKOUTS) * 100} icon={Trophy} color="bg-yellow-500/15 text-yellow-500" />
                    <MetricCard title="Active minutes" value={sum(w, (a) => a.duration_minutes)} subtitle={`Target: ${WEEKLY_MIN}`} progress={(sum(w, (a) => a.duration_minutes) / WEEKLY_MIN) * 100} icon={Clock} color="bg-accent-500/15 text-accent-500" />
                    <MetricCard title="Calories burned" value={Math.round(sum(w, (a) => a.calories_burned))} subtitle="Last 7 days" icon={Flame} color="bg-red-500/15 text-red-500" />
                    <MetricCard title="Current streak" value={view.streak} subtitle="Consecutive days" icon={Zap} color="bg-green-500/15 text-green-500" />
                  </div>
                  <div className="space-y-3">
                    {Array.from({ length: 7 }, (_, i) => dayStr(-i)).map((d) => {
                      const items = w.filter((a) => a.date === d);
                      return (
                        <div key={d} className="p-4 glass-subtle rounded-xl">
                          <div className="flex items-center justify-between">
                            <span className="font-medium text-foreground">{dayLabel(d)}{d === today ? ' (today)' : ''}</span>
                            {items.length === 0 ? (
                              <span className="text-sm text-muted-foreground">Rest day</span>
                            ) : (
                              <span className="text-sm text-muted-foreground">
                                {items.length} workout{items.length > 1 ? 's' : ''} · {sum(items, (a) => a.duration_minutes)} min
                              </span>
                            )}
                          </div>
                          {items.length > 0 && (
                            <p className="text-sm text-muted-foreground mt-1">
                              {items.map((a) => TYPE_LABEL[a.activity_type] || a.activity_type).join(', ')}
                            </p>
                          )}
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}

              {tab === 'history' && (
                data.length === 0 ? (
                  <div className="text-center py-8">
                    <Calendar className="w-14 h-14 mx-auto text-muted-foreground/50 mb-4" />
                    <p className="text-muted-foreground">Nothing in the last 30 days yet.</p>
                  </div>
                ) : (
                  <div className="space-y-3">
                    {data.map((a) => <ActivityRow key={a.id} a={a} showDate disabled={delMut.isPending} onDelete={() => confirmDelete(a)} />)}
                  </div>
                )
              )}
            </div>
          </div>
        </>
      )}

      {showLog && <LogWorkoutModal preset={preset} onClose={() => setShowLog(false)} />}
    </div>
  );
}

function LogWorkoutModal({ preset, onClose }: { preset: string; onClose: () => void }) {
  const qc = useQueryClient();
  const [type, setType] = useState(preset);
  const [duration, setDuration] = useState('');
  const [intensity, setIntensity] = useState('moderate');
  const [calories, setCalories] = useState('');
  const [steps, setSteps] = useState('');
  const [distance, setDistance] = useState('');
  const [date, setDate] = useState(dayStr(0));
  const [time, setTime] = useState(nowTime());
  const [notes, setNotes] = useState('');
  const [error, setError] = useState('');

  const mut = useMutation({
    mutationFn: createActivity,
    onSuccess: () => { toast.success('Workout logged'); qc.invalidateQueries({ queryKey: ['activities'] }); onClose(); },
    onError: (e) => setError(errorMessage(e, 'Could not log workout')),
  });

  function optNum(v: string): number | undefined | null {
    if (v.trim() === '') return undefined;
    const n = Number(v);
    return Number.isFinite(n) && n >= 0 ? n : null;
  }

  function onSubmit(e: FormEvent) {
    e.preventDefault();
    setError('');
    const dur = Math.round(Number(duration));
    if (!duration.trim() || !Number.isFinite(dur) || dur < 1) return setError('Duration must be at least 1 minute.');
    const cal = optNum(calories), st = optNum(steps), dist = optNum(distance);
    if (cal === null || st === null || dist === null) return setError('Calories, steps and distance must be numbers, 0 or more.');
    const start = toDate(date, time);
    if (!date || !time || Number.isNaN(start.getTime())) return setError('Please choose a valid date and time.');
    const end = new Date(start.getTime() + dur * 60000);
    const payload: any = {
      date,
      activity_type: type,
      start_time: start.toISOString(),
      end_time: end.toISOString(),
      duration_minutes: dur,
      intensity,
      tags: [],
      muscle_groups: [],
    };
    if (cal !== undefined) payload.calories_burned = cal;
    if (st !== undefined) payload.steps = Math.round(st);
    if (dist !== undefined) payload.distance_km = dist;
    if (notes.trim()) payload.notes = notes.trim();
    mut.mutate(payload);
  }

  return (
    <Modal title="Log workout" onClose={onClose}>
      <form onSubmit={onSubmit} className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className={labelClass} htmlFor="w-type">Type</label>
            <select id="w-type" className={selectClass} value={type} onChange={(e) => setType(e.target.value)}>
              {ACTIVITY_TYPES.map((a) => <option key={a.id} value={a.id}>{a.label}</option>)}
            </select>
          </div>
          <div>
            <label className={labelClass} htmlFor="w-int">Intensity</label>
            <select id="w-int" className={selectClass} value={intensity} onChange={(e) => setIntensity(e.target.value)}>
              {INTENSITIES.map((a) => <option key={a.id} value={a.id}>{a.label}</option>)}
            </select>
          </div>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className={labelClass} htmlFor="w-dur">Duration (minutes)</label>
            <input id="w-dur" type="number" min="1" step="1" className={inputClass} value={duration} onChange={(e) => setDuration(e.target.value)} placeholder="e.g. 30" autoFocus />
          </div>
          <div>
            <label className={labelClass} htmlFor="w-cal">Calories burned (optional)</label>
            <input id="w-cal" type="number" min="0" step="any" className={inputClass} value={calories} onChange={(e) => setCalories(e.target.value)} />
          </div>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className={labelClass} htmlFor="w-steps">Steps (optional)</label>
            <input id="w-steps" type="number" min="0" step="1" className={inputClass} value={steps} onChange={(e) => setSteps(e.target.value)} />
          </div>
          <div>
            <label className={labelClass} htmlFor="w-dist">Distance km (optional)</label>
            <input id="w-dist" type="number" min="0" step="any" className={inputClass} value={distance} onChange={(e) => setDistance(e.target.value)} />
          </div>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className={labelClass} htmlFor="w-date">Date</label>
            <input id="w-date" type="date" className={inputClass} value={date} onChange={(e) => setDate(e.target.value)} />
          </div>
          <div>
            <label className={labelClass} htmlFor="w-time">Start time</label>
            <input id="w-time" type="time" className={inputClass} value={time} onChange={(e) => setTime(e.target.value)} />
          </div>
        </div>
        <div>
          <label className={labelClass} htmlFor="w-notes">Notes (optional)</label>
          <textarea id="w-notes" rows={2} className={inputClass} value={notes} onChange={(e) => setNotes(e.target.value)} />
        </div>
        {error && <div className="rounded-xl bg-red-500/10 border border-red-500/30 text-red-500 text-sm px-4 py-3" role="alert">{error}</div>}
        <div className="flex justify-end gap-3 pt-2">
          <button type="button" className="btn-ghost" onClick={onClose}>Cancel</button>
          <button type="submit" className="btn-primary" disabled={mut.isPending}>{mut.isPending ? 'Saving...' : 'Save workout'}</button>
        </div>
      </form>
    </Modal>
  );
}