'use client';

import { motion } from 'framer-motion';
import { User, Shield, Bell, Palette, Globe, Database, Key, Trash2, Download, Mail, Smartphone, Laptop, Tablet, LogOut, ChevronRight, Save, AlertCircle, CheckCircle, Moon, Dumbbell } from 'lucide-react';
import { cn } from '@/lib/utils';
import { useTheme } from 'next-themes';

const settingsSections = [
  { id: 'profile', label: 'Profile', icon: User },
  { id: 'preferences', label: 'Preferences', icon: Palette },
  { id: 'notifications', label: 'Notifications', icon: Bell },
  { id: 'privacy', label: 'Privacy & Security', icon: Shield },
  { id: 'integrations', label: 'Integrations', icon: Database },
  { id: 'devices', label: 'Devices', icon: Smartphone },
  { id: 'data', label: 'Data & Export', icon: Download },
  { id: 'danger', label: 'Danger Zone', icon: Trash2, danger: true },
];

export function SettingsPage() {
  const { theme, setTheme } = useTheme();
  const [activeSection, setActiveSection] = useState('profile');
  const [profile, setProfile] = useState({
    fullName: 'Alex Johnson',
    email: 'alex@example.com',
    timezone: 'America/New_York',
    language: 'en',
  });
  const [preferences, setPreferences] = useState({
    theme: 'system',
    compactMode: false,
    animations: true,
    autoRefresh: true,
    units: 'metric',
    weekStart: 'monday',
  });
  const [notificationPrefs, setNotificationPrefs] = useState({
    email: true,
    push: true,
    inApp: true,
    marketing: false,
    weeklyReport: true,
    goalReminders: true,
    thresholdAlerts: true,
    insights: true,
  });
  const [privacySettings, setPrivacySettings] = useState({
    analytics: true,
    crashReports: true,
    personalizedAds: false,
    dataSharing: false,
    aiProcessing: true,
  });

  return (
    <div className="space-y-6">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4"
      >
        <div>
          <h1 className="heading-1">Settings</h1>
          <p className="body-md text-muted-foreground mt-1">
            Manage your account, preferences, privacy, and data.
          </p>
        </div>
      </motion.div>

      <div className="flex flex-col lg:flex-row gap-6">
        {/* Sidebar Navigation */}
        <motion.aside
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          className="lg:w-64 flex-shrink-0 space-y-2"
        >
          {settingsSections.map((section) => (
            <button
              key={section.id}
              onClick={() => setActiveSection(section.id)}
              className={cn(
                'w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-all',
                'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-500 focus-visible:ring-offset-2',
                activeSection === section.id
                  ? 'bg-primary-100 dark:bg-primary-900/30 text-primary-600 dark:text-primary-400 shadow-glass'
                  : section.danger
                  ? 'text-red-500/80 hover:bg-red-500/10 dark:hover:bg-red-500/10'
                  : 'text-foreground/70 hover:bg-white/5 dark:hover:bg-white/5'
              )}
            >
              <section.icon className="w-5 h-5 flex-shrink-0" />
              {section.label}
            </button>
          ))}
        </motion.aside>

        {/* Content */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          className="flex-1 min-w-0 space-y-6"
        >
          {activeSection === 'profile' && <ProfileSettings profile={profile} onChange={setProfile} />}
          {activeSection === 'preferences' && <PreferencesSettings preferences={preferences} onChange={setPreferences} theme={theme} setTheme={setTheme} />}
          {activeSection === 'notifications' && <NotificationSettings prefs={notificationPrefs} onChange={setNotificationPrefs} />}
          {activeSection === 'privacy' && <PrivacySettings settings={privacySettings} onChange={setPrivacySettings} />}
          {activeSection === 'integrations' && <IntegrationsSettings />}
          {activeSection === 'devices' && <DevicesSettings />}
          {activeSection === 'data' && <DataSettings />}
          {activeSection === 'danger' && <DangerZone />}
        </motion.div>
      </div>
    </div>
  );
}

function Section({ title, description, children }: any) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="card p-6"
    >
      <div className="mb-6">
        <h2 className="heading-5">{title}</h2>
        {description && <p className="text-sm text-muted-foreground mt-1">{description}</p>}
      </div>
      {children}
    </motion.div>
  );
}

function ProfileSettings({ profile, onChange }: any) {
  return (
    <>
      <Section title="Personal Information" description="Your basic profile details visible in the app">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <InputField label="Full Name" value={profile.fullName} onChange={(e) => onChange({ ...profile, fullName: e.target.value })} />
          <InputField label="Email" value={profile.email} type="email" disabled />
          <SelectField label="Timezone" value={profile.timezone} onChange={(e) => onChange({ ...profile, timezone: e.target.value })} options={[
            'America/New_York', 'America/Chicago', 'America/Denver', 'America/Los_Angeles',
            'Europe/London', 'Europe/Paris', 'Europe/Berlin', 'Asia/Tokyo', 'Australia/Sydney',
          ]} />
          <SelectField label="Language" value={profile.language} onChange={(e) => onChange({ ...profile, language: e.target.value })} options={[
            { value: 'en', label: 'English' },
            { value: 'es', label: 'Spanish' },
            { value: 'fr', label: 'French' },
            { value: 'de', label: 'German' },
            { value: 'ja', label: 'Japanese' },
          ]} />
        </div>
      </Section>

      <Section title="Avatar" description="Your profile picture shown across the app">
        <div className="flex items-center gap-6">
          <div className="w-24 h-24 rounded-2xl bg-gradient-to-br from-primary-500 to-secondary-500 flex items-center justify-center">
            <span className="text-white text-2xl font-bold">{profile.fullName?.charAt(0) || 'U'}</span>
          </div>
          <div>
            <button className="btn-primary mb-2"><Upload className="w-4 h-4 mr-2" /> Change Avatar</button>
            <p className="text-sm text-muted-foreground">JPG, PNG up to 5MB. Square images work best.</p>
          </div>
        </div>
      </Section>

      <div className="flex justify-end">
        <button className="btn-primary"><Save className="w-4 h-4 mr-2" /> Save Changes</button>
      </div>
    </>
  );
}

function PreferencesSettings({ preferences, onChange, theme, setTheme }: any) {
  return (
    <>
      <Section title="Appearance" description="Customize how Know Thyself looks and feels">
        <div className="space-y-4">
          <SettingItem
            label="Theme"
            description="Choose your preferred color scheme"
            content={
              <div className="flex gap-3">
                {['light', 'dark', 'system'].map((t) => (
                  <button
                    key={t}
                    onClick={() => { setTheme(t); onChange({ ...preferences, theme: t }); }}
                    className={cn(
                      'flex-1 p-4 rounded-xl border-2 transition-colors',
                      theme === t
                        ? 'border-primary-500 bg-primary-500/10 dark:bg-primary-500/20'
                        : 'border-white/10 dark:border-white/5 hover:border-white/20 dark:hover:border-white/10'
                    )}
                  >
                    <div className="w-8 h-8 rounded-lg mx-auto mb-2" style={{
                      background: t === 'light' ? '#ffffff' : t === 'dark' ? '#0f0f1a' : 'linear-gradient(135deg, #ffffff, #0f0f1a)'
                    }} />
                    <p className="text-center text-sm font-medium capitalize">{t}</p>
                  </button>
                ))}
              </div>
            }
          />
          <SettingItem
            label="Compact Mode"
            description="Reduce spacing for more information density"
            content={
              <Toggle checked={preferences.compactMode} onChange={(checked) => onChange({ ...preferences, compactMode: checked })} />
            }
          />
          <SettingItem
            label="Animations"
            description="Enable smooth transitions and micro-interactions"
            content={
              <Toggle checked={preferences.animations} onChange={(checked) => onChange({ ...preferences, animations: checked })} />
            }
          />
          <SettingItem
            label="Auto Refresh"
            description="Automatically refresh data when app regains focus"
            content={
              <Toggle checked={preferences.autoRefresh} onChange={(checked) => onChange({ ...preferences, autoRefresh: checked })} />
            }
          />
        </div>
      </Section>

      <Section title="Units & Formats" description="Measurement and display preferences">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <SelectField
            label="Units"
            value={preferences.units}
            onChange={(e) => onChange({ ...preferences, units: e.target.value })}
            options={[
              { value: 'metric', label: 'Metric (kg, cm, km)' },
              { value: 'imperial', label: 'Imperial (lbs, ft, mi)' },
            ]}
          />
          <SelectField
            label="Week Starts On"
            value={preferences.weekStart}
            onChange={(e) => onChange({ ...preferences, weekStart: e.target.value })}
            options={[
              { value: 'monday', label: 'Monday' },
              { value: 'sunday', label: 'Sunday' },
            ]}
          />
        </div>
      </Section>
    </>
  );
}

function NotificationSettings({ prefs, onChange }: any) {
  return (
    <>
      <Section title="Delivery Channels" description="How you receive notifications">
        <div className="space-y-3">
          {Object.entries(prefs).map(([key, enabled]) => (
            <SettingItem
              key={key}
              label={key.charAt(0).toUpperCase() + key.slice(1).replace(/([A-Z])/g, ' $1')}
              description={`Receive ${key} notifications`}
              content={
                <Toggle checked={enabled} onChange={(checked) => onChange({ ...prefs, [key]: checked })} />
              }
            />
          ))}
        </div>
      </Section>

      <Section title="Quiet Hours" description="Suppress non-urgent notifications during specified times">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <InputField label="Start Time" type="time" value="22:00" />
          <InputField label="End Time" type="time" value="07:00" />
        </div>
        <p className="text-sm text-muted-foreground mt-2">Urgent alerts (threshold warnings) will still come through during quiet hours.</p>
      </Section>

      <Section title="Frequency Limits" description="Maximum notifications per time period">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <InputField label="Max per Hour" type="number" value="3" />
          <InputField label="Max per Day" type="number" value="10" />
        </div>
      </Section>
    </>
  );
}

function PrivacySettings({ settings, onChange }: any) {
  return (
    <>
      <Section title="Data Processing" description="Control how your data is used">
        <div className="space-y-3">
          {Object.entries(settings).map(([key, enabled]) => (
            <SettingItem
              key={key}
              label={key.charAt(0).toUpperCase() + key.slice(1).replace(/([A-Z])/g, ' $1')}
              description={getPrivacyDescription(key)}
              content={
                <Toggle checked={enabled} onChange={(checked) => onChange({ ...settings, [key]: checked })} />
              }
            />
          ))}
        </div>
      </Section>

      <Section title="Consent Management" description="Review and update your consent preferences">
        <div className="space-y-3">
          {[
            { type: 'Data Collection', version: '2.1', given: true },
            { type: 'Analytics', version: '1.3', given: true },
            { type: 'AI Processing', version: '1.0', given: true },
            { type: 'Marketing', version: '1.0', given: false },
            { type: 'Third-party Sharing', version: '1.0', given: false },
          ].map((consent) => (
            <div key={consent.type} className="flex items-center justify-between p-4 glass-subtle rounded-xl">
              <div>
                <p className="font-medium text-foreground">{consent.type}</p>
                <p className="text-sm text-muted-foreground">Version {consent.version} • {consent.given ? 'Given' : 'Not given'}</p>
              </div>
              <button className={cn('px-3 py-1.5 rounded-lg text-sm font-medium', consent.given ? 'bg-red-500/10 text-red-600 dark:text-red-400' : 'bg-green-500/10 text-green-600 dark:text-green-400')}>
                {consent.given ? 'Withdraw' : 'Grant'}
              </button>
            </div>
          ))}
        </div>
      </Section>
    </>
  );
}

function getPrivacyDescription(key: string): string {
  const descriptions: Record<string, string> = {
    analytics: 'Allow anonymous usage analytics to improve the product',
    crashReports: 'Send crash reports to help fix bugs',
    personalizedAds: 'Enable personalized advertising (currently disabled)',
    dataSharing: 'Share anonymized data with research partners',
    aiProcessing: 'Allow AI processing of your data for personalized insights',
  };
  return descriptions[key] || '';
}

function IntegrationsSettings() {
  return (
    <>
      <Section title="Connected Services" description="Manage your third-party integrations">
        <div className="space-y-4">
          {[
            { name: 'Apple Health', icon: Heart, connected: true, description: 'Steps, workouts, heart rate, sleep' },
            { name: 'Google Fit', icon: Heart, connected: false, description: 'Activity, heart rate, sleep data' },
            { name: 'Fitbit', icon: Heart, connected: false, description: 'Steps, sleep, heart rate, weight' },
            { name: 'Oura Ring', icon: Moon, connected: false, description: 'Sleep, readiness, activity scores' },
            { name: 'Garmin Connect', icon: Dumbbell, connected: false, description: 'Advanced training metrics' },
            { name: 'Strava', icon: Dumbbell, connected: false, description: 'Running, cycling, swimming activities' },
          ].map((integration) => (
            <IntegrationCard key={integration.name} {...integration} />
          ))}
        </div>
      </Section>

      <Section title="Browser Extension" description="Install the Know Thyself browser extension for automatic digital activity tracking">
        <div className="flex items-center justify-between p-4 glass-subtle rounded-xl">
          <div>
            <h4 className="font-medium text-foreground">Know Thyself Browser Extension</h4>
            <p className="text-sm text-muted-foreground">Track website usage, focus sessions, and digital wellbeing automatically</p>
          </div>
          <button className="btn-primary">Install Extension</button>
        </div>
      </Section>
    </>
  );
}

function IntegrationCard({ name, icon: Icon, connected, description }: any) {
  return (
    <div className="flex items-center justify-between p-4 glass-subtle rounded-xl">
      <div className="flex items-center gap-4">
        <div className="p-3 rounded-xl bg-primary-100 dark:bg-primary-900/30 text-primary-600 dark:text-primary-400">
          <Icon className="w-5 h-5" />
        </div>
        <div>
          <h4 className="font-medium text-foreground">{name}</h4>
          <p className="text-sm text-muted-foreground">{description}</p>
        </div>
      </div>
      <button className={cn('px-4 py-2 rounded-lg text-sm font-medium', connected ? 'bg-red-500/10 text-red-600 dark:text-red-400' : 'btn-primary')}>
        {connected ? 'Disconnect' : 'Connect'}
      </button>
    </div>
  );
}

function DevicesSettings() {
  return (
    <>
      <Section title="Active Sessions" description="Devices currently signed into your account">
        <div className="space-y-3">
          {[
            { device: 'MacBook Pro', browser: 'Chrome 120', location: 'San Francisco, CA', current: true, lastActive: 'Now' },
            { device: 'iPhone 15', browser: 'Safari', location: 'San Francisco, CA', current: false, lastActive: '2h ago' },
            { device: 'iPad Pro', browser: 'Chrome', location: 'Home', current: false, lastActive: '1d ago' },
          ].map((device) => (
            <DeviceCard key={device.device} {...device} />
          ))}
        </div>
      </Section>

      <Section title="Push Notifications" description="Manage web push subscriptions for this browser">
        <div className="space-y-3">
          <div className="flex items-center justify-between p-4 glass-subtle rounded-xl">
            <div>
              <h4 className="font-medium text-foreground">This Browser (Chrome 120)</h4>
              <p className="text-sm text-muted-foreground">Subscribed • Last used: Now</p>
            </div>
            <span className="px-2 py-1 rounded-full text-xs font-medium bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300">Active</span>
          </div>
          <button className="btn-outline w-full">Enable Push Notifications</button>
        </div>
      </Section>
    </>
  );
}

function DeviceCard({ device, browser, location, current, lastActive }: any) {
  return (
    <div className="flex items-center justify-between p-4 glass-subtle rounded-xl">
      <div className="flex items-center gap-4">
        <div className="p-3 rounded-xl bg-primary-100 dark:bg-primary-900/30 text-primary-600 dark:text-primary-400">
          <Laptop className="w-5 h-5" />
        </div>
        <div>
          <div className="flex items-center gap-2">
            <h4 className="font-medium text-foreground">{device}</h4>
            {current && <span className="px-2 py-0.5 rounded-full text-xs font-medium bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300">Current</span>}
          </div>
          <p className="text-sm text-muted-foreground">{browser} • {location}</p>
        </div>
      </div>
      <div className="text-right">
        <p className="text-sm font-medium text-foreground">{lastActive}</p>
        {!current && <button className="text-sm text-red-500 hover:underline mt-1">Sign Out</button>}
      </div>
    </div>
  );
}

function DataSettings() {
  return (
    <>
      <Section title="Export Your Data" description="Download a complete copy of your data in JSON format">
        <div className="flex items-center justify-between p-4 glass-subtle rounded-xl">
          <div>
            <h4 className="font-medium text-foreground">Complete Data Export</h4>
            <p className="text-sm text-muted-foreground">Includes all tracking data, goals, reports, and settings</p>
          </div>
          <button className="btn-primary"><Download className="w-4 h-4 mr-2" /> Request Export</button>
        </div>
        <p className="text-sm text-muted-foreground mt-2">Export will be emailed to you within 24 hours. Includes data from the last 365 days by default.</p>
      </Section>

      <Section title="Scheduled Exports" description="Automatically receive data exports on a schedule">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <SelectField label="Frequency" value="monthly" options={[{value: 'weekly', label: 'Weekly'}, {value: 'monthly', label: 'Monthly'}, {value: 'quarterly', label: 'Quarterly'}]} />
          <InputField label="Format" type="text" value="JSON" disabled />
          <SelectField label="Date Range" value="all" options={[{value: '30', label: 'Last 30 days'}, {value: '90', label: 'Last 90 days'}, {value: '365', label: 'Last 365 days'}, {value: 'all', label: 'All time'}]} />
        </div>
      </Section>

      <Section title="Import Data" description="Restore data from a previous export">
        <div className="flex items-center justify-between p-4 glass-subtle rounded-xl">
          <div>
            <h4 className="font-medium text-foreground">Import Data File</h4>
            <p className="text-sm text-muted-foreground">Upload a JSON export to restore your data</p>
          </div>
          <button className="btn-outline">Choose File</button>
        </div>
      </Section>
    </>
  );
}

function DangerZone() {
  return (
    <>
      <Section title="Reset Data" description="Permanently delete specific categories of your data" className="border-l-4 border-red-500">
        <div className="space-y-4">
          {[
            { name: 'Digital Activity', desc: 'All website usage, focus sessions, and thresholds', icon: Monitor },
            { name: 'Health Data', desc: 'Sleep, nutrition, activity, and hydration records', icon: Heart },
            { name: 'Goals & Tasks', desc: 'All goals, progress, tasks, and focus sessions', icon: Target },
            { name: 'AI Insights', desc: 'Observations, patterns, recommendations, and reports', icon: Brain },
          ].map((item) => (
            <div key={item.name} className="flex items-center justify-between p-4 glass-subtle rounded-xl border border-red-500/20">
              <div className="flex items-center gap-4">
                <div className="p-3 rounded-xl bg-red-100 dark:bg-red-900/30 text-red-600 dark:text-red-400">
                  <item.icon className="w-5 h-5" />
                </div>
                <div>
                  <h4 className="font-medium text-foreground">{item.name}</h4>
                  <p className="text-sm text-muted-foreground">{item.desc}</p>
                </div>
              </div>
              <button className="px-4 py-2 rounded-lg text-sm font-medium bg-red-500/10 text-red-600 dark:text-red-400 hover:bg-red-500/20">Delete</button>
            </div>
          ))}
        </div>
      </Section>

      <Section title="Delete Account" description="Permanently delete your account and all associated data. This action cannot be undone." className="border-l-4 border-red-500 bg-red-500/5">
        <div className="space-y-4">
          <div className="p-4 glass-subtle rounded-xl border border-red-500/20">
            <div className="flex items-center gap-3 mb-3">
              <AlertCircle className="w-6 h-6 text-red-500" />
              <div>
                <h4 className="font-medium text-foreground">This will permanently delete:</h4>
                <ul className="text-sm text-muted-foreground mt-1 space-y-1 list-disc list-inside">
                  <li>Your account and profile</li>
                  <li>All tracking data and history</li>
                  <li>Goals, tasks, and focus sessions</li>
                  <li>AI observations and reports</li>
                  <li>Settings and preferences</li>
                </ul>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <input type="checkbox" id="confirm-delete" className="w-4 h-4 rounded border-gray-300 text-red-500 focus:ring-red-500" required />
              <label htmlFor="confirm-delete" className="text-sm text-foreground">I understand this action is irreversible</label>
            </div>
            <button className="btn-primary" disabled>Delete Account Permanently</button>
          </div>
        </div>
      </Section>

      <Section title="Sign Out Everywhere" description="End all active sessions on all devices">
        <div className="flex items-center justify-between p-4 glass-subtle rounded-xl">
          <div>
            <h4 className="font-medium text-foreground">Sign Out of All Devices</h4>
            <p className="text-sm text-muted-foreground">You will need to sign in again on each device</p>
          </div>
          <button className="btn-outline text-red-500 border-red-500/50 hover:bg-red-500/10">Sign Out Everywhere</button>
        </div>
      </Section>
    </>
  );
}

// Helper Components
function SettingItem({ label, description, content }: any) {
  return (
    <div className="flex items-center justify-between p-4 glass-subtle rounded-xl">
      <div className="flex-1">
        <h4 className="font-medium text-foreground">{label}</h4>
        <p className="text-sm text-muted-foreground">{description}</p>
      </div>
      <div>{content}</div>
    </div>
  );
}

function Toggle({ checked, onChange }: any) {
  return (
    <button
      onClick={() => onChange(!checked)}
      className={cn('relative w-12 h-7 rounded-full transition-colors', checked ? 'bg-primary-500' : 'bg-muted-foreground/20')}
      aria-checked={checked}
      role="switch"
    >
      <motion.div
        animate={{ x: checked ? 24 : 2 }}
        transition={{ type: 'spring', stiffness: 500, damping: 30 }}
        className="absolute top-1 left-1 w-5 h-5 bg-white rounded-full shadow-md"
      />
    </button>
  );
}

function InputField({ label, value, onChange, type = 'text', disabled, ...props }: any) {
  return (
    <div>
      <label className="block text-sm font-medium text-foreground mb-1.5">{label}</label>
      <input
        type={type}
        value={value}
        onChange={onChange}
        disabled={disabled}
        className="input"
        {...props}
      />
    </div>
  );
}

function SelectField({ label, value, onChange, options, ...props }: any) {
  return (
    <div>
      <label className="block text-sm font-medium text-foreground mb-1.5">{label}</label>
      <select value={value} onChange={onChange} className="input" {...props}>
        {options.map((opt: any) => (
          <option key={opt.value} value={opt.value}>{opt.label || opt}</option>
        ))}
      </select>
    </div>
  );
}

// Missing imports
import { useState } from 'react';
import { Upload, Monitor, Heart, Target, Brain } from 'lucide-react';
