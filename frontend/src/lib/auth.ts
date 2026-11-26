const ACCESS = 'kt_access_token';
const REFRESH = 'kt_refresh_token';

export function getAccessToken(): string | null {
  try {
    return typeof window === 'undefined' ? null : window.localStorage.getItem(ACCESS);
  } catch {
    return null;
  }
}

export function saveTokens(t: { access_token?: string; refresh_token?: string }) {
  try {
    if (t.access_token) window.localStorage.setItem(ACCESS, t.access_token);
    if (t.refresh_token) window.localStorage.setItem(REFRESH, t.refresh_token);
  } catch {}
}

export function clearTokens() {
  try {
    window.localStorage.removeItem(ACCESS);
    window.localStorage.removeItem(REFRESH);
  } catch {}
}

export function authHeaders(extra: Record<string, string> = {}): Record<string, string> {
  const token = getAccessToken();
  return token ? { ...extra, Authorization: `Bearer ${token}` } : extra;
}

export async function extractError(res: Response, fallback: string): Promise<string> {
  try {
    const body = await res.json();
    const parts: string[] = [];
    if (typeof body?.message === 'string' && body.message) parts.push(body.message);
    if (Array.isArray(body?.details)) {
      for (const d of body.details) {
        const m = d?.message || d?.msg;
        if (m) parts.push(String(m));
      }
    }
    if (Array.isArray(body?.detail)) {
      for (const d of body.detail) if (d?.msg) parts.push(String(d.msg));
    } else if (typeof body?.detail === 'string') {
      parts.push(body.detail);
    }
    if (parts.length) return parts.join(' ');
  } catch {}
  return fallback;
}