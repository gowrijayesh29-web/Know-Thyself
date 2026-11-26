'use client';

import { useRef, useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import toast from 'react-hot-toast';
import { Sparkles, Droplets, Loader2, CheckCircle2, Undo2, ListChecks, Target, History, AlertTriangle } from 'lucide-react';
import { cn } from '@/lib/utils';
import { errorMessage } from '@/lib/api';
import { listHydration, createHydration, deleteHydration, dayStr } from '@/lib/health-api';
import { SECTIONS, weekRange, getLatestSurvey, submitSurvey, askSurveyReport } from '@/lib/survey-api';

const WATER_TARGET = 2500;
const DAYS = [0, 1, 2, 3, 4, 5, 6, 7];
const SCALE = [1, 2, 3, 4, 5];
const SCORES = [
  { k: 'nutrition_score', label: 'Nutrition' },
  { k: 'activity_score', label: 'Activity' },
  { k: 'sleep_score', label: 'Sleep' },
  { k: 'stress_score', label: 'Stress (higher = calmer)' },
  { k: 'overall_wellbeing_score', label: 'Overall' },
];

function Chip({ on, label, onClick }: { on: boolean; label: string; onClick: () => void }) {
  return (
    <button type="button" onClick={onClick}
      className={cn('px-4 py-2 rounded-xl text-sm font-medium transition-colors', on ? 'bg-primary-500 text-white' : 'glass-subtle text-foreground hover:bg-primary-500/10')}>
      {label}
    </button>
  );
}

function WaterCard() {
  const qc = useQueryClient();
  const today = dayStr(0);
  const water = useQuery({ queryKey: ['hydration', today], queryFn: () => listHydration(today, today) });
  const add = useMutation({
    mutationFn: (ml: number) => createHydration({ date: today, timestamp: new Date().toISOString(), amount_ml: ml, beverage_type: 'water' }),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['hydration'] }); },
    onError: (e) => toast.error(errorMessage(e)),
  });
  const undo = useMutation({
    mutationFn: (id: string) => deleteHydration(id),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['hydration'] }); },
    onError: (e) => toast.error(errorMessage(e)),
  });
  const items = water.data ?? [];
  const ml = items.reduce((t: number, h: any) => t + (h.amount_ml || 0), 0);
  const busy = add.isPending || undo.isPending;
  return (
    <div className="card p-6">
      <div className="flex flex-wrap items-center justify-between gap-3 mb-4">
        <h2 className="heading-5 flex items-center gap-2"><Droplets className="w-5 h-5 text-blue-500" /> Water today</h2>
        <p className="text-sm text-muted-foreground">{(ml / 1000).toFixed(2)} L of {(WATER_TARGET / 1000).toFixed(1)} L (default target)</p>
      </div>
      <div className="h-2 bg-muted-foreground/10 rounded-full overflow-hidden mb-4">
        <div className="h-full rounded-full bg-blue-500 transition-all duration-700" style={{ width: `${Math.min(100, (ml / WATER_TARGET) * 100)}%` }} />
      </div>
      <div className="flex flex-wrap items-center gap-2">
        {[250, 500, 750].map((v) => (
          <button key={v} disabled={busy} onClick={() => add.mutate(v)} className="btn-outline btn-sm">+{v} ml</button>
        ))}
        <button disabled={busy || items.length === 0} onClick={() => undo.mutate(items[0].id)} className="btn-ghost btn-sm">
          <Undo2 className="w-4 h-4 mr-1" /> Undo last
        </button>
      </div>
    </div>
  );
}

function ScoreList({ s }: { s: any }) {
  return (
    <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
      {SCORES.filter((x) => s[x.k] != null).map((x) => (
        <div key={x.k} className="glass-subtle p-4 rounded-xl text-center">
          <p className="text-xs font-medium text-foreground/60">{x.label}</p>
          <p className="text-2xl font-bold text-foreground mt-1">{Math.round(s[x.k])}<span className="text-sm text-muted-foreground">/100</span></p>
        </div>
      ))}
    </div>
  );
}

function SurveyCard() {
  const qc = useQueryClient();
  const week = weekRange();
  const latest = useQuery({ queryKey: ['survey-latest'], queryFn: getLatestSurvey, retry: false });
  const [ans, setAns] = useState<Record<string, any>>({});
  const [report, setReport] = useState<any>(null);
  const started = useRef(Date.now());
  const total = SECTIONS.reduce((t, s) => t + s.qs.length, 0);
  const answered = Object.keys(ans).length;
  const s = latest.data;
  const doneThisWeek = !!s && s.week_start === week.start;
  const sub = useMutation({
    mutationFn: () => submitSurvey(ans, Math.round((Date.now() - started.current) / 1000)),
    onSuccess: () => {
      toast.success('Survey saved');
      qc.invalidateQueries({ queryKey: ['survey-latest'] });
      qc.invalidateQueries({ queryKey: ['wellness'] });
    },
    onError: (e) => toast.error(errorMessage(e)),
  });
  const ai = useMutation({
    mutationFn: (sv: any) => askSurveyReport(sv),
    onSuccess: (t: any) => setReport(t),
    onError: (e) => toast.error(errorMessage(e)),
  });
  if (latest.isLoading) {
    return <div className="card p-6 flex items-center text-muted-foreground"><Loader2 className="w-5 h-5 animate-spin mr-3" /> Loading survey...</div>;
  }
  return (
    <div className="space-y-6">
      {s && (
        <div className="card p-6 space-y-4">
          <h2 className="heading-5 flex items-center gap-2">
            {doneThisWeek && <CheckCircle2 className="w-5 h-5 text-green-500" />}
            {doneThisWeek ? 'This week survey is done' : 'Latest survey (week of ' + s.week_start + ')'}
          </h2>
          <ScoreList s={s} />
          <p className="text-xs text-muted-foreground">Estimated from your survey answers. Rough self-reports, not measurements.</p>
          <div>
            <button className="btn-primary btn-sm" disabled={ai.isPending} onClick={() => ai.mutate(s)}>
              <Sparkles className="w-4 h-4 mr-2" /> {ai.isPending ? 'Thinking...' : report ? 'Analyse again' : 'Analyse with AI'}
            </button>
            {report && <ReportView r={report} />}
          </div>
        </div>
      )}
      {!doneThisWeek && (
        <div className="card p-6 space-y-6">
          <div>
            <h2 className="heading-5">Weekly survey ({week.start} to {week.end})</h2>
            <p className="text-sm text-muted-foreground">Tap an answer for each question. A rough idea is enough.</p>
          </div>
          {SECTIONS.map((sec) => (
            <div key={sec.title} className="space-y-4">
              <div>
                <h3 className="heading-6">{sec.title}</h3>
                <p className="text-sm text-muted-foreground">{sec.note}</p>
              </div>
              {sec.qs.map((q) => (
                <div key={q.id}>
                  <p className="text-sm text-foreground mb-2">{q.text}</p>
                  <div className="flex flex-wrap gap-2">
                    {q.kind === 'choice'
                      ? q.options!.map((o) => <Chip key={o.v} on={ans[q.id] === o.v} label={o.label} onClick={() => setAns({ ...ans, [q.id]: o.v })} />)
                      : (q.kind === 'days' ? DAYS : SCALE).map((n) => <Chip key={n} on={ans[q.id] === n} label={String(n)} onClick={() => setAns({ ...ans, [q.id]: n })} />)}
                  </div>
                </div>
              ))}
            </div>
          ))}
          <div className="flex items-center gap-4">
            <button className="btn-primary" disabled={sub.isPending || answered < total} onClick={() => sub.mutate()}>
              {sub.isPending ? 'Saving...' : 'Submit survey'}
            </button>
            <span className="text-sm text-muted-foreground">{answered} of {total} answered</span>
          </div>
        </div>
      )}
    </div>
  );
}

export function NutritionPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="heading-1">Nutrition</h1>
        <p className="body-md text-muted-foreground mt-1">Nutrition is measured with a quick weekly survey, not by logging meals. Scores are estimates from your answers.</p>
      </div>
      <WaterCard />
      <SurveyCard />
    </div>
  );
}

function ReportView({ r }: { r: any }) {
  if (r.raw) return <p className="text-sm text-foreground mt-3 whitespace-pre-line">{r.raw}</p>;
  const list = (a: any): any[] => (Array.isArray(a) ? a : []);
  return (
    <div className="mt-4 space-y-4">
      {r.headline && (
        <div className="rounded-2xl border border-primary-500/30 bg-primary-500/10 p-4">
          <p className="text-lg font-semibold text-foreground">{r.headline}</p>
        </div>
      )}
      <div className="grid md:grid-cols-2 gap-4">
        <div className="glass-subtle rounded-2xl p-4">
          <h4 className="font-semibold text-foreground mb-2 flex items-center gap-2"><ListChecks className="w-4 h-4 text-primary-500" /> What happened</h4>
          <ul className="space-y-1 text-sm text-foreground list-disc pl-5">
            {list(r.happened).map((x: string, i: number) => <li key={i}>{x}</li>)}
          </ul>
        </div>
        <div className="glass-subtle rounded-2xl p-4">
          <h4 className="font-semibold text-foreground mb-2 flex items-center gap-2"><Target className="w-4 h-4 text-green-500" /> What a good week looks like</h4>
          <p className="text-sm text-foreground">{r.should}</p>
        </div>
      </div>
      <div className="glass-subtle rounded-2xl p-4">
        <h4 className="font-semibold text-foreground mb-2 flex items-center gap-2"><History className="w-4 h-4 text-blue-500" /> Your history</h4>
        <p className="text-sm text-foreground">{r.history}</p>
      </div>
      <div className="glass-subtle rounded-2xl p-4">
        <h4 className="font-semibold text-foreground mb-3">How to fix it this week</h4>
        <div className="space-y-3">
          {list(r.fixes).map((f: any, i: number) => (
            <div key={i} className="flex gap-3">
              <div className="w-7 h-7 shrink-0 rounded-full bg-primary-500 text-white text-sm font-bold flex items-center justify-center">{i + 1}</div>
              <div>
                <p className="font-bold text-foreground">{f.title}</p>
                <p className="text-sm text-foreground">{f.detail}</p>
                {f.when && <p className="text-xs text-muted-foreground mt-0.5">When: {f.when}</p>}
              </div>
            </div>
          ))}
        </div>
      </div>
      {r.risk && (
        <div className="rounded-2xl border border-amber-500/30 bg-amber-500/10 p-4">
          <h4 className="font-semibold text-amber-500 mb-1 flex items-center gap-2"><AlertTriangle className="w-4 h-4" /> If nothing changes</h4>
          <p className="text-sm text-foreground">{r.risk}</p>
        </div>
      )}
      <p className="text-xs text-muted-foreground">Written by AI from your rough self-reports and saved survey history. General wellbeing guidance, not medical advice.</p>
    </div>
  );
}
