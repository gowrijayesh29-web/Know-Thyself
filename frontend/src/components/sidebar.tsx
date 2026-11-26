'use client';

import { motion } from 'framer-motion';
import { LucideIcon } from 'lucide-react';
import { cn } from '@/lib/utils';

interface NavigationItem {
  id: string;
  label: string;
  icon: LucideIcon;
}

interface SidebarProps {
  navigation: NavigationItem[];
  currentPage: string;
  onNavigate: (page: any) => void;
  open: boolean;
  onClose: () => void;
}

export function Sidebar({ navigation, currentPage, onNavigate, open, onClose }: SidebarProps) {
  return (
    <>
      {/* Desktop sidebar */}
      <aside
        className={cn(
          'fixed left-0 top-0 z-50 h-screen w-64 glass-strong border-r border-white/10 dark:border-white/5',
          'transform transition-transform duration-300 ease-out lg:translate-x-0',
          open ? 'translate-x-0' : '-translate-x-full'
        )}
        aria-label="Main navigation"
      >
        <div className="flex h-full flex-col">
          {/* Logo */}
          <div className="flex h-20 items-center justify-center px-6 border-b border-white/10 dark:border-white/5">
            <motion.div
              initial={{ scale: 0.8, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ delay: 0.1, type: 'spring', stiffness: 260, damping: 20 }}
              className="flex items-center gap-3"
            >
              <div className="relative">
                <div className="w-10 h-10 rounded-2xl bg-gradient-to-br from-primary-500 to-secondary-500 flex items-center justify-center">
                  <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                  </svg>
                </div>
                <motion.div
                  animate={{ scale: [1, 1.1, 1] }}
                  transition={{ duration: 2, repeat: Infinity, ease: 'easeInOut' }}
                  className="absolute -bottom-1 -right-1 w-3 h-3 bg-accent-500 rounded-full border-2 border-background-light dark:border-background-dark"
                />
              </div>
              <div>
                <h1 className="text-xl font-bold text-foreground">Know Thyself</h1>
                <p className="text-xs text-muted-foreground">Your Intelligence</p>
              </div>
            </motion.div>
          </div>

          {/* Navigation */}
          <nav className="flex-1 overflow-y-auto px-4 py-6 space-y-1" aria-label="Navigation">
            {navigation.map((item, index) => (
              <motion.button
                key={item.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.1 + index * 0.03, type: 'spring', stiffness: 260, damping: 20 }}
                onClick={() => { onNavigate(item.id); onClose(); }}
                className={cn(
                  'w-full flex items-center gap-3 px-4 py-3 rounded-2xl text-sm font-medium transition-all duration-200',
                  'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-500 focus-visible:ring-offset-2 focus-visible:ring-offset-background-dark',
                  currentPage === item.id
                    ? 'bg-gradient-to-r from-primary-500/20 to-secondary-500/20 text-primary-600 dark:text-primary-400 shadow-glass'
                    : 'text-foreground/70 hover:bg-white/5 dark:hover:bg-white/5 hover:text-foreground'
                )}
                aria-current={currentPage === item.id ? 'page' : undefined}
              >
                <item.icon className="w-5 h-5 flex-shrink-0" aria-hidden="true" />
                <span>{item.label}</span>
                {currentPage === item.id && (
                  <motion.div
                    layoutId="active-indicator"
                    className="ml-auto w-1.5 h-1.5 rounded-full bg-primary-500"
                    transition={{ type: 'spring', stiffness: 500, damping: 30 }}
                  />
                )}
              </motion.button>
            ))}
          </nav>

        </div>
      </aside>

      {/* Mobile close button */}
      <motion.button
        initial={{ opacity: 0, scale: 0.8 }}
        animate={{ opacity: open ? 1 : 0, scale: open ? 1 : 0.8 }}
        exit={{ opacity: 0, scale: 0.8 }}
        onClick={onClose}
        className="fixed bottom-6 right-6 z-40 lg:hidden glass-strong p-3 rounded-2xl shadow-elevation-3"
        aria-label="Close navigation"
      >
        <svg className="w-6 h-6 text-foreground" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
        </svg>
      </motion.button>
    </>
  );
}