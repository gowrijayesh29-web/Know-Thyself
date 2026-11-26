'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { BookOpen, Calendar, ChevronLeft, ChevronRight, Download, Share2, Printer, Clock, Zap, Heart, Moon, Apple, Target, TrendingUp, TrendingDown, AlertCircle, CheckCircle, FileText, BarChart3 } from 'lucide-react';
import { cn, formatDate, formatRelativeTime } from '@/lib/utils';

const mockReports = [
  {
    id: 1,
    weekStart: '2024-11-11',
    weekEnd: '2024-11-17',
    status: 'completed',
    generatedAt: '2024-11-18T08:00:00Z',
    summary: {
      overall: 'Good progress this week with improvements in sleep consistency and focus sessions.',
      digitalScore: 78,
      physicalScore: 82,
      nutritionScore: 65,
      sleepScore: 85,
    },
    highlights: [
      'Sleep efficiency improved to 91% (avg)',
      'Completed 18 focus sessions (target: 15)',
      'Screen time reduced by 8% vs last week',
    ],
    concerns: [
      'Protein intake below target (avg 87g vs 130g)',
      'Weekend screen time spikes on Saturday',
    ],
  },
  {
    id: 2,
    weekStart: '2024-11-04',
    weekEnd: '2024-11-10',
    status: 'completed',
    generatedAt: '2024-11-11T08:00:00Z',
    summary: {
      overall: 'Solid week with strong activity performance but digital wellbeing needs attention.',
      digitalScore: 62,
      physicalScore: 88,
      nutritionScore: 75,
      sleepScore: 78,
    },
    highlights: [
      'Hit 10k steps 6/7 days',
      'Completed 4 workouts',
      'Good meal consistency',
    ],
    concerns: [
      'Social media time exceeded 2h daily limit',
      'Inconsistent bedtime (variance ±1.5h)',
    ],
  },
  {
    id: 3,
    weekStart: '2024-10-28',
    weekEnd: '2024-11-03',
    status: 'completed',
    generatedAt: '2024-11-04T08:00:00Z',
    summary: {
      overall: 'Recovery week with lower activity but improved sleep quality.',
      digitalScore: 70,
      physicalScore: 65,
      nutritionScore: 80,
      sleepScore: 88,
    },
    highlights: [
      'Best sleep week of the month',
      'Nutrition variety score: 82%',
      'Low stress scores',
    ],
    concerns: [
      'Only 2 workouts completed',
      'Step count below 5k for 3 days',
    ],
  },
];

export function ReportsPage() {
  const [selectedReport, setSelectedReport] = useState(mockReports[0]);
  const [viewMode, setViewMode] = useState<'list' | 'detail'>('detail');

  return (
    <div className="space-y-6">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4"
      >
        <div>
          <h1 className="heading-1">Weekly Reports</h1>
          <p className="body-md text-muted-foreground mt-1">
            Your personalized intelligence reports. Track progress, identify patterns, and plan ahead.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button className="btn-outline">
            <Calendar className="w-4 h-4 mr-2" />
            Custom Range
          </button>
          <button className="btn-primary">
            <FileText className="w-4 h-4 mr-2" />
            Generate Report
          </button>
        </div>
      </motion.div>

      {viewMode === 'detail' && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex flex-col lg:flex-row gap-6"
        >
          {/* Report List Sidebar */}
          <aside className="lg:w-72 flex-shrink-0 space-y-3">
            {mockReports.map((report) => (
              <ReportListItem
                key={report.id}
                report={report}
                isSelected={selectedReport.id === report.id}
                onClick={() => setSelectedReport(report)}
              />
            ))}
            <button className="w-full btn-outline justify-center mt-4">
              Load More Reports
            </button>
          </aside>

          {/* Report Detail */}
          <div className="flex-1 min-w-0">
            <ReportDetail report={selectedReport} onClose={() => setViewMode('list')} />
          </div>
        </motion.div>
      )}

      {viewMode === 'list' && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-4"
        >
          {mockReports.map((report) => (
            <ReportCard key={report.id} report={report} onClick={() => { setSelectedReport(report); setViewMode('detail'); }} />
          ))}
        </motion.div>
      )}
    </div>
  );
}

function ReportListItem({ report, isSelected, onClick }: any) {
  return (
    <button
      onClick={onClick}
      className={cn(
        'w-full text-left p-4 rounded-xl transition-all',
        isSelected
          ? 'bg-primary-100 dark:bg-primary-900/30 border-l-4 border-primary-500'
          : 'glass-subtle hover:bg-white/5 dark:hover:bg-white/5'
      )}
    >
      <div className="flex items-center justify-between mb-2">
        <span className={cn('text-sm font-medium', isSelected ? 'text-primary-600 dark:text-primary-400' : 'text-foreground')}>
          Week of {formatDate(report.weekStart)}
        </span>
        <span className={cn(
          'px-2 py-0.5 rounded-full text-xs font-medium',
          report.status === 'completed' ? 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300' :
          'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-300'
        )}>
          {report.status}
        </span>
      </div>
      <p className="text-xs text-muted-foreground">{formatDate(report.weekStart)} – {formatDate(report.weekEnd)}</p>
    </button>
  );
}

function ReportCard({ report, onClick }: any) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      onClick={onClick}
      className="card-hover p-6 cursor-pointer"
      whileHover={{ y: -4 }}
    >
      <div className="flex items-start justify-between mb-4">
        <div>
          <p className="text-sm font-medium text-foreground/60">Weekly Intelligence Report</p>
          <p className="heading-5 mt-1">Week of {formatDate(report.weekStart)}</p>
        </div>
        <span className={cn(
          'px-3 py-1 rounded-full text-xs font-medium',
          report.status === 'completed' ? 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300' :
          'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-300'
        )}>
          {report.status}
        </span>
      </div>
      <p className="text-sm text-muted-foreground mb-4">{formatDate(report.weekStart)} – {formatDate(report.weekEnd)}</p>
      <div className="grid grid-cols-4 gap-4 mb-4">
        <ScoreBadge label="Digital" value={report.summary.digitalScore} icon={<Smartphone className="w-4 h-4" />} />
        <ScoreBadge label="Physical" value={report.summary.physicalScore} icon={<Heart className="w-4 h-4" />} />
        <ScoreBadge label="Nutrition" value={report.summary.nutritionScore} icon={<Apple className="w-4 h-4" />} />
        <ScoreBadge label="Sleep" value={report.summary.sleepScore} icon={<Moon className="w-4 h-4" />} />
      </div>
      <p className="text-sm text-foreground/80 italic">"{report.summary.overall}"</p>
    </motion.div>
  );
}

function ScoreBadge({ label, value, icon }: any) {
  const color = value >= 80 ? 'green' : value >= 60 ? 'yellow' : 'red';
  return (
    <div className="text-center p-3 glass-subtle rounded-xl">
      <div className="flex items-center justify-center gap-1 mb-1">
        {icon}
        <span className="text-xs font-medium text-foreground/60">{label}</span>
      </div>
      <div className={cn('text-2xl font-bold', `text-${color}-600 dark:text-${color}-400`)}>{value}</div>
    </div>
  );
}

function ReportDetail({ report, onClose }: any) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-6"
    >
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <button onClick={onClose} className="btn-ghost btn-sm btn-icon mb-2">
            <ChevronLeft className="w-4 h-4" />
          </button>
          <h1 className="heading-1">Weekly Intelligence Report</h1>
          <p className="text-muted-foreground">{formatDate(report.weekStart)} – {formatDate(report.weekEnd)}</p>
        </div>
        <div className="flex items-center gap-2">
          <button className="btn-outline"><Share2 className="w-4 h-4 mr-2" /> Share</button>
          <button className="btn-outline"><Download className="w-4 h-4 mr-2" /> PDF</button>
          <button className="btn-outline"><Printer className="w-4 h-4 mr-2" /> Print</button>
        </div>
      </div>

      {/* Summary Scores */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="grid grid-cols-2 md:grid-cols-4 gap-4"
      >
        <DetailScoreCard label="Digital Wellbeing" value={report.summary.digitalScore} icon={<Smartphone className="w-6 h-6" />} color="blue" description="Screen time, focus, distractions" />
        <DetailScoreCard label="Physical Health" value={report.summary.physicalScore} icon={<Heart className="w-6 h-6" />} color="red" description="Activity, workouts, steps" />
        <DetailScoreCard label="Nutrition" value={report.summary.nutritionScore} icon={<Apple className="w-6 h-6" />} color="green" description="Macros, variety, hydration" />
        <DetailScoreCard label="Sleep & Recovery" value={report.summary.sleepScore} icon={<Moon className="w-6 h-6" />} color="indigo" description="Duration, quality, consistency" />
      </motion.div>

      {/* Overall Summary */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="card p-6"
      >
        <h2 className="heading-5 mb-4">Week at a Glance</h2>
        <p className="text-foreground/80 leading-relaxed">{report.summary.overall}</p>
      </motion.div>

      {/* Highlights & Concerns */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.15 }}
          className="card p-6"
        >
          <div className="flex items-center gap-2 mb-4">
            <CheckCircle className="w-5 h-5 text-green-500" />
            <h2 className="heading-5">Improvements</h2>
          </div>
          <ul className="space-y-3">
            {report.highlights.map((item, index) => (
              <motion.li
                key={index}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.05 }}
                className="flex items-start gap-3 text-sm"
              >
                <CheckCircle className="w-5 h-5 text-green-500 flex-shrink-0 mt-0.5" />
                <span className="text-foreground/80">{item}</span>
              </motion.li>
            ))}
          </ul>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="card p-6"
        >
          <div className="flex items-center gap-2 mb-4">
            <AlertCircle className="w-5 h-5 text-yellow-500" />
            <h2 className="heading-5">Areas for Attention</h2>
          </div>
          <ul className="space-y-3">
            {report.concerns.map((item, index) => (
              <motion.li
                key={index}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.05 }}
                className="flex items-start gap-3 text-sm"
              >
                <AlertCircle className="w-5 h-5 text-yellow-500 flex-shrink-0 mt-0.5" />
                <span className="text-foreground/80">{item}</span>
              </motion.li>
            ))}
          </ul>
        </motion.div>
      </div>

      {/* Action Buttons */}
      <div className="flex items-center justify-end gap-3">
        <button className="btn-outline"><Download className="w-4 h-4 mr-2" /> Download PDF</button>
        <button className="btn-primary"><FileText className="w-4 h-4 mr-2" /> Save to Archive</button>
      </div>
    </motion.div>
  );
}

function DetailScoreCard({ label, value, icon, color, description }: any) {
  return (
    <div className="card-hover p-6 text-center" whileHover={{ y: -4 }}>
      <div className={cn('p-3 rounded-xl mx-auto mb-4 w-fit', `bg-${color}-100 dark:bg-${color}-900/30 text-${color}-600 dark:text-${color}-400`)}>
        {icon}
      </div>
      <p className="text-4xl font-bold text-foreground">{value}</p>
      <p className="font-medium text-foreground mt-1">{label}</p>
      <p className="text-sm text-muted-foreground mt-2">{description}</p>
      <div className="mt-4 h-2 bg-muted-foreground/10 rounded-full overflow-hidden">
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${value}%` }}
          transition={{ delay: 0.3, duration: 0.8, ease: [0.34, 1.56, 0.64, 1] }}
          className="h-full rounded-full"
          style={{ background: `var(--color-${color}-500)` }}
        />
      </div>
    </div>
  );
}

// Missing imports
import { Smartphone } from 'lucide-react';
