import axios from 'axios';
import { getAccessToken, clearTokens } from '@/lib/auth';

export const api = axios.create({ baseURL: '/api' });

api.interceptors.request.use((config) => {
  const token = getAccessToken();
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

api.interceptors.response.use(
  (res) => res,
  (error) => {
    if (error?.response?.status === 401 && typeof window !== 'undefined') {
      clearTokens();
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export function errorMessage(err: any, fallback = 'Something went wrong'): string {
  const data = err?.response?.data;
  if (data) {
    const parts: string[] = [];
    if (typeof data.message === 'string' && data.message) parts.push(data.message);
    if (Array.isArray(data.details)) {
      for (const d of data.details) {
        const m = d?.message || d?.msg;
        if (m) parts.push(String(m));
      }
    }
    if (Array.isArray(data.detail)) {
      for (const d of data.detail) {
        if (d?.msg) {
          const field = Array.isArray(d.loc) ? String(d.loc[d.loc.length - 1] ?? '') : '';
          parts.push(`${field} ${d.msg}`.trim());
        }
      }
    } else if (typeof data.detail === 'string') {
      parts.push(data.detail);
    }
    if (parts.length) return parts.join(' ');
  }
  if (err?.message) return err.message;
  return fallback;
}