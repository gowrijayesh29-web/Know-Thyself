import { api } from '@/lib/api';

export interface Goal {
  id: string;
  title: string;
  description?: string | null;
  category: string;
  frequency: string;
  status: string;
  target_value: number;
  target_unit: string;
  current_value: number;
  progress_percentage: number;
  streak_days: number;
  priority: number;
  start_date: string;
  end_date?: string | null;
}

export const CATEGORIES = [
  { id: 'digital_wellbeing', label: 'Digital' },
  { id: 'physical_activity', label: 'Activity' },
  { id: 'nutrition', label: 'Nutrition' },
  { id: 'sleep', label: 'Sleep' },
  { id: 'hydration', label: 'Hydration' },
  { id: 'study', label: 'Study' },
  { id: 'work', label: 'Work' },
  { id: 'mental_wellbeing', label: 'Mental' },
  { id: 'personal_routine', label: 'Routine' },
  { id: 'general_lifestyle', label: 'Lifestyle' },
];

export const UNITS = [
  'minutes', 'hours', 'count', 'steps', 'calories', 'grams',
  'milliliters', 'liters', 'kg', 'percentage', 'score', 'boolean',
];

export const FREQUENCIES = ['daily', 'weekly', 'monthly'];

export function todayStr(): string {
  const d = new Date();
  const m = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  return `${d.getFullYear()}-${m}-${day}`;
}

function unwrapList(data: any): Goal[] {
  if (Array.isArray(data)) return data;
  return data?.items ?? data?.data ?? data?.results ?? [];
}

export async function listGoals(): Promise<Goal[]> {
  const res = await api.get('/goals', { params: { page: 1, page_size: 50 } });
  return unwrapList(res.data);
}

export async function createGoal(payload: any): Promise<Goal> {
  const res = await api.post('/goals', payload);
  return res.data;
}

export async function updateGoal(id: string, payload: any): Promise<Goal> {
  const res = await api.put(`/goals/${id}`, payload);
  return res.data;
}

export async function deleteGoal(id: string): Promise<void> {
  await api.delete(`/goals/${id}`);
}

export async function logProgress(id: string, payload: any): Promise<any> {
  const res = await api.post(`/goals/${id}/progress`, payload);
  return res.data;
}