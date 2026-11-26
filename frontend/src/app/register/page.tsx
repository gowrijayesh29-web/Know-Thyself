'use client';

import { useEffect, useState, FormEvent } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { AuthProvider, useAuth } from '@/components/providers';

const inputClass =
  'w-full px-4 py-2.5 glass-subtle rounded-xl text-sm text-foreground placeholder:text-muted-foreground/50 focus:outline-none focus:ring-2 focus:ring-primary-500/40 transition-all';

function RegisterForm() {
  const router = useRouter();
  const { user, isLoading, register } = useAuth();
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirm, setConfirm] = useState('');
  const [accepted, setAccepted] = useState(false);
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    if (!isLoading && user) router.replace('/');
  }, [isLoading, user, router]);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setError('');
    if (password.length < 8) return setError('Password must be at least 8 characters.');
    if (password !== confirm) return setError('The two passwords do not match.');
    if (!accepted) return setError('Please accept the terms to continue.');

    let timezone = 'UTC';
    try {
      timezone = Intl.DateTimeFormat().resolvedOptions().timeZone || 'UTC';
    } catch {}

    const payload = {
      email: email.trim(),
      password,
      full_name: fullName.trim(),
      timezone,
      locale: 'en',
      accept_terms: true,
      marketing_consent: false,
    };

    setBusy(true);
    try {
      try {
        await register(payload);
      } catch (err: any) {
        if (/timezone/i.test(err?.message || '') && timezone !== 'UTC') {
          await register({ ...payload, timezone: 'UTC' });
        } else {
          throw err;
        }
      }
      router.replace('/');
    } catch (err: any) {
      setError(err?.message || 'Registration failed');
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-background-light dark:bg-background-dark p-4">
      <div className="w-full max-w-md glass-strong rounded-3xl p-8">
        <div className="text-center mb-8">
          <div className="w-12 h-12 mx-auto mb-4 rounded-2xl bg-gradient-to-br from-primary-500 to-secondary-500" />
          <h1 className="text-2xl font-bold text-foreground">Create your account</h1>
          <p className="text-sm text-muted-foreground mt-1">Start getting to know yourself</p>
        </div>
        <form onSubmit={onSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-foreground/80 mb-1.5" htmlFor="name">Full name</label>
            <input id="name" type="text" required value={fullName} onChange={(e) => setFullName(e.target.value)} className={inputClass} placeholder="Your name" autoComplete="name" />
          </div>
          <div>
            <label className="block text-sm font-medium text-foreground/80 mb-1.5" htmlFor="email">Email</label>
            <input id="email" type="email" required value={email} onChange={(e) => setEmail(e.target.value)} className={inputClass} placeholder="you@example.com" autoComplete="email" />
          </div>
          <div>
            <label className="block text-sm font-medium text-foreground/80 mb-1.5" htmlFor="password">Password</label>
            <input id="password" type="password" required minLength={8} value={password} onChange={(e) => setPassword(e.target.value)} className={inputClass} placeholder="At least 8 characters" autoComplete="new-password" />
          </div>
          <div>
            <label className="block text-sm font-medium text-foreground/80 mb-1.5" htmlFor="confirm">Confirm password</label>
            <input id="confirm" type="password" required value={confirm} onChange={(e) => setConfirm(e.target.value)} className={inputClass} placeholder="Repeat the password" autoComplete="new-password" />
          </div>
          <label className="flex items-start gap-2 text-sm text-foreground/80">
            <input type="checkbox" checked={accepted} onChange={(e) => setAccepted(e.target.checked)} className="mt-1" />
            <span>I accept the terms of service and privacy policy.</span>
          </label>
          {error && (
            <div className="rounded-xl bg-red-500/10 border border-red-500/30 text-red-500 text-sm px-4 py-3" role="alert">
              {error}
            </div>
          )}
          <button type="submit" disabled={busy} className="w-full py-2.5 rounded-xl bg-gradient-to-r from-primary-500 to-primary-600 text-white font-medium text-sm disabled:opacity-60 hover:opacity-90 transition-all">
            {busy ? 'Creating account...' : 'Create account'}
          </button>
        </form>
        <p className="text-center text-sm text-muted-foreground mt-6">
          Already have an account?{' '}
          <Link href="/login" className="text-primary-500 hover:underline">Sign in</Link>
        </p>
      </div>
    </div>
  );
}

export default function RegisterPage() {
  return (
    <AuthProvider>
      <RegisterForm />
    </AuthProvider>
  );
}