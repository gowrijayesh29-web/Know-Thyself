import { api } from '@/lib/api';

export interface DigitalRecord {
  id: string;
  domain: string;
  title?: string | null;
  category: string;
  is_productive?: boolean | null;
  start_time: string;
  end_time: string;
  duration_seconds: number;
  active_seconds: number;
}

function unwrap<T>(data: any): T[] {
  if (Array.isArray(data)) return data;
  return data?.items ?? data?.data ?? data?.results ?? [];
}

export async function listDigital(fromIso: string, toIso: string): Promise<DigitalRecord[]> {
  const out: DigitalRecord[] = [];
  for (let page = 1; page <= 10; page++) {
    const res = await api.get('/digital/activities', {
      params: { start_time_from: fromIso, start_time_to: toIso, page, page_size: 50 },
    });
    const items = unwrap<DigitalRecord>(res.data);
    out.push(...items);
    if (items.length < 50) break;
  }
  return out;
}
export async function createDigital(payload: any): Promise<DigitalRecord> {
  return (await api.post('/digital/activities', payload)).data;
}
export async function deleteDigital(id: string): Promise<void> {
  await api.delete(`/digital/activities/${id}`);
}
export async function analyzeDigital(): Promise<{ classified: any[]; remaining: number; stats: any; insight: any; message?: string }> {
  const c = (await api.post('/digital/ai/classify', null, { timeout: 150000 })).data;
  const tz = -new Date().getTimezoneOffset();
  const i = (await api.post('/digital/ai/insights', null, { params: { tz_offset: tz }, timeout: 150000 })).data;
  return { classified: c.classified || [], remaining: c.remaining || 0, stats: i.stats, insight: i.insight, message: i.message };
}
