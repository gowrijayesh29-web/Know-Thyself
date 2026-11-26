import { api } from '@/lib/api';

export interface StepDay { date: string; steps: number; source?: string }

export async function importSteps(items: StepDay[]): Promise<any> {
  return (await api.post('/physical/steps/import', { items })).data;
}

export async function listSteps(from: string, to: string): Promise<StepDay[]> {
  const r = await api.get('/physical/steps', { params: { date_from: from, date_to: to } });
  return Array.isArray(r.data) ? r.data : r.data?.items ?? [];
}
