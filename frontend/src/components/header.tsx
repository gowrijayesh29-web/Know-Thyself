'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { Menu, Sun, Moon, Bell, ChevronDown, Search } from 'lucide-react';
import { useTheme } from 'next-themes';
import { cn } from '@/lib/utils';

interface HeaderProps {
  currentPage: string;
  onMenuClick: () => void;
  user: any | null;
  onUserMenuToggle: (open: boolean) => void;
  userMenuOpen: boolean;
  onLogout: () => Promise<void>;
}

export function Header({ currentPage, onMenuClick, user, onUserMenuToggle, userMenuOpen, onLogout }: HeaderProps) {
  const { theme, setTheme } = useTheme();
  const [notificationsOpen, setNotificationsOpen] = useState(false);

  return (
    <header className="sticky top-0 z-30 glass-strong border-b border-white/10 dark:border-white/5">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="flex h-16 items-center justify-between gap-4">
          {/* Mobile menu button */}
          <button
            onClick={onMenuClick}
            className="lg:hidden glass-subtle p-2 rounded-xl hover:bg-white/10 dark:hover:bg-white/5 transition-colors"
            aria-label="Open navigation menu"
          >
            <Menu className="w-6 h-6 text-foreground" />
          </button>

          {/* Page title */}
          <div className="flex-1 lg:hidden">
            <h1 className="text-lg font-semibold text-foreground truncate">{currentPage}</h1>
          </div>

          {/* Search */}
          <div className="hidden md:flex flex-1 max-w-md">
            <div className="relative w-full">
              <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground" aria-hidden="true" />
              <input
                type="search"
                placeholder="Search Know Thyself..."
                className="w-full pl-11 pr-4 py-2.5 glass-subtle rounded-xl text-sm text-foreground placeholder:text-muted-foreground/50 focus:outline-none focus:ring-2 focus:ring-primary-500/20 transition-all"
                aria-label="Search"
              />
            </div>
          </div>

          {/* Desktop actions */}
          <div className="flex items-center gap-2">
            {/* Theme toggle */}
            <button
              onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
              className="glass-subtle p-2.5 rounded-xl hover:bg-white/10 dark:hover:bg-white/5 transition-colors"
              aria-label={theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'}
            >
              {theme === 'dark' ? (
                <Sun className="w-5 h-5 text-accent-500" />
              ) : (
                <Moon className="w-5 h-5 text-secondary-500" />
              )}
            </button>

            {/* Notifications */}
            <div className="relative">
              <button
                onClick={() => setNotificationsOpen(!notificationsOpen)}
                className="glass-subtle p-2.5 rounded-xl hover:bg-white/10 dark:hover:bg-white/5 transition-colors relative"
                aria-label="Notifications"
                aria-expanded={notificationsOpen}
              >
                <Bell className="w-5 h-5 text-foreground/80" />
                <span className="absolute -top-1 -right-1 w-4 h-4 bg-red-500 text-white text-xs font-medium rounded-full flex items-center justify-center">
                  3
                </span>
              </button>

              {notificationsOpen && (
                <motion.div
                  initial={{ opacity: 0, y: -10, scale: 0.95 }}
                  animate={{ opacity: 1, y: 0, scale: 1 }}
                  exit={{ opacity: 0, y: -10, scale: 0.95 }}
                  className="absolute right-0 top-full mt-2 w-80 glass-strong rounded-2xl shadow-elevation-4 border border-white/10 dark:border-white/5 overflow-hidden"
                  style={{ boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.25)' }}
                >
                  <div className="p-4 border-b border-white/10 dark:border-white/5 flex items-center justify-between">
                    <h3 className="font-semibold text-foreground">Notifications</h3>
                    <button className="text-sm text-primary-600 dark:text-primary-400 hover:underline">Mark all read</button>
                  </div>
                  <div className="max-h-96 overflow-y-auto">
                    {[
                      { title: 'Weekly Report Ready', message: 'Your weekly intelligence report is ready to view.', time: '2h ago', unread: true },
                      { title: 'Goal Achieved!', message: 'You completed your daily step goal of 10,000 steps.', time: '5h ago', unread: true },
                      { title: 'Screen Time Alert', message: 'You\'ve exceeded 3 hours of social media today.', time: '1d ago', unread: false },
                    ].map((notification, index) => (
                      <motion.div
                        key={index}
                        initial={{ opacity: 0, x: 20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: index * 0.05 }}
                        className={cn(
                          'p-4 border-b border-white/5 dark:border-white/5 hover:bg-white/5 dark:hover:bg-white/5 transition-colors',
                          notification.unread && 'bg-primary-500/5 dark:bg-primary-500/10'
                        )}
                      >
                        <div className="flex items-start gap-3">
                          <div className={cn(
                            'w-2 h-2 mt-2 rounded-full flex-shrink-0',
                            notification.unread ? 'bg-primary-500' : 'bg-transparent border border-white/20 dark:border-white/10'
                          )} />
                          <div className="flex-1 min-w-0">
                            <p className={cn('text-sm font-medium text-foreground', notification.unread && 'font-semibold')}>
                              {notification.title}
                            </p>
                            <p className="text-sm text-muted-foreground mt-0.5">{notification.message}</p>
                            <p className="text-xs text-muted-foreground/70 mt-1">{notification.time}</p>
                          </div>
                        </div>
                      </motion.div>
                    ))}
                  </div>
                  <div className="p-3 border-t border-white/10 dark:border-white/5">
                    <button className="w-full text-center text-sm text-primary-600 dark:text-primary-400 hover:underline">
                      View all notifications
                    </button>
                  </div>
                </motion.div>
              )}
            </div>

            {/* User menu */}
            <div className="relative">
              <button
                onClick={() => onUserMenuToggle(!userMenuOpen)}
                className="flex items-center gap-2.5 glass-subtle pr-3 pl-2.5 rounded-xl hover:bg-white/10 dark:hover:bg-white/5 transition-colors"
                aria-label="User menu"
                aria-expanded={userMenuOpen}
              >
                <div className="w-8 h-8 rounded-2xl bg-gradient-to-br from-primary-500 to-secondary-500 flex items-center justify-center">
                  <span className="text-white font-medium text-sm">
                    {user?.full_name?.charAt(0) || user?.email?.charAt(0)?.toUpperCase() || 'U'}
                  </span>
                </div>
                <div className="hidden sm:block text-left">
                  <p className="text-sm font-medium text-foreground truncate max-w-[140px]">
                    {user?.full_name || 'User'}
                  </p>
                  <p className="text-xs text-muted-foreground truncate max-w-[140px]">
                    {user?.email}
                  </p>
                </div>
                <ChevronDown className="w-4 h-4 text-muted-foreground" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}