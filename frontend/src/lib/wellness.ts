import { api } from '@/lib/api';
import { dayStr, toDate, listActivities } from '@/lib/health-api';
import { listSleep } from '@/lib/sleep-api';
import { listDigital } from '@/lib/digital-api';
import { listSurveys } from '@/lib/survey-api';

export const WEIGHTS = { sleep: 0.2, activity: 0.3, nutrition: 0.3, digital: 0.2 } as const;
export type Key = keyof typeof WEIGHTS;
export const KEYS: Key[] = ['sleep', 'activity', 'nutrition', 'digital'];
export const LABEL: Record<Key, string> = { sleep: 'Sleep', activity: 'Physical activity', nutrition: 'Nutrition', digital: 'Digital wellness' };
export interface Ind { score: number; detail: string }
export type Window = Partial<Record<Key, Ind>>;
export interface RawData { act: any[]; sleep: any[]; dig: any[]; surveys: any[] }
export interface Row { key: Key; from: number; to: number; points: number; fromDetail: string; toDetail: string }

const sum = (a: number[]) => a.reduce((s, x) => s + x, 0);
const hm = (m: number) => `${Math.floor(Math.round(m) / 60)}h ${Math.round(m) % 60}m`;
const dayOf = (iso: string) => {
  const d = new Date(iso);
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
};

export async function loadWellnessData(): Promise<RawData> {
  const today = dayStr(0);
  const res = await Promise.allSettled([
    listActivities(dayStr(-13), today),
    listSleep(dayStr(-13), today),
    listDigital(toDate(dayStr(-13), '00:00').toISOString(), toDate(today, '23:59').toISOString()),
    listSurveys(),
  ]);
  const pick = (r: PromiseSettledResult<any[]>): any[] => (r.status === 'fulfilled' ? r.value : []);
  return { act: pick(res[0]), sleep: pick(res[1]), dig: pick(res[2]), surveys: pick(res[3]) };
}

function sleepScore(m: number): number {
  if (m < 420) return (m / 420) * 100;
  if (m > 540) return Math.max(70, 100 - ((m - 540) / 60) * 15);
  return 100;
}

export function computeWindow(d: RawData, from: string, to: string): Window {
  const w: Window = {};
  const sl = d.sleep.filter((r: any) => r.date >= from && r.date <= to);
  if (sl.length) {
    const avg = sum(sl.map((r: any) => r.total_sleep_minutes)) / sl.length;
    w.sleep = { score: sum(sl.map((r: any) => sleepScore(r.total_sleep_minutes))) / sl.length, detail: `avg ${hm(avg)} over ${sl.length} night${sl.length > 1 ? 's' : ''}` };
  }
  const ac = d.act.filter((a: any) => a.date >= from && a.date <= to);
  if (ac.length) {
    const min = sum(ac.map((a: any) => a.duration_minutes || 0));
    const days = new Set(ac.map((a: any) => a.date)).size;
    w.activity = { score: (0.7 * Math.min(min / 150, 1) + 0.3 * Math.min(days / 4, 1)) * 100, detail: `${min} active min on ${days} day${days > 1 ? 's' : ''}` };
  }
  const dg = d.dig.filter((r: any) => { const k = dayOf(r.start_time); return k >= from && k <= to; });
  if (dg.length) {
    const days = new Set(dg.map((r: any) => dayOf(r.start_time))).size;
    const avgMin = sum(dg.map((r: any) => r.active_seconds)) / 60 / days;
    const prod = sum(dg.filter((r: any) => r.is_productive === true).map((r: any) => r.active_seconds));
    const unprod = sum(dg.filter((r: any) => r.is_productive === false).map((r: any) => r.active_seconds));
    const late = sum(dg.filter((r: any) => { const h = new Date(r.start_time).getHours(); return h >= 23 || h < 5; }).map((r: any) => r.active_seconds)) / 60 / days;
    const parts: number[][] = [[avgMin <= 360 ? 1 : Math.max(0, 1 - (avgMin - 360) / 240), 0.3], [Math.max(0, 1 - late / 60), 0.2]];
    if (prod + unprod > 0) parts.push([prod / (prod + unprod), 0.5]);
    const score = (sum(parts.map(([s, wt]) => s * wt)) / sum(parts.map(([, wt]) => wt))) * 100;
    w.digital = { score, detail: `${hm(avgMin)}/day screen time` + (prod + unprod > 0 ? `, ${Math.round((prod / (prod + unprod)) * 100)}% productive` : '') + (late >= 1 ? `, ${Math.round(late)} min/day after 11pm` : '') };
  }
  const sv = d.surveys.find((s: any) => s.week_start >= from && s.week_start <= to && s.nutrition_score != null);
  if (sv) w.nutrition = { score: sv.nutrition_score, detail: 'from your weekly survey' };
  return w;
}

export function overall(w: Window): number | null {
  const ks = KEYS.filter((k) => w[k]);
  if (!ks.length) return null;
  return sum(ks.map((k) => w[k]!.score * WEIGHTS[k])) / sum(ks.map((k) => WEIGHTS[k]));
}

export function compare(cur: Window, prev: Window): { rows: Row[]; delta: number } | null {
  const ks = KEYS.filter((k) => cur[k] && prev[k]);
  if (!ks.length) return null;
  const tw = sum(ks.map((k) => WEIGHTS[k]));
  const rows: Row[] = ks.map((k) => ({ key: k, from: prev[k]!.score, to: cur[k]!.score, points: ((cur[k]!.score - prev[k]!.score) * WEIGHTS[k]) / tw, fromDetail: prev[k]!.detail, toDetail: cur[k]!.detail })).sort((a, b) => b.points - a.points);
  return { rows, delta: sum(rows.map((r) => r.points)) };
}

export async function explainScore(cur: Window, prev: Window, cmp: { rows: Row[]; delta: number } | null): Promise<string> {
  const line = (w: Window) => KEYS.map((k) => (w[k] ? `${LABEL[k]} (weight ${Math.round(WEIGHTS[k] * 100)}%): ${Math.round(w[k]!.score)}/100, ${w[k]!.detail}` : `${LABEL[k]}: no data`)).join('\n');
  const ch = cmp ? cmp.rows.map((r) => `${LABEL[r.key]}: ${Math.round(r.from)} to ${Math.round(r.to)} = ${r.points >= 0 ? '+' : ''}${r.points.toFixed(1)} points on the overall score`).join('\n') : 'No earlier week to compare.';
  const context = `Wellness score = weighted average of four 0-100 indicator scores (sleep 20%, physical activity 30%, nutrition 30%, digital wellness 20%). Indicators with no data are left out and the weights re-balanced. Scores are estimates from tracked and self-reported data.\nLAST 7 DAYS:\n${line(cur)}\nPREVIOUS 7 DAYS:\n${line(prev)}\nCHANGE CONTRIBUTIONS:\n${ch}`;
  const r = await api.post('/ai/ask', { question: 'Explain my wellness score and what changed versus the previous week. Say which habit helped most and which held me back, and give one action for tomorrow.', context, mode: 'chat' }, { timeout: 120000 });
  return r.data.answer;
}
