'use client';
import { useMemo, useState } from 'react';
import { useMutation, useQuery } from '@tanstack/react-query';
import toast from 'react-hot-toast';
import { Sparkles, TrendingUp, TrendingDown, Loader2 } from 'lucide-react';
import { cn } from '@/lib/utils';
import { errorMessage } from '@/lib/api';
import { dayStr } from '@/lib/health-api';
import { WEIGHTS, KEYS, LABEL, loadWellnessData, computeWindow, overall, compare, explainScore } from '@/lib/wellness';

function Ring({ value }: { value: number }) {
  const color = value < 50 ? 'text-red-500' : value < 75 ? 'text-yellow-500' : 'text-green-500';
  return (
    <div className="relative w-36 h-36 shrink-0">
      <svg viewBox="0 0 120 120" className="w-full h-full -rotate-90">
        <circle cx="60" cy="60" r="52" fill="none" stroke="currentColor" strokeWidth="10" className="text-muted-foreground/10" />
        <circle cx="60" cy="60" r="52" fill="none" stroke="currentColor" strokeWidth="10" strokeLinecap="round" className={color} strokeDasharray={327} strokeDashoffset={327 - (value / 100) * 327} />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className="text-4xl font-bold text-foreground">{Math.round(value)}</span>
        <span className="text-xs text-muted-foreground">out of 100</span>
      </div>
    </div>
  );
}

export function WellnessScore() {
  const today = dayStr(0);
  const { data, isLoading } = useQuery({ queryKey: ['wellness', today], queryFn: loadWellnessData });
  const [text, setText] = useState('');
  const m = useMemo(() => {
    if (!data) return null;
    const cur = computeWindow(data, dayStr(-6), today);
    const prev = computeWindow(data, dayStr(-13), dayStr(-7));
    const cmp = compare(cur, prev);
    const top = cmp && cmp.rows[0].points > 0 ? cmp.rows[0] : null;
    const low = cmp ? [...cmp.rows].reverse().find((r) => r.points < 0) ?? null : null;
    return { cur, prev, now: overall(cur), cmp, top, low };
  }, [data, today]);
  const ai = useMutation({
    mutationFn: () => explainScore(m!.cur, m!.prev, m!.cmp),
    onSuccess: (t: string) => setText(t),
    onError: (e) => toast.error(errorMessage(e)),
  });
  return (
    <div className="card p-6">
      <h2 className="heading-5">Wellness score</h2>
      <p className="text-sm text-muted-foreground mb-6">Last 7 days. Sleep 20%, Activity 30%, Nutrition 30%, Digital 20%.</p>
      {isLoading || !m ? (
        <div className="flex items-center text-muted-foreground"><Loader2 className="w-5 h-5 animate-spin mr-3" /> Calculating...</div>
      ) : m.now == null ? (
        <p className="text-sm text-muted-foreground">Not enough data yet. Sleep, workouts, screen time or the weekly survey will fill this in.</p>
      ) : (
        <div className="space-y-6">
          <div className="flex flex-col md:flex-row gap-6 md:items-center">
            <Ring value={m.now} />
            <div className="flex-1 space-y-3">
              {KEYS.map((k) => {
                const ind = m.cur[k];
                return (
                  <div key={k}>
                    <div className="flex justify-between text-sm mb-1">
                      <span className="text-foreground">{LABEL[k]} <span className="text-muted-foreground">({Math.round(WEIGHTS[k] * 100)}%)</span></span>
                      <span className="text-muted-foreground">{ind ? `${Math.round(ind.score)}/100` : 'no data this week'}</span>
                    </div>
                    <div className="h-2 bg-muted-foreground/10 rounded-full overflow-hidden">
                      <div className="h-full rounded-full bg-primary-500 transition-all duration-700" style={{ width: `${ind ? Math.round(ind.score) : 0}%` }} />
                    </div>
                    {ind && <p className="text-xs text-muted-foreground mt-1">{ind.detail}</p>}
                  </div>
                );
              })}
            </div>
          </div>
          <div className="glass-subtle rounded-2xl p-4">
            <h3 className="heading-6 mb-3">Compared with the previous 7 days</h3>
            {!m.cmp ? (
              <p className="text-sm text-muted-foreground">No earlier week with matching data to compare yet.</p>
            ) : (
              <div className="space-y-2">
                <p className={cn('flex items-center gap-2 font-semibold', m.cmp.delta >= 0 ? 'text-green-500' : 'text-red-500')}>
                  {m.cmp.delta >= 0 ? <TrendingUp className="w-5 h-5" /> : <TrendingDown className="w-5 h-5" />}
                  {m.cmp.delta >= 0 ? '+' : ''}{m.cmp.delta.toFixed(1)} points ({m.cmp.rows.length} shared indicator{m.cmp.rows.length > 1 ? 's' : ''})
                </p>
                {m.cmp.rows.map((r) => (
                  <div key={r.key} className="flex justify-between text-sm">
                    <span className="text-foreground">{LABEL[r.key]}: {Math.round(r.from)} to {Math.round(r.to)}</span>
                    <span className={cn('font-medium', r.points >= 0 ? 'text-green-500' : 'text-red-500')}>{r.points >= 0 ? '+' : ''}{r.points.toFixed(1)} pts</span>
                  </div>
                ))}
                <p className="text-sm text-foreground pt-1">
                  {m.top ? `Biggest improvement: ${LABEL[m.top.key]} (${m.top.toDetail}). ` : 'No habit improved versus the previous 7 days. '}
                  {m.low ? `Held you back most: ${LABEL[m.low.key]} (${m.low.toDetail}).` : ''}
                </p>
              </div>
            )}
          </div>
          <div>
            <button className="btn-primary btn-sm" disabled={ai.isPending} onClick={() => ai.mutate()}>
              <Sparkles className="w-4 h-4 mr-2" /> {ai.isPending ? 'Thinking...' : text ? 'Explain again' : 'Explain with AI'}
            </button>
            {text && <p className="text-sm text-foreground mt-3 whitespace-pre-line">{text}</p>}
          </div>
          <p className="text-xs text-muted-foreground">Indicators with no data are left out and the other weights are re-balanced. Scores are estimates from tracked and self-reported data.</p>
        </div>
      )}
    </div>
  );
}
