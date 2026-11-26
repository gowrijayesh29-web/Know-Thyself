'use client';

import { useMemo, useRef, useState, useEffect } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import { Sparkles, Send, Loader2, Brain, MessageSquare } from 'lucide-react';
import { cn } from '@/lib/utils';
import { api, errorMessage } from '@/lib/api';
import { inputClass } from '@/components/modal';
import { dayStr, toDate, listActivities, listNutrition, listHydration } from '@/lib/health-api';
import { listSleep } from '@/lib/sleep-api';
import { listDigital } from '@/lib/digital-api';

function localDay(iso: string): string {
  const d = new Date(iso);
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
}
function hm(min: number): string {
  const r = Math.round(min);
  return `${Math.floor(r / 60)}h${String(r % 60).padStart(2, '0')}m`;
}
const sum = (a: number[]) => a.reduce((s, x) => s + x, 0);

async function loadData() {
  const today = dayStr(0);
  const from = dayStr(-6);
  const res = await Promise.allSettled([
    listActivities(from, today),
    listNutrition(from, today),
    listHydration(from, today),
    listSleep(from, today),
    listDigital(toDate(from, '00:00').toISOString(), toDate(today, '23:59').toISOString()),
  ]);
  const pick = (r: PromiseSettledResult<any[]>): any[] => (r.status === 'fulfilled' ? r.value : []);
  return { act: pick(res[0]), nut: pick(res[1]), hyd: pick(res[2]), sleep: pick(res[3]), dig: pick(res[4]) };
}

function buildContext(d: any): string {
  const lines: string[] = [`Today is ${dayStr(0)}. Data below covers the last 7 days (oldest first).`];
  for (let i = 6; i >= 0; i--) {
    const day = dayStr(-i);
    const parts: string[] = [];
    const sl = d.sleep.find((r: any) => r.date === day);
    parts.push(sl
      ? `sleep ${hm(sl.total_sleep_minutes)} (quality ${sl.quality_rating || 'n/a'}${sl.caffeine_after_noon ? ', caffeine after noon' : ''}${sl.screen_time_before_bed_minutes != null ? `, ${sl.screen_time_before_bed_minutes} min screen before bed` : ''})`
      : 'sleep not logged');
    const wk = d.act.filter((a: any) => a.date === day);
    parts.push(wk.length ? `workouts: ${wk.map((a: any) => `${a.activity_type} ${a.duration_minutes}min`).join(', ')}` : 'no workout');
    const nt = d.nut.filter((n: any) => n.date === day);
    parts.push(nt.length ? `food ${Math.round(sum(nt.map((n: any) => n.calories || 0)))} kcal, ${Math.round(sum(nt.map((n: any) => n.protein_g || 0)))} g protein` : 'food not logged');
    const hy = d.hyd.filter((h: any) => (h.date || (h.timestamp ? localDay(h.timestamp) : '')) === day);
    parts.push(hy.length ? `water ${Math.round(sum(hy.map((h: any) => h.amount_ml || 0)))} ml` : 'water not logged');
    const dg = d.dig.filter((r: any) => localDay(r.start_time) === day);
    if (dg.length) {
      const tot = sum(dg.map((r: any) => r.active_seconds)) / 60;
      const pr = sum(dg.filter((r: any) => r.is_productive === true).map((r: any) => r.active_seconds)) / 60;
      const un = sum(dg.filter((r: any) => r.is_productive === false).map((r: any) => r.active_seconds)) / 60;
      parts.push(`screen ${hm(tot)} (productive ${hm(pr)}, unproductive ${hm(un)})`);
    } else parts.push('screen time not logged');
    lines.push(`${day}: ${parts.join('; ')}`);
  }
  return lines.join('\n');
}

type Msg = { role: 'user' | 'ai'; text: string };

const SUMMARY_Q = 'Write my weekly summary in plain text with these four parts: 1) Overall, in 2 sentences. 2) What went well, 2 short bullets. 3) What needs attention, 2 short bullets. 4) One specific action for tomorrow. Use my actual numbers and dates.';
const CHIPS = ['Why might my sleep be off?', 'How is my screen time?', 'Am I eating enough protein?', 'What should I do tomorrow?'];
const clean = (t: string) => t.replace(/\*\*/g, '').replace(/^#+\s*/gm, '');

export function AIPage() {
  const { data, isLoading } = useQuery({ queryKey: ['ai-data', dayStr(0)], queryFn: loadData });
  const context = useMemo(() => (data ? buildContext(data) : ''), [data]);
  const hasData = !!data && data.act.length + data.nut.length + data.hyd.length + data.sleep.length + data.dig.length > 0;
  const [msgs, setMsgs] = useState<Msg[]>([]);
  const [input, setInput] = useState('');
  const endRef = useRef<HTMLDivElement>(null);

  const mut = useMutation({
    mutationFn: async (q: string) => (await api.post('/ai/ask', { question: q, context, mode: 'chat' }, { timeout: 120000 })).data.answer as string,
    onSuccess: (a) => setMsgs((m) => [...m, { role: 'ai', text: a || 'The model returned an empty answer. Try again.' }]),
    onError: (e) => setMsgs((m) => [...m, { role: 'ai', text: 'Error: ' + errorMessage(e) }]),
  });

  function ask(q: string, label?: string) {
    if (!q.trim() || mut.isPending || !hasData) return;
    setMsgs((m) => [...m, { role: 'user', text: label ?? q }]);
    mut.mutate(q);
    setInput('');
  }

  useEffect(() => { endRef.current?.scrollIntoView({ behavior: 'smooth' }); }, [msgs, mut.isPending]);

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="heading-1">AI Intelligence</h1>
          <p className="body-md text-muted-foreground mt-1">Ask questions about your own logged sleep, workouts, meals, water and screen time.</p>
        </div>
        <button className="btn-primary" disabled={mut.isPending || isLoading || !hasData} onClick={() => ask(SUMMARY_Q, 'Summarise my week')}>
          <Sparkles className="w-4 h-4 mr-2" /> Summarise my week
        </button>
      </div>

      {isLoading ? (
        <div className="flex items-center justify-center py-16 text-muted-foreground"><Loader2 className="w-6 h-6 animate-spin mr-3" /> Loading your data...</div>
      ) : !hasData ? (
        <div className="glass-subtle p-8 rounded-2xl text-center">
          <Brain className="w-12 h-12 mx-auto text-muted-foreground/50 mb-4" />
          <p className="text-foreground mb-1">Nothing to analyse yet</p>
          <p className="text-sm text-muted-foreground">Log some sleep, workouts, meals or screen time first, then come back.</p>
        </div>
      ) : (
        <div className="card p-6 space-y-4">
          <div className="space-y-4 min-h-[260px] max-h-[520px] overflow-y-auto pr-1">
            {msgs.length === 0 && (
              <div className="text-center py-10">
                <MessageSquare className="w-10 h-10 mx-auto text-muted-foreground/50 mb-3" />
                <p className="text-foreground">Click Summarise my week, or ask something below.</p>
              </div>
            )}
            {msgs.map((m, i) => (
              <div key={i} className={cn('flex', m.role === 'user' ? 'justify-end' : 'justify-start')}>
                <div className={cn('max-w-[85%] rounded-2xl px-4 py-3 text-sm whitespace-pre-wrap', m.role === 'user' ? 'bg-primary-500 text-white' : 'glass-subtle text-foreground')}>
                  {m.role === 'ai' ? clean(m.text) : m.text}
                </div>
              </div>
            ))}
            {mut.isPending && (
              <div className="flex justify-start">
                <div className="glass-subtle rounded-2xl px-4 py-3 text-sm text-muted-foreground flex items-center"><Loader2 className="w-4 h-4 animate-spin mr-2" /> Thinking about your data...</div>
              </div>
            )}
            <div ref={endRef} />
          </div>

          <div className="flex flex-wrap gap-2">
            {CHIPS.map((c) => (
              <button key={c} className="btn-outline btn-sm" disabled={mut.isPending} onClick={() => ask(c)}>{c}</button>
            ))}
          </div>

          <div className="flex gap-3">
            <input className={inputClass} value={input} placeholder="Ask about your week..." onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => { if (e.key === 'Enter') ask(input); }} />
            <button className="btn-primary" disabled={mut.isPending || !input.trim()} onClick={() => ask(input)}><Send className="w-4 h-4" /></button>
          </div>

          <details className="text-sm">
            <summary className="cursor-pointer text-muted-foreground">Data the AI sees (last 7 days)</summary>
            <pre className="mt-3 p-4 glass-subtle rounded-xl text-xs text-muted-foreground whitespace-pre-wrap overflow-x-auto">{context}</pre>
          </details>
          <p className="text-xs text-muted-foreground">AI-generated from your own logs. Not medical advice.</p>
        </div>
      )}
    </div>
  );
}
