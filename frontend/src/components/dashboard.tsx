'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { motion, AnimatePresence } from 'framer-motion';
import { LayoutDashboard, MousePointerClick, HeartPulse, Apple, Moon, Target, Brain, BookOpen, Bell, Settings, Menu, X, Sun, Moon as MoonIcon, User, LogOut, ChevronDown } from 'lucide-react';
import { Sidebar } from './sidebar';
import { Header } from './header';
import { OverviewPage } from './pages/overview';
import { DigitalPage } from './pages/digital';
import { PhysicalPage } from './pages/physical';
import { NutritionPage } from './pages/nutrition';
import { SleepPage } from './pages/sleep';
import { GoalsPage } from './pages/goals';
import { AIPage } from './pages/ai';
import { ReportsPage } from './pages/reports';
import { NotificationsPage } from './pages/notifications';
import { KnowledgePage } from './pages/knowledge';
import { SettingsPage } from './pages/settings';
import { useAuth } from '@/components/providers';

type PageType = 
  | 'overview'
  | 'digital'
  | 'physical'
  | 'nutrition'
  | 'sleep'
  | 'goals'
  | 'ai'
  | 'reports'
  | 'notifications'
  | 'knowledge'
  | 'settings';

const navigation = [
  { id: 'overview', label: 'Overview', icon: LayoutDashboard },
  { id: 'digital', label: 'Digital Intelligence', icon: MousePointerClick },
  { id: 'physical', label: 'Physical Health', icon: HeartPulse },
  { id: 'nutrition', label: 'Nutrition', icon: Apple },
  { id: 'sleep', label: 'Sleep & Recovery', icon: Moon },
  { id: 'goals', label: 'Goals', icon: Target },
  { id: 'ai', label: 'AI Intelligence', icon: Brain },
  { id: 'reports', label: 'Weekly Reports', icon: BookOpen },
  { id: 'notifications', label: 'Notifications', icon: Bell },
  { id: 'knowledge', label: 'Knowledge', icon: BookOpen },
  { id: 'settings', label: 'Settings', icon: Settings },
];

const pageComponents: Record<PageType, React.ComponentType> = {
  overview: OverviewPage,
  digital: DigitalPage,
  physical: PhysicalPage,
  nutrition: NutritionPage,
  sleep: SleepPage,
  goals: GoalsPage,
  ai: AIPage,
  reports: ReportsPage,
  notifications: NotificationsPage,
  knowledge: KnowledgePage,
  settings: SettingsPage,
};

export function Dashboard() {
  const [currentPage, setCurrentPage] = useState<PageType>('overview');
  const navigate = (p: PageType) => {
    setCurrentPage(p);
    try { if (window.location.hash !== '#' + p) window.history.pushState(null, '', '#' + p); } catch {}
  };
  useEffect(() => {
    const fromHash = () => {
      const h = window.location.hash.replace('#', '');
      setCurrentPage(h && Object.prototype.hasOwnProperty.call(pageComponents, h) ? (h as PageType) : 'overview');
    };
    fromHash();
    window.addEventListener('hashchange', fromHash);
    return () => window.removeEventListener('hashchange', fromHash);
  }, []);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [userMenuOpen, setUserMenuOpen] = useState(false);
  const { user, isLoading, logout } = useAuth();
  const router = useRouter();
  useEffect(() => {
    if (!isLoading && !user) router.replace('/login');
  }, [isLoading, user, router]);
  useEffect(() => {
    const handler = (e: any) => {
      const page = e?.detail;
      if (page && Object.prototype.hasOwnProperty.call(pageComponents, page)) navigate(page as PageType);
    };
    window.addEventListener('kt-navigate', handler);
    return () => window.removeEventListener('kt-navigate', handler);
  }, []);

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background-light dark:bg-background-dark">
        <div className="glass-strong rounded-3xl p-8 text-center">
          <div className="animate-spin-slow w-12 h-12 border-4 border-primary-500 border-t-transparent rounded-full mx-auto mb-4" />
          <p className="text-foreground/70">Loading Know Thyself...</p>
        </div>
      </div>
    );
  }

  if (!user) return null;

  const CurrentPageComponent = pageComponents[currentPage];

  return (
    <div className="min-h-screen bg-background-light dark:bg-background-dark">
      {/* Mobile sidebar overlay */}
      <AnimatePresence>
        {sidebarOpen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-40 bg-black/50 lg:hidden"
            onClick={() => setSidebarOpen(false)}
            aria-hidden="true"
          />
        )}
      </AnimatePresence>

      {/* Sidebar */}
      <Sidebar
        navigation={navigation}
        currentPage={currentPage}
        onNavigate={navigate}
        open={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
      />

      {/* Main content */}
      <div className="lg:pl-64 min-h-screen transition-all duration-300">
        {/* Header */}
        <Header
          currentPage={navigation.find(n => n.id === currentPage)?.label || 'Overview'}
          onMenuClick={() => setSidebarOpen(true)}
          user={user}
          onUserMenuToggle={setUserMenuOpen}
          userMenuOpen={userMenuOpen}
          onLogout={logout}
        />

        {/* Page content */}
        <main className="p-4 sm:p-6 lg:p-8">
          <AnimatePresence mode="wait">
            <motion.div
              key={currentPage}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3, ease: [0.34, 1.56, 0.64, 1] }}
              className="max-w-7xl mx-auto"
            >
              <CurrentPageComponent />
            </motion.div>
          </AnimatePresence>
        </main>
      </div>

      {/* User dropdown menu */}
      <AnimatePresence>
        {userMenuOpen && (
          <>
            <motion.div
              initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-50"
            onClick={() => setUserMenuOpen(false)}
            />
            <motion.div
              initial={{ opacity: 0, y: -10, scale: 0.95 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, y: -10, scale: 0.95 }}
              className="fixed top-20 right-6 z-50 w-56 glass-strong rounded-2xl shadow-elevation-4 py-2 border border-white/10 dark:border-white/5"
              style={{ boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.25)' }}
            >
              <div className="px-4 py-3 border-b border-white/10 dark:border-white/5">
                <p className="font-medium text-sm text-foreground">{user?.full_name || user?.email}</p>
                <p className="text-xs text-muted-foreground truncate">{user?.email}</p>
              </div>
              <button
                onClick={() => { setUserMenuOpen(false); }}
                className="w-full flex items-center gap-3 px-4 py-2.5 text-sm text-foreground/80 hover:bg-white/5 dark:hover:bg-white/5 transition-colors"
              >
                <User className="w-5 h-5" />
                Profile
              </button>
              <button
                onClick={async () => { await logout(); setUserMenuOpen(false); }}
                className="w-full flex items-center gap-3 px-4 py-2.5 text-sm text-red-500 hover:bg-red-500/10 transition-colors"
              >
                <LogOut className="w-5 h-5" />
                Sign out
              </button>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </div>
  );
}