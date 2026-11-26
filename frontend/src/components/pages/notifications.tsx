'use client';

import { motion } from 'framer-motion';
import { Bell, BellOff, Check, ChevronRight, Filter, Clock, AlertTriangle, CheckCircle, Trophy, BookOpen, Zap, Target, Moon, Smartphone, MoreVertical, Trash2 } from 'lucide-react';
import { cn, formatRelativeTime } from '@/lib/utils';

const mockNotifications = [
  { id: 1, type: 'achievement', title: '7-Day Focus Streak!', message: 'You\'ve completed focus sessions for 7 consecutive days.', time: '2h ago', read: false, priority: 'high' },
  { id: 2, type: 'warning', title: 'Screen Time Limit Exceeded', message: 'Social media usage has exceeded your 2-hour daily limit.', time: '3h ago', read: false, priority: 'high' },
  { id: 3, type: 'insight', title: 'Weekly Report Ready', message: 'Your intelligence report for Week 46 is now available.', time: '5h ago', read: false, priority: 'medium' },
  { id: 4, type: 'reminder', title: 'Bedtime in 30 Minutes', message: 'Your target bedtime is 10:30 PM. Start winding down.', time: '1d ago', read: true, priority: 'medium' },
  { id: 5, type: 'achievement', title: 'Goal Completed: 10k Steps', message: 'You hit your daily step target of 10,000 steps!', time: '1d ago', read: true, priority: 'low' },
  { id: 6, type: 'nudging', title: 'Focus Session Suggested', message: 'Good time for a 45-min deep work session before lunch.', time: '2d ago', read: true, priority: 'low' },
  { id: 7, type: 'warning', title: 'Hydration Reminder', message: 'You\'ve only had 800ml water today. Target: 2.5L', time: '2d ago', read: true, priority: 'medium' },
  { id: 8, type: 'insight', title: 'Pattern Detected', message: 'Late-night coding correlates with poor sleep quality.', time: '3d ago', read: true, priority: 'low' },
  { id: 9, type: 'reminder', title: 'Weekly Check-in Due', message: 'Your weekly lifestyle survey is ready to complete.', time: '4d ago', read: true, priority: 'low' },
  { id: 10, type: 'achievement', title: 'Month Milestone', message: '30 days of consistent sleep tracking!', time: '5d ago', read: true, priority: 'low' },
];

const typeConfig: Record<string, { icon: React.ReactNode; color: string; label: string }> = {
  achievement: { icon: <Trophy className="w-5 h-5" />, color: 'yellow', label: 'Achievement' },
  warning: { icon: <AlertTriangle className="w-5 h-5" />, color: 'red', label: 'Warning' },
  insight: { icon: <Lightbulb className="w-5 h-5" />, color: 'blue', label: 'Insight' },
  reminder: { icon: <Clock className="w-5 h-5" />, color: 'purple', label: 'Reminder' },
  nudging: { icon: <Zap className="w-5 h-5" />, color: 'orange', label: 'Nudge' },
  report: { icon: <BookOpen className="w-5 h-5" />, color: 'indigo', label: 'Report' },
};

export function NotificationsPage() {
  const [filter, setFilter] = useState<'all' | 'unread' | 'read'>('all');
  const [notifications, setNotifications] = useState(mockNotifications);

  const filteredNotifications = notifications.filter(n => {
    if (filter === 'unread') return !n.read;
    if (filter === 'read') return n.read;
    return true;
  });

  const unreadCount = notifications.filter(n => !n.read).length;

  const markAsRead = (id: number) => {
    setNotifications(prev => prev.map(n => n.id === id ? { ...n, read: true } : n));
  };

  const markAllAsRead = () => {
    setNotifications(prev => prev.map(n => ({ ...n, read: true })));
  };

  const deleteNotification = (id: number) => {
    setNotifications(prev => prev.filter(n => n.id !== id));
  };

  return (
    <div className="space-y-6">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4"
      >
        <div>
          <h1 className="heading-1">Notifications</h1>
          <p className="body-md text-muted-foreground mt-1">
            Stay informed with personalized alerts, insights, and achievement celebrations.
          </p>
        </div>
        <div className="flex items-center gap-3">
          {unreadCount > 0 && (
            <button onClick={markAllAsRead} className="btn-outline">
              <Check className="w-4 h-4 mr-2" />
              Mark All Read ({unreadCount})
            </button>
          )}
          <button className="btn-outline">
            <Filter className="w-4 h-4 mr-2" />
            Filters
          </button>
        </div>
      </motion.div>

      {/* Filter Tabs */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="flex gap-2"
      >
        {['all', 'unread', 'read'].map((f) => (
          <button
            key={f}
            onClick={() => setFilter(f as any)}
            className={cn(
              'px-4 py-2 rounded-xl text-sm font-medium transition-colors',
              filter === f
                ? 'bg-primary-100 dark:bg-primary-900/30 text-primary-600 dark:text-primary-400'
                : 'glass-subtle text-foreground/70 hover:bg-white/5 dark:hover:bg-white/5'
            )}
          >
            {f.charAt(0).toUpperCase() + f.slice(1)}
            {f === 'unread' && unreadCount > 0 && (
              <span className="ml-2 px-2 py-0.5 rounded-full text-xs bg-primary-100 dark:bg-primary-900/30 text-primary-600 dark:text-primary-400">
                {unreadCount}
              </span>
            )}
          </button>
        ))}
      </motion.div>

      {/* Notifications List */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.15 }}
        className="space-y-3"
      >
        {filteredNotifications.length === 0 ? (
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="card p-12 text-center"
          >
            <BellOff className="w-16 h-16 mx-auto text-muted-foreground/50 mb-4" />
            <h3 className="heading-5 mb-2">No notifications</h3>
            <p className="text-muted-foreground">You're all caught up!</p>
          </motion.div>
        ) : (
          filteredNotifications.map((notification, index) => (
            <NotificationItem
              key={notification.id}
              notification={notification}
              index={index}
              onRead={markAsRead}
              onDelete={deleteNotification}
            />
          ))
        )}
      </motion.div>

      {/* Settings */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="card p-6"
      >
        <h2 className="heading-5 mb-4">Notification Preferences</h2>
        <div className="space-y-4">
          {[
            { key: 'nudges', label: 'Smart Nudges', desc: 'AI-powered suggestions based on your patterns', enabled: true },
            { key: 'reminders', label: 'Goal Reminders', desc: 'Reminders for your active goals and routines', enabled: true },
            { key: 'achievements', label: 'Achievements', desc: 'Celebrate milestones and streak completions', enabled: true },
            { key: 'warnings', label: 'Threshold Warnings', desc: 'Alerts when you exceed your set limits', enabled: true },
            { key: 'insights', label: 'Weekly Insights', desc: 'Pattern detections and correlation findings', enabled: true },
            { key: 'reports', label: 'Weekly Reports', desc: 'Notification when your report is ready', enabled: true },
          ].map((pref) => (
            <PreferenceToggle key={pref.key} {...pref} />
          ))}
        </div>
      </motion.div>
    </div>
  );
}

function NotificationItem({ notification, index, onRead, onDelete }: any) {
  const config = typeConfig[notification.type] || typeConfig.insight;
  const priorityColors: Record<string, string> = {
    high: 'red',
    medium: 'yellow',
    low: 'green',
  };

  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: index * 0.03 }}
      className={cn(
        'flex items-start gap-4 p-4 rounded-xl transition-colors',
        !notification.read
          ? 'bg-primary-500/5 dark:bg-primary-500/10 border-l-4 border-primary-500'
          : 'glass-subtle hover:bg-white/5 dark:hover:bg-white/5'
      )}
    >
      <div className={cn('p-3 rounded-xl flex-shrink-0', `bg-${config.color}-100 dark:bg-${config.color}-900/30 text-${config.color}-600 dark:text-${config.color}-400`)}>
        {config.icon}
      </div>
      <div className="flex-1 min-w-0">
        <div className="flex items-start justify-between gap-2 mb-1">
          <h4 className={cn('font-semibold', !notification.read ? 'text-foreground' : 'text-foreground/70')}>
            {notification.title}
          </h4>
          <div className="flex items-center gap-2">
            <span className={cn(
              'px-2 py-0.5 rounded-full text-xs font-medium',
              `bg-${priorityColors[notification.priority]}-100 dark:bg-${priorityColors[notification.priority]}-900/30 text-${priorityColors[notification.priority]}-700 dark:text-${priorityColors[notification.priority]}-300`
            )}>
              {notification.priority}
            </span>
            <span className="text-xs text-muted-foreground">{notification.time}</span>
          </div>
        </div>
        <p className="text-sm text-muted-foreground mb-2">{notification.message}</p>
        <div className="flex items-center gap-2">
          <span className="px-2 py-0.5 rounded-full text-xs font-medium bg-gray-100 dark:bg-gray-900/30 text-gray-700 dark:text-gray-300">
            {config.label}
          </span>
          {!notification.read && (
            <button onClick={() => onRead(notification.id)} className="btn-primary btn-sm">
              Mark Read
            </button>
          )}
        </div>
      </div>
      <div className="flex flex-col items-end gap-2">
        {!notification.read && (
          <div className="w-2 h-2 rounded-full bg-primary-500" />
        )}
        <button
          onClick={() => onDelete(notification.id)}
          className="p-2 rounded-lg text-muted-foreground/50 hover:text-red-500 hover:bg-red-500/10 transition-colors"
          aria-label="Delete notification"
        >
          <Trash2 className="w-4 h-4" />
        </button>
      </div>
    </motion.div>
  );
}

function PreferenceToggle({ key, label, desc, enabled }: any) {
  const [isEnabled, setIsEnabled] = useState(enabled);

  return (
    <div className="flex items-center justify-between p-4 glass-subtle rounded-xl">
      <div className="flex-1">
        <h4 className="font-medium text-foreground">{label}</h4>
        <p className="text-sm text-muted-foreground">{desc}</p>
      </div>
      <button
        onClick={() => setIsEnabled(!isEnabled)}
        className={cn(
          'relative w-12 h-7 rounded-full transition-colors',
          isEnabled ? 'bg-primary-500' : 'bg-muted-foreground/20'
        )}
        aria-checked={isEnabled}
        role="switch"
      >
        <motion.div
          animate={{ x: isEnabled ? 24 : 2 }}
          transition={{ type: 'spring', stiffness: 500, damping: 30 }}
          className="absolute top-1 left-1 w-5 h-5 bg-white rounded-full shadow-md"
        />
      </button>
    </div>
  );
}

// Missing imports
import { useState } from 'react';
import { Lightbulb } from 'lucide-react';
