import { api } from '@/lib/api';

export interface SleepRecord {
  id: string;
  date: string;
  bedtime: string;
  sleep_start: string;
  sleep_end: string;
  wake_time: string;
  time_in_bed_minutes: number;
  total_sleep_minutes: number;
  awake_minutes?: number | null;
  sleep_latency_minutes?: number | null;
  quality_rating?: string | null;
  screen_time_before_bed_minutes?: number | null;
  caffeine_after_noon: boolean;
  alcohol_before_bed: boolean;
  exercise_before_bed: boolean;
}

function unwrap<T>(data: any): T[] {
  if (Array.isArray(data)) return data;
  return data?.items ?? data?.data ?? data?.results ?? [];
}

export async function listSleep(from: string, to: string): Promise<SleepRecord[]> {
  const res = await api.get('/physical/sleep', { params: { date_from: from, date_to: to, page: 1, page_size: 50 } });
  return unwrap<SleepRecord>(res.data);
}
export async function createSleep(payload: any): Promise<SleepRecord> {
  return (await api.post('/physical/sleep', payload)).data;
}
export async function deleteSleep(id: string): Promise<void> {
  await api.delete(`/physical/sleep/${id}`);
}