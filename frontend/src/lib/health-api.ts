import { api } from '@/lib/api';

export function dayStr(offset = 0): string {
  const d = new Date();
  d.setDate(d.getDate() + offset);
  const m = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  return `${d.getFullYear()}-${m}-${day}`;
}

export function nowTime(): string {
  const d = new Date();
  return `${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`;
}

export function toDate(date: string, time: string): Date {
  return new Date(`${date}T${time}:00`);
}

function unwrap<T>(data: any): T[] {
  if (Array.isArray(data)) return data;
  return data?.items ?? data?.data ?? data?.results ?? [];
}

export interface ActivityRecord {
  id: string;
  date: string;
  activity_type: string;
  start_time: string;
  end_time: string;
  duration_minutes: number;
  intensity?: string | null;
  calories_burned?: number | null;
  distance_km?: number | null;
  steps?: number | null;
  notes?: string | null;
}

export interface NutritionRecord {
  id: string;
  date: string;
  meal_type: string;
  timestamp: string;
  food_name: string;
  quantity: number;
  unit: string;
  calories?: number | null;
  protein_g?: number | null;
  carbs_g?: number | null;
  fat_g?: number | null;
  fiber_g?: number | null;
}

export interface HydrationRecord {
  id: string;
  date: string;
  timestamp: string;
  amount_ml: number;
  beverage_type: string;
}

const range = (from: string, to: string) => ({ date_from: from, date_to: to, page: 1, page_size: 50 });

export async function listActivities(from: string, to: string): Promise<ActivityRecord[]> {
  const res = await api.get('/physical/activity', { params: range(from, to) });
  return unwrap<ActivityRecord>(res.data);
}
export async function createActivity(payload: any): Promise<ActivityRecord> {
  return (await api.post('/physical/activity', payload)).data;
}
export async function deleteActivity(id: string): Promise<void> {
  await api.delete(`/physical/activity/${id}`);
}

export async function listNutrition(from: string, to: string): Promise<NutritionRecord[]> {
  const res = await api.get('/physical/nutrition', { params: range(from, to) });
  return unwrap<NutritionRecord>(res.data);
}
export async function createNutrition(payload: any): Promise<NutritionRecord> {
  return (await api.post('/physical/nutrition', payload)).data;
}
export async function deleteNutrition(id: string): Promise<void> {
  await api.delete(`/physical/nutrition/${id}`);
}

export async function listHydration(from: string, to: string): Promise<HydrationRecord[]> {
  const res = await api.get('/physical/hydration', { params: range(from, to) });
  return unwrap<HydrationRecord>(res.data);
}
export async function createHydration(payload: any): Promise<HydrationRecord> {
  return (await api.post('/physical/hydration', payload)).data;
}
export async function deleteHydration(id: string): Promise<void> {
  await api.delete(`/physical/hydration/${id}`);
}