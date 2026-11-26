'use client';

import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { useState, useEffect, createContext, useContext, ReactNode } from 'react';
import { ThemeProvider } from 'next-themes';
import { getAccessToken, saveTokens, clearTokens, authHeaders, extractError } from '@/lib/auth';

interface ProvidersProps {
  children: ReactNode;
}

export function Providers({ children }: ProvidersProps) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: 60 * 1000, // 1 minute
            gcTime: 5 * 60 * 1000, // 5 minutes
            retry: 1,
            refetchOnWindowFocus: false,
          },
        },
      })
  );

  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider attribute="class" defaultTheme="system" enableSystem>
        {children}
        <ReactQueryDevtools initialIsOpen={false} />
      </ThemeProvider>
    </QueryClientProvider>
  );
}

// Auth context
interface AuthContextType {
  user: any | null;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (data: any) => Promise<void>;
  logout: () => Promise<void>;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

async function fetchMe(): Promise<any | null> {
  if (!getAccessToken()) return null;
  try {
    const res = await fetch('/api/auth/me', { headers: authHeaders() });
    if (res.status === 401 || res.status === 403) {
      clearTokens();
      return null;
    }
    if (!res.ok) return null;
    const data = await res.json();
    return data?.user ?? data;
  } catch (error) {
    console.error('Auth check failed:', error);
    return null;
  }
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<any | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    fetchMe().then((u) => {
      if (!cancelled) {
        setUser(u);
        setIsLoading(false);
      }
    });
    return () => {
      cancelled = true;
    };
  }, []);

  const login = async (email: string, password: string) => {
    const postJson = () =>
      fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      });
    const postForm = () =>
      fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: new URLSearchParams({ username: email, password }).toString(),
      });

    let res = await postJson();
    if (res.status === 422) {
      // some backends expect form fields (username/password) instead of JSON
      const retry = await postForm();
      if (retry.ok || retry.status !== 422) res = retry;
    }
    if (!res.ok) throw new Error(await extractError(res, 'Login failed'));
    saveTokens(await res.json());
    setUser(await fetchMe());
  };

  const register = async (data: any) => {
    const res = await fetch('/api/auth/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error(await extractError(res, 'Registration failed'));
    saveTokens(await res.json());
    setUser(await fetchMe());
  };

  const logout = async () => {
    try {
      await fetch('/api/auth/logout', { method: 'POST', headers: authHeaders() });
    } catch {}
    clearTokens();
    setUser(null);
  };

  const refreshUser = async () => {
    setUser(await fetchMe());
  };

  return (
    <AuthContext.Provider value={{ user, isLoading, login, register, logout, refreshUser }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}