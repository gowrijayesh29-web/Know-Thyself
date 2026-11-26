'use client';

import { useEffect, useMemo, useState, FormEvent } from 'react';
import { motion } from 'framer-motion';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import toast from 'react-hot-toast';
import {
  Target, Plus, Smartphone, Dumbbell, Apple, Moon, BookOpen, Briefcase, Brain, Droplets,
  Sparkles, Flame, Check, Trash2, PauseCircle, PlayCircle, X, Loader2, TrendingUp,
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { errorMessage } from '@/lib/api';
import type { Goal } from '@/lib/goals-api';
import {
  CATEGORIES, UNITS, FREQUENCIES, listGoals, createGoal, updateGoal, deleteGoal, logProgress, todayStr,
} from '@/lib/goals-api';

const CATEGORY_ICONS: Record<string, any> = {
  digital_wellbeing: Smartphone,
  physical_activity: Dumbbell,
  nutrition: Apple,
  sleep: Moon,
  hydration: Droplets,
  study: BookOpen,
  work: Briefcase,
  mental_wellbeing: Brain,
  personal_routine: Sparkles,
  general_lifestyle: Target,
};

const CATEGORY_STYLES: Record<string, string> = {
  digital_wellbeing: 'bg-blue-500/15 text-blue-500',
  physical_activity: 'bg-red-500/15 text-red-500',
  nutrition: 'bg-green-500/15 text-green-500',
  sleep: 'bg-indigo-500/15 text-indigo-400',
  hydration: 'bg-cyan-500/15 text-cyan-500',
  study: 'bg-purple-500/15 text-purple-500',
  work: 'bg-amber-500/15 text-amber-500',
  mental_wellbeing: 'bg-pink-500/15 text-pink-500',
  personal_routine: 'bg-teal-500/15 text-teal-500',
  general_lifestyle: 'bg-slate-500/15 text-slate-400',
};

const PRIORITY: Record<number, { label: string; cls: string }> = {
  1: { label: 'High', cls: 'bg-red-500/15 text-red-500' },
  2: { label: 'Medium', cls: 'bg-yellow-500/15 text-yellow-500' },
  3: { label: 'Low', cls: 'bg-green-500/15 text-green-500' },
};

const inputClass =
  'w-full px-4 py-2.5 glass-subtle rounded-xl text-sm text-foreground placeholder:text-muted-foreground/50 focus:outline-none focus:ring-2 focus:ring-primary-500/40 transition-all';
const selectClass = inputClass + ' [&>option]:bg-white [&>option]:text-slate-900';
const labelClass = 'block text-sm font-medium text-foreground/80 mb-1.5';

function fmt(n: number): string {
  if (n === null || n === undefined || Number.isNaN(n)) return '0';
  return Number.isInteger(n) ? String(n) : n.toFixed(1);
}

function unitLabel(u: string): string {
  return (u || '').replace('_', ' ');
}

export function GoalsPage() {
  const qc = useQueryClient();
  const [category, setCategory] = useState('all');
  const [statusFilter, setStatusFilter] = useState('all');
  const [showCreate, setShowCreate] = useState(false);
  const [logTarget, setLogTarget] = useState<Goal | null>(null);

  useEffect(() => {
    try {
      if (sessionStorage.getItem('kt_open_goal_form')) {
        sessionStorage.removeItem('kt_open_goal_form');
        setShowCreate(true);
      }
    } catch {}
    const open = () => {
      try { sessionStorage.removeItem('kt_open_goal_form'); } catch {}
      setShowCreate(true);
    };
    window.addEventListener('kt-open-goal-form', open);
    return () => window.removeEventListener('kt-open-goal-form', open);
  }, []);

  const { data: goals = [], isLoading, isError, error, refetch } = useQuery({
    queryKey: ['goals'],
    queryFn: listGoals,
  });

  const refresh = () => qc.invalidateQueries({ queryKey: ['goals'] });

  const statusMut = useMutation({
    mutationFn: ({ id, status }: { id: string; status: string }) => updateGoal(id, { status }),
    onSuccess: (_d, v) => {
      toast.success(v.status === 'completed' ? 'Goal completed' : v.status === 'paused' ? 'Goal paused' : 'Goal resumed');
      refresh();
    },
    onError: (e) => toast.error(errorMessage(e)),
  });

  const deleteMut = useMutation({
    mutationFn: (id: string) => deleteGoal(id),
    onSuccess: () => { toast.success('Goal deleted'); refresh(); },
    onError: (e) => toast.error(errorMessage(e)),
  });

  const filtered = useMemo(
    () =>
      goals.filter((g) => {
        const catOk = category === 'all' || g.category === category;
        const statusOk = statusFilter === 'all' || g.status === statusFilter;
        return catOk && statusOk;
      }),
    [goals, category, statusFilter]
  );

  const stats = useMemo(() => {
    const active = goals.filter((g) => g.status === 'active');
    const avg = active.length
      ? Math.round(active.reduce((a, g) => a + (g.progress_percentage || 0), 0) / active.length)
      : 0;
    const best = goals.reduce((m, g) => Math.max(m, g.streak_days || 0), 0);
    return { active: active.length, avg, best, done: goals.filter((g) => g.status === 'completed').length };
  }, [goals]);

  const busy = statusMut.isPending || deleteMut.isPending;

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="heading-1">Goals</h1>
          <p className="body-md text-muted-foreground mt-1">
            Set targets, log your progress, and build streaks.
          </p>
        </div>
        <button className="btn-primary" onClick={() => setShowCreate(true)}>
          <Plus className="w-4 h-4 mr-2" />
          New Goal
        </button>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          { label: 'Active goals', value: String(stats.active), icon: Target },
          { label: 'Avg progress', value: stats.avg + '%', icon: TrendingUp },
          { label: 'Best streak', value: stats.best + ' days', icon: Flame },
          { label: 'Completed', value: String(stats.done), icon: Check },
        ].map((s) => (
          <div key={s.label} className="glass-subtle rounded-2xl p-4">
            <s.icon className="w-5 h-5 text-primary-500 mb-2" />
            <p className="text-2xl font-bold text-foreground">{s.value}</p>
            <p className="text-xs text-muted-foreground mt-1">{s.label}</p>
          </div>
        ))}
      </div>

      <div className="flex flex-wrap gap-2">
        {[{ id: 'all', label: 'All' }, ...CATEGORIES].map((c) => (
          <button
            key={c.id}
            onClick={() => setCategory(c.id)}
            className={cn(
              'px-4 py-2 rounded-xl text-sm font-medium transition-colors',
              category === c.id
                ? 'bg-primary-500/20 text-primary-500'
                : 'glass-subtle text-foreground/70 hover:bg-white/5'
            )}
          >
            {c.label}
          </button>
        ))}
      </div>

      <div className="flex flex-wrap gap-2">
        {['all', 'active', 'paused', 'completed'].map((st) => (
          <button
            key={st}
            onClick={() => setStatusFilter(st)}
            className={cn(
              'px-4 py-2 rounded-xl text-sm font-medium transition-colors',
              statusFilter === st
                ? 'bg-primary-500/20 text-primary-500'
                : 'glass-subtle text-foreground/70 hover:bg-white/5'
            )}
          >
            {st.charAt(0).toUpperCase() + st.slice(1)}
          </button>
        ))}
      </div>

      {isLoading ? (
        <div className="flex items-center justify-center py-16 text-muted-foreground">
          <Loader2 className="w-6 h-6 animate-spin mr-3" />
          Loading your goals...
        </div>
      ) : isError ? (
        <div className="rounded-2xl border border-red-500/30 bg-red-500/10 p-6 text-center">
          <p className="text-red-500 font-medium mb-1">Could not load goals</p>
          <p className="text-sm text-muted-foreground mb-4">{errorMessage(error)}</p>
          <button className="btn-primary btn-sm" onClick={() => refetch()}>Try again</button>
        </div>
      ) : filtered.length === 0 ? (
        <div className="card-hover p-10 text-center border-2 border-dashed border-white/20">
          <Target className="w-14 h-14 mx-auto text-muted-foreground/50 mb-4" />
          <h3 className="heading-5 mb-2">{goals.length === 0 ? 'No goals yet' : 'No goals match these filters'}</h3>
          <p className="text-muted-foreground mb-4">
            {goals.length === 0 ? 'Create your first goal to start tracking progress.' : 'Try a different category or status.'}
          </p>
          {goals.length === 0 && (
            <button className="btn-primary" onClick={() => setShowCreate(true)}>
              <Plus className="w-4 h-4 mr-2" />
              Create Goal
            </button>
          )}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filtered.map((goal, index) => (
            <GoalCard
              key={goal.id}
              goal={goal}
              index={index}
              busy={busy}
              onLog={() => setLogTarget(goal)}
              onStatus={(status) => statusMut.mutate({ id: goal.id, status })}
              onDelete={() => {
                if (window.confirm(`Delete "${goal.title}"? This cannot be undone.`)) deleteMut.mutate(goal.id);
              }}
            />
          ))}
        </div>
      )}

      {showCreate && <CreateGoalModal onClose={() => setShowCreate(false)} />}
      {logTarget && <LogProgressModal goal={logTarget} onClose={() => setLogTarget(null)} />}
    </div>
  );
}

function GoalCard({ goal, index, busy, onLog, onStatus, onDelete }: {
  goal: Goal; index: number; busy: boolean;
  onLog: () => void; onStatus: (s: string) => void; onDelete: () => void;
}) {
  const Icon = CATEGORY_ICONS[goal.category] || Target;
  const pct = Math.round(Math.min(100, Math.max(0, goal.progress_percentage || 0)));
  const pr = PRIORITY[goal.priority] || PRIORITY[2];
  const isActive = goal.status === 'active';
  const isPaused = goal.status === 'paused';
  const isDone = goal.status === 'completed';

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: Math.min(index, 8) * 0.04 }}
      className={cn('card-hover relative p-5', !isActive && 'opacity-80')}
    >
      <div className="flex items-start justify-between mb-4">
        <div className={cn('p-3 rounded-xl', CATEGORY_STYLES[goal.category] || CATEGORY_STYLES.general_lifestyle)}>
          <Icon className="w-5 h-5" />
        </div>
        <div className="flex items-center gap-2">
          {!isActive && (
            <span className="px-2 py-1 rounded-full text-xs font-medium bg-slate-500/15 text-slate-400">
              {goal.status}
            </span>
          )}
          <span className={cn('px-2 py-1 rounded-full text-xs font-medium', pr.cls)}>{pr.label}</span>
        </div>
      </div>

      <h3 className="font-semibold text-foreground mb-1 line-clamp-1">{goal.title}</h3>
      <p className="text-sm text-muted-foreground mb-4">
        {fmt(goal.current_value)} / {fmt(goal.target_value)} {unitLabel(goal.target_unit)} ({goal.frequency})
      </p>

      <div className="relative w-24 h-24 mx-auto mb-4">
        <svg className="w-full h-full -rotate-90" viewBox="0 0 96 96">
          <circle cx="48" cy="48" r="40" fill="none" stroke="currentColor" strokeWidth="6" className="text-muted-foreground/10" />
          <circle
            cx="48" cy="48" r="40" fill="none" stroke="currentColor" strokeWidth="6" strokeLinecap="round"
            className={isDone ? 'text-green-500' : 'text-primary-500'}
            style={{ strokeDasharray: 251, strokeDashoffset: 251 - (pct / 100) * 251, transition: 'stroke-dashoffset 0.8s ease' }}
          />
        </svg>
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="text-center">
            <p className="text-xl font-bold text-foreground">{pct}%</p>
            <p className="text-xs text-muted-foreground">{goal.streak_days || 0} day streak</p>
          </div>
        </div>
      </div>

      <div className="flex items-center justify-between gap-2 pt-4 border-t border-white/10">
        {isActive ? (
          <button className="btn-primary btn-sm" onClick={onLog} disabled={busy}>Log progress</button>
        ) : (
          <span className="text-xs text-muted-foreground">{isDone ? 'Goal completed' : 'Paused'}</span>
        )}
        <div className="flex items-center gap-1">
          {isActive && (
            <button title="Mark completed" disabled={busy} onClick={() => onStatus('completed')}
              className="p-2 rounded-xl glass-subtle hover:bg-white/10 transition-colors">
              <Check className="w-4 h-4 text-green-500" />
            </button>
          )}
          {isActive && (
            <button title="Pause" disabled={busy} onClick={() => onStatus('paused')}
              className="p-2 rounded-xl glass-subtle hover:bg-white/10 transition-colors">
              <PauseCircle className="w-4 h-4 text-foreground/70" />
            </button>
          )}
          {(isPaused || isDone) && (
            <button title="Reactivate" disabled={busy} onClick={() => onStatus('active')}
              className="p-2 rounded-xl glass-subtle hover:bg-white/10 transition-colors">
              <PlayCircle className="w-4 h-4 text-primary-500" />
            </button>
          )}
          <button title="Delete" disabled={busy} onClick={onDelete}
            className="p-2 rounded-xl glass-subtle hover:bg-red-500/10 transition-colors">
            <Trash2 className="w-4 h-4 text-red-500" />
          </button>
        </div>
      </div>
    </motion.div>
  );
}

function Modal({ title, onClose, children }: { title: string; onClose: () => void; children: React.ReactNode }) {
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => { if (e.key === 'Escape') onClose(); };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [onClose]);

  return (
    <div className="fixed inset-0 z-[70] flex items-center justify-center p-4 bg-black/60" onClick={onClose}>
      <motion.div
        initial={{ opacity: 0, y: 16, scale: 0.97 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        className="w-full max-w-lg max-h-[90vh] overflow-y-auto rounded-3xl p-6 bg-white dark:bg-surface-dark border border-white/10 shadow-elevation-4 text-foreground"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between mb-5">
          <h2 className="text-xl font-bold text-foreground">{title}</h2>
          <button onClick={onClose} className="p-2 rounded-xl hover:bg-white/10" aria-label="Close">
            <X className="w-5 h-5" />
          </button>
        </div>
        {children}
      </motion.div>
    </div>
  );
}

function CreateGoalModal({ onClose }: { onClose: () => void }) {
  const qc = useQueryClient();
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [category, setCategory] = useState('digital_wellbeing');
  const [frequency, setFrequency] = useState('daily');
  const [target, setTarget] = useState('');
  const [unit, setUnit] = useState('hours');
  const [priority, setPriority] = useState('2');
  const [error, setError] = useState('');

  const mut = useMutation({
    mutationFn: createGoal,
    onSuccess: () => {
      toast.success('Goal created');
      qc.invalidateQueries({ queryKey: ['goals'] });
      onClose();
    },
    onError: (e) => setError(errorMessage(e, 'Could not create goal')),
  });

  function onSubmit(e: FormEvent) {
    e.preventDefault();
    setError('');
    const tv = Number(target);
    if (!title.trim()) return setError('Please give the goal a title.');
    if (target.trim() === '' || !Number.isFinite(tv) || tv < 0) return setError('Target must be a number, 0 or more.');
    mut.mutate({
      title: title.trim(),
      description: description.trim() || null,
      category,
      frequency,
      target_value: tv,
      target_unit: unit,
      start_date: todayStr(),
      priority: Number(priority),
      tags: [],
      reminder_enabled: false,
    });
  }

  return (
    <Modal title="New goal" onClose={onClose}>
      <form onSubmit={onSubmit} className="space-y-4">
        <div>
          <label className={labelClass} htmlFor="g-title">Title</label>
          <input id="g-title" className={inputClass} value={title} onChange={(e) => setTitle(e.target.value)} placeholder="e.g. Walk 10,000 steps" autoFocus />
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className={labelClass} htmlFor="g-cat">Category</label>
            <select id="g-cat" className={selectClass} value={category} onChange={(e) => setCategory(e.target.value)}>
              {CATEGORIES.map((c) => <option key={c.id} value={c.id}>{c.label}</option>)}
            </select>
          </div>
          <div>
            <label className={labelClass} htmlFor="g-freq">Repeats</label>
            <select id="g-freq" className={selectClass} value={frequency} onChange={(e) => setFrequency(e.target.value)}>
              {FREQUENCIES.map((f) => <option key={f} value={f}>{f}</option>)}
            </select>
          </div>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className={labelClass} htmlFor="g-target">Target</label>
            <input id="g-target" type="number" min="0" step="any" className={inputClass} value={target} onChange={(e) => setTarget(e.target.value)} placeholder="e.g. 10000" />
          </div>
          <div>
            <label className={labelClass} htmlFor="g-unit">Unit</label>
            <select id="g-unit" className={selectClass} value={unit} onChange={(e) => setUnit(e.target.value)}>
              {UNITS.map((u) => <option key={u} value={u}>{unitLabel(u)}</option>)}
            </select>
          </div>
        </div>
        <div>
          <label className={labelClass} htmlFor="g-pri">Priority</label>
          <select id="g-pri" className={selectClass} value={priority} onChange={(e) => setPriority(e.target.value)}>
            <option value="1">High</option>
            <option value="2">Medium</option>
            <option value="3">Low</option>
          </select>
        </div>
        <div>
          <label className={labelClass} htmlFor="g-desc">Notes (optional)</label>
          <textarea id="g-desc" rows={2} className={inputClass} value={description} onChange={(e) => setDescription(e.target.value)} />
        </div>
        {error && (
          <div className="rounded-xl bg-red-500/10 border border-red-500/30 text-red-500 text-sm px-4 py-3" role="alert">{error}</div>
        )}
        <div className="flex justify-end gap-3 pt-2">
          <button type="button" className="btn-ghost" onClick={onClose}>Cancel</button>
          <button type="submit" className="btn-primary" disabled={mut.isPending}>
            {mut.isPending ? 'Creating...' : 'Create goal'}
          </button>
        </div>
      </form>
    </Modal>
  );
}

function LogProgressModal({ goal, onClose }: { goal: Goal; onClose: () => void }) {
  const qc = useQueryClient();
  const [value, setValue] = useState(goal.current_value ? String(goal.current_value) : '');
  const [override, setOverride] = useState<boolean | null>(null);
  const [error, setError] = useState('');

  const num = Number(value);
  const autoAchieved = value.trim() !== '' && Number.isFinite(num) && num >= goal.target_value;
  const achieved = override ?? autoAchieved;

  const mut = useMutation({
    mutationFn: (payload: any) => logProgress(goal.id, payload),
    onSuccess: () => {
      toast.success('Progress logged');
      qc.invalidateQueries({ queryKey: ['goals'] });
      onClose();
    },
    onError: (e) => setError(errorMessage(e, 'Could not log progress')),
  });

  function onSubmit(e: FormEvent) {
    e.preventDefault();
    setError('');
    if (value.trim() === '' || !Number.isFinite(num) || num < 0) return setError('Enter a number, 0 or more.');
    mut.mutate({
      date: todayStr(),
      value: num,
      target_value: goal.target_value,
      achieved,
      source: 'manual',
    });
  }

  return (
    <Modal title={`Log progress: ${goal.title}`} onClose={onClose}>
      <form onSubmit={onSubmit} className="space-y-4">
        <div>
          <label className={labelClass} htmlFor="p-val">
            Today's value ({unitLabel(goal.target_unit)}), target {fmt(goal.target_value)}
          </label>
          <input id="p-val" type="number" min="0" step="any" className={inputClass} value={value} onChange={(e) => setValue(e.target.value)} autoFocus />
        </div>
        <label className="flex items-center gap-2 text-sm text-foreground/80">
          <input type="checkbox" checked={achieved} onChange={(e) => setOverride(e.target.checked)} />
          Count today as achieved (adds to your streak)
        </label>
        <p className="text-xs text-muted-foreground">One entry per day. Logging again today will be rejected.</p>
        {error && (
          <div className="rounded-xl bg-red-500/10 border border-red-500/30 text-red-500 text-sm px-4 py-3" role="alert">{error}</div>
        )}
        <div className="flex justify-end gap-3 pt-2">
          <button type="button" className="btn-ghost" onClick={onClose}>Cancel</button>
          <button type="submit" className="btn-primary" disabled={mut.isPending}>
            {mut.isPending ? 'Saving...' : 'Save'}
          </button>
        </div>
      </form>
    </Modal>
  );
}