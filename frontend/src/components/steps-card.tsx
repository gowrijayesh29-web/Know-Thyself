'use client';
import { useRef } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import toast from 'react-hot-toast';
import { Footprints, Upload, Loader2 } from 'lucide-react';
import { cn } from '@/lib/utils';
import { errorMessage } from '@/lib/api';
import { dayStr } from '@/lib/health-api';
import { importSteps, listSteps, StepDay } from '@/lib/steps-api';

function splitCsv(line: string): string[] {
  const out: string[] = [];
  let cur = '';
  let q = false;
  for (const ch of line) {
    if (ch === '"') q = !q;
    else if (ch === ',' && !q) { out.push(cur); cur = ''; }
    else cur += ch;
  }
  out.push(cur);
  return out;
}

function parseExport(text: string): StepDay[] {
  const lines = text.replace(/^\uFEFF/, '').split(/\r?\n/).filter((l) => l.trim());
  if (lines.length < 2) return [];
  const head = splitCsv(lines[0]);
  const di = head.findIndex((h) => h.trim().startsWith('Date'));
  const si = head.findIndex((h) => h.trim().startsWith('Step Count'));
  if (di < 0 || si < 0) return [];
  const out: StepDay[] = [];
  for (const l of lines.slice(1)) {
    const c = splitCsv(l);
    const d = (c[di] || '').trim().slice(0, 10);
    const n = Math.round(Number(c[si]));
    if (/^\d{4}-\d{2}-\d{2}$/.test(d) && (c[si] || '').trim() !== '' && Number.isFinite(n) && n >= 0) out.push({ date: d, steps: n, source: 'apple_health_export' });
  }
  return out;
}

export function StepsCard() {
  const qc = useQueryClient();
  const input = useRef<HTMLInputElement>(null);
  const to = dayStr(0);
  const q = useQuery({ queryKey: ['steps', to], queryFn: () => listSteps(dayStr(-13), to) });
  const imp = useMutation({
    mutationFn: async (file: File) => {
      const text = await file.text();
      const rows = parseExport(text);
      if (!rows.length) throw new Error('No step rows found in ' + file.name + ' (' + text.length + ' characters). First line: ' + text.slice(0, 70));
      await importSteps(rows);
      return rows.length;
    },
    onSuccess: (n: number) => { toast.success('Imported ' + n + ' days of steps'); qc.invalidateQueries({ queryKey: ['steps'] }); },
    onError: (e) => toast.error(errorMessage(e)),
  });
  const days = (q.data ?? []).slice().sort((a, b) => (a.date < b.date ? -1 : 1)).slice(-7);
  const max = Math.max(10000, ...days.map((d) => d.steps));
  const avg = days.length ? Math.round(days.reduce((t, d) => t + d.steps, 0) / days.length) : 0;
  return (
    <div className="card p-6">
      <div className="flex flex-wrap items-center justify-between gap-3 mb-4">
        <div>
          <h2 className="heading-5 flex items-center gap-2"><Footprints className="w-5 h-5 text-primary-500" /> Daily steps</h2>
          <p className="text-sm text-muted-foreground">From your iPhone Health export. Default target: 10,000 a day.</p>
        </div>
        <div>
          <input ref={input} type="file" accept=".csv,text/csv" className="hidden"
            onChange={(e) => { const f = e.target.files?.[0]; if (f) imp.mutate(f); e.target.value = ''; }} />
          <button className="btn-primary btn-sm" disabled={imp.isPending} onClick={() => input.current?.click()}>
            {imp.isPending ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Upload className="w-4 h-4 mr-2" />} Import iPhone export (CSV)
          </button>
        </div>
      </div>
      {q.isLoading ? (
        <div className="flex items-center text-muted-foreground"><Loader2 className="w-5 h-5 animate-spin mr-3" /> Loading steps...</div>
      ) : days.length === 0 ? (
        <p className="text-sm text-muted-foreground">No steps imported yet. In Health Auto Export, export Step Count as CSV, unzip it, and choose the CSV here.</p>
      ) : (
        <div className="space-y-3">
          <p className="text-sm text-foreground">Average over {days.length} day{days.length > 1 ? 's' : ''}: <span className="font-semibold">{avg.toLocaleString()}</span> steps</p>
          <div className="space-y-2">
            {days.map((d) => (
              <div key={d.date} className="flex items-center gap-3 text-sm">
                <span className="w-14 text-muted-foreground">{d.date.slice(5)}</span>
                <div className="flex-1 h-3 bg-muted-foreground/10 rounded-full overflow-hidden">
                  <div className={cn('h-full rounded-full', d.steps >= 10000 ? 'bg-green-500' : 'bg-primary-500')} style={{ width: Math.min(100, (d.steps / max) * 100) + '%' }} />
                </div>
                <span className="w-16 text-right text-foreground">{d.steps.toLocaleString()}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
