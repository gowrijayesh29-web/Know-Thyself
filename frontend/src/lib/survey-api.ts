import { api } from '@/lib/api';

export const SURVEY_VERSION = 'v1';

export interface SurveyQ {
  id: string;
  text: string;
  kind: 'days' | 'scale' | 'choice';
  options?: { v: string; label: string }[];
}

export const SECTIONS: { title: string; note: string; qs: SurveyQ[] }[] = [
  {
    title: 'Food this week',
    note: 'A rough idea is enough. No calories or amounts to look up.',
    qs: [
      { id: 'fruit_days', kind: 'days', text: 'On how many days did you eat fruit?' },
      { id: 'veg_days', kind: 'days', text: 'On how many days did you eat vegetables or salad?' },
      { id: 'protein_days', kind: 'days', text: 'On how many days did you eat a protein food (dal, eggs, paneer, chicken, fish, sprouts)?' },
      { id: 'oily_days', kind: 'days', text: 'On how many days did you eat fried or very oily food?' },
      { id: 'sugary_days', kind: 'days', text: 'On how many days did you have sweets or sugary drinks?' },
      { id: 'skipped_days', kind: 'days', text: 'On how many days did you skip a main meal?' },
      { id: 'water', kind: 'choice', text: 'How much water did you drink on a typical day?', options: [
        { v: 'low', label: 'Under 1.5 L' }, { v: 'ok', label: '1.5 to 2.5 L' }, { v: 'good', label: 'More than 2.5 L' },
      ] },
    ],
  },
  {
    title: 'Body and mind',
    note: 'Your own feeling is what we want here.',
    qs: [
      { id: 'exercise_days', kind: 'days', text: 'On how many days did you exercise or play a sport?' },
      { id: 'sleep_quality', kind: 'scale', text: 'How well did you sleep overall? (1 = very badly, 5 = very well)' },
      { id: 'stress', kind: 'scale', text: 'How stressed did you feel? (1 = very little, 5 = very stressed)' },
      { id: 'energy', kind: 'scale', text: 'How was your energy during the day? (1 = very low, 5 = very high)' },
    ],
  },
];

function pad(n: number) { return String(n).padStart(2, '0'); }
function iso(d: Date) { return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`; }

export function weekRange(ref: Date = new Date()) {
  const d = new Date(ref.getFullYear(), ref.getMonth(), ref.getDate());
  d.setDate(d.getDate() - ((d.getDay() + 6) % 7));
  const start = iso(d);
  d.setDate(d.getDate() + 6);
  return { start, end: iso(d) };
}

export async function getLatestSurvey(): Promise<any | null> {
  return (await api.get('/knowledge/surveys/weekly/latest')).data ?? null;
}

export async function submitSurvey(responses: Record<string, any>, seconds: number): Promise<any> {
  const w = weekRange();
  return (await api.post('/knowledge/surveys/weekly', {
    week_start: w.start, week_end: w.end, survey_version: SURVEY_VERSION,
    responses, completion_time_seconds: seconds, is_complete: true, skipped_sections: [],
  })).data;
}

export function surveyContext(s: any): string {
  const r = s.responses || {};
  const lines: string[] = [];
  SECTIONS.forEach((sec) => sec.qs.forEach((q) => {
    const a = r[q.id];
    if (a === undefined) return;
    const opt = q.options?.find((o) => o.v === a);
    lines.push(`${q.text} -> ${opt ? opt.label : a}${q.kind === 'days' ? ' of 7 days' : ''}`);
  }));
  const sc = ['nutrition_score', 'activity_score', 'sleep_score', 'stress_score', 'overall_wellbeing_score']
    .filter((k) => s[k] != null).map((k) => `${k.replace('_wellbeing', '').replace('_score', '')} ${Math.round(s[k])}/100`);
  return `Weekly self-reported survey for ${s.week_start} to ${s.week_end}. These are rough self-reports, not measurements, and there is no calorie data. For the stress score, higher means calmer.\n` + lines.join('\n') + `\nScores (0-100, higher is better): ${sc.join(', ')}.`;
}

export async function askSurveyAI(s: any): Promise<string> {
  const r = await api.post('/ai/ask', {
    question: 'Analyse my weekly lifestyle survey. Name my strongest area, my weakest area, and give one action for next week.',
    context: surveyContext(s), mode: 'chat',
  }, { timeout: 120000 });
  return r.data.answer;
}

export async function listSurveys(): Promise<any[]> {
  const res = await api.get('/knowledge/surveys/weekly', { params: { page: 1, page_size: 20 } });
  const d = res.data;
  return Array.isArray(d) ? d : d?.items ?? d?.data ?? d?.results ?? [];
}

function brief(s: any): string {
  const r = s.responses || {};
  const sc = ['nutrition_score', 'activity_score', 'sleep_score', 'stress_score', 'overall_wellbeing_score']
    .filter((k) => s[k] != null).map((k) => `${k.replace('_wellbeing', '').replace('_score', '')} ${Math.round(s[k])}`).join(', ');
  const ans = Object.keys(r).map((k) => `${k}=${r[k]}`).join(', ');
  return `Week ${s.week_start}: scores ${sc}. Answers: ${ans}.`;
}

export async function askSurveyReport(s: any): Promise<any> {
  let prev: any[] = [];
  try {
    prev = (await listSurveys()).filter((x: any) => x.week_start !== s.week_start)
      .sort((a: any, b: any) => (a.week_start < b.week_start ? 1 : -1)).slice(0, 4);
  } catch {}
  const history = prev.length ? prev.map(brief).join('\n') : 'NONE. This is the first survey on record.';
  const question = 'Write a structured report on my weekly lifestyle survey. Reply with ONLY a JSON object (no markdown, no code fences) with exactly these keys: '
    + 'headline (one punchy sentence), '
    + 'happened (array of 3 to 4 short strings, each citing my actual answers or scores with numbers), '
    + 'should (one or two sentences on what a healthy week looks like for my weak areas, general guidance), '
    + 'history (one or two sentences comparing with the previous weeks in HISTORY, or say plainly that this is the first survey so there is no history yet), '
    + 'fixes (array of exactly 3 objects with keys title (3 to 6 words, imperative), detail (one concrete action with numbers), when (when to do it)), '
    + 'risk (one or two sentences on what is likely to happen over the coming weeks if nothing changes, general and not a medical diagnosis). '
    + 'Use only the data given. Do not invent numbers. Plain language, no emojis.';
  const r = await api.post('/ai/ask', {
    question, context: surveyContext(s) + '\nHISTORY (previous weeks, newest first):\n' + history, mode: 'chat',
  }, { timeout: 120000 });
  const txt: string = r.data.answer || '';
  const a = txt.indexOf('{');
  const b = txt.lastIndexOf('}');
  if (a >= 0 && b > a) {
    try { return JSON.parse(txt.slice(a, b + 1)); } catch {}
  }
  return { raw: txt };
}
