'use client';

import { Dashboard } from '@/components/dashboard';
import { AuthProvider } from '@/components/providers';

export default function HomePage() {
  return (
    <AuthProvider>
      <Dashboard />
    </AuthProvider>
  );
}