'use client';

import { motion } from 'framer-motion';
import { BookOpen, Search, Filter, Star, Clock, Brain, Heart, Apple, Moon, Dumbbell, Smartphone, Target, Users, ChevronRight, Tag, ExternalLink, Download, Share2, Bookmark, BookmarkCheck, Zap } from 'lucide-react';
import { cn } from '@/lib/utils';

const categories = [
  { id: 'all', label: 'All', icon: BookOpen },
  { id: 'nutrition', label: 'Nutrition', icon: Apple, color: 'green' },
  { id: 'sleep', label: 'Sleep & Recovery', icon: Moon, color: 'indigo' },
  { id: 'activity', label: 'Physical Activity', icon: Dumbbell, color: 'red' },
  { id: 'mental', label: 'Mental Wellbeing', icon: Brain, color: 'purple' },
  { id: 'digital', label: 'Digital Wellbeing', icon: Smartphone, color: 'blue' },
  { id: 'lifestyle', label: 'General Lifestyle', icon: Target, color: 'orange' },
  { id: 'habits', label: 'Habit Formation', icon: Zap, color: 'amber' },
];

const mockArticles = [
  {
    id: 1,
    title: 'The Science of Sleep Cycles',
    subtitle: 'Understanding REM, deep sleep, and how to optimize each phase',
    category: 'sleep',
    readTime: 8,
    difficulty: 2,
    tags: ['sleep science', 'circadian rhythm', 'optimization'],
    featured: true,
    evidenceQuality: 'high',
    keyTakeaways: [
      'Adults need 7-9 hours with 4-5 complete sleep cycles',
      'Deep sleep dominates first half, REM dominates second half',
      'Consistent wake time is more important than bedtime',
    ],
  },
  {
    id: 2,
    title: 'Protein Timing for Muscle Recovery',
    subtitle: 'When and how much protein to eat for optimal recovery',
    category: 'nutrition',
    readTime: 6,
    difficulty: 2,
    tags: ['protein', 'recovery', 'muscle'],
    featured: false,
    evidenceQuality: 'high',
    keyTakeaways: [
      '20-40g protein within 2 hours post-exercise',
      'Even distribution across meals beats single large dose',
      'Leucine threshold (~3g) triggers muscle protein synthesis',
    ],
  },
  {
    id: 3,
    title: 'Digital Minimalism: A Practical Guide',
    subtitle: 'Reducing screen time without losing productivity',
    category: 'digital',
    readTime: 10,
    difficulty: 1,
    tags: ['digital wellbeing', 'productivity', 'focus'],
    featured: true,
    evidenceQuality: 'moderate',
    keyTakeaways: [
      'Batch notifications into 2-3 scheduled checks',
      'Use grayscale mode after 8 PM',
      'Replace scrolling with intentional activities',
    ],
  },
  {
    id: 4,
    title: 'Building Habits That Actually Stick',
    subtitle: 'The psychology of habit formation and implementation intentions',
    category: 'habits',
    readTime: 7,
    difficulty: 2,
    tags: ['habits', 'psychology', 'behavior change'],
    featured: false,
    evidenceQuality: 'high',
    keyTakeaways: [
      'Start with 2-minute versions of desired habits',
      'Use "if-then" planning for obstacle anticipation',
      'Environment design beats willpower',
    ],
  },
  {
    id: 5,
    title: 'Exercise and Mental Health: The Evidence',
    subtitle: 'How physical activity affects anxiety, depression, and cognitive function',
    category: 'mental',
    readTime: 9,
    difficulty: 2,
    tags: ['exercise', 'mental health', 'anxiety', 'depression'],
    featured: false,
    evidenceQuality: 'high',
    keyTakeaways: [
      '150 min/week moderate exercise reduces depression risk by 26%',
      'Both aerobic and resistance training show benefits',
      'Consistency matters more than intensity',
    ],
  },
  {
    id: 6,
    title: 'Circadian Rhythm Optimization',
    subtitle: 'Aligning your lifestyle with your biological clock',
    category: 'sleep',
    readTime: 8,
    difficulty: 3,
    tags: ['circadian rhythm', 'light exposure', 'melatonin'],
    featured: false,
    evidenceQuality: 'moderate',
    keyTakeaways: [
      'Morning light exposure (10k+ lux) anchors circadian rhythm',
      'Evening blue light suppression critical for melatonin',
      'Meal timing affects peripheral clocks',
    ],
  },
];

const mockRecommendations = [
  {
    id: 1,
    articleId: 1,
    reason: 'Your sleep data shows inconsistent bedtimes and low deep sleep percentage',
    relevance: 0.92,
    trigger: 'pattern',
  },
  {
    id: 2,
    articleId: 4,
    reason: 'You\'ve started 3 new habits this month but only 1 has stuck past 2 weeks',
    relevance: 0.87,
    trigger: 'goal',
  },
  {
    id: 3,
    articleId: 3,
    reason: 'Evening screen time averages 2.5h with social media peaking at 10 PM',
    relevance: 0.95,
    trigger: 'observation',
  },
];

export function KnowledgePage() {
  const [activeCategory, setActiveCategory] = useState('all');
  const [activeTab, setActiveTab] = useState<'library' | 'recommendations'>('library');
  const [searchQuery, setSearchQuery] = useState('');

  const filteredArticles = mockArticles.filter(article => {
    const catMatch = activeCategory === 'all' || article.category === activeCategory;
    const searchMatch = searchQuery === '' ||
      article.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      article.subtitle.toLowerCase().includes(searchQuery.toLowerCase()) ||
      article.tags.some(t => t.toLowerCase().includes(searchQuery.toLowerCase()));
    return catMatch && searchMatch;
  });

  return (
    <div className="space-y-6">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4"
      >
        <div>
          <h1 className="heading-1">Knowledge & Learning</h1>
          <p className="body-md text-muted-foreground mt-1">
            Evidence-based articles, personalized recommendations, and practical guides for your journey.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <div className="relative hidden sm:block">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground" />
            <input
              type="search"
              placeholder="Search articles..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-11 pr-4 py-2.5 glass-subtle rounded-xl text-sm w-64 focus:outline-none focus:ring-2 focus:ring-primary-500/20"
            />
          </div>
        </div>
      </motion.div>

      {/* Category Filter */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="flex flex-wrap gap-2"
      >
        {categories.map((cat) => (
          <button
            key={cat.id}
            onClick={() => setActiveCategory(cat.id)}
            className={cn(
              'flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium transition-colors',
              activeCategory === cat.id
                ? `bg-${cat.color}-100 dark:bg-${cat.color}-900/30 text-${cat.color}-600 dark:text-${cat.color}-400`
                : 'glass-subtle text-foreground/70 hover:bg-white/5 dark:hover:bg-white/5'
            )}
          >
            <cat.icon className="w-4 h-4" />
            {cat.label}
          </button>
        ))}
      </motion.div>

      {/* Tabs */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.15 }}
        className="flex gap-2 mb-6"
      >
        {[
          { id: 'library', label: 'Library', icon: BookOpen },
          { id: 'recommendations', label: 'For You', icon: Sparkles },
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id as any)}
            className={cn(
              'flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium transition-colors',
              activeTab === tab.id
                ? 'bg-primary-100 dark:bg-primary-900/30 text-primary-600 dark:text-primary-400'
                : 'glass-subtle text-foreground/70 hover:bg-white/5 dark:hover:bg-white/5'
            )}
          >
            <tab.icon className="w-4 h-4" />
            {tab.label}
          </button>
        ))}
      </motion.div>

      {/* Content */}
      {activeTab === 'library' && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4"
        >
          {filteredArticles.map((article, index) => (
            <ArticleCard key={article.id} article={article} index={index} />
          ))}
          {filteredArticles.length === 0 && (
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              className="col-span-full card p-12 text-center"
            >
              <Search className="w-16 h-16 mx-auto text-muted-foreground/50 mb-4" />
              <h3 className="heading-5 mb-2">No articles found</h3>
              <p className="text-muted-foreground">Try adjusting your filters or search terms</p>
            </motion.div>
          )}
        </motion.div>
      )}

      {activeTab === 'recommendations' && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-4"
        >
          <div className="card p-6">
            <div className="flex items-center gap-3 mb-4">
              <div className="p-3 rounded-xl bg-primary-100 dark:bg-primary-900/30 text-primary-600 dark:text-primary-400">
                <Sparkles className="w-6 h-6" />
              </div>
              <div>
                <h3 className="heading-5">Personalized Recommendations</h3>
                <p className="text-sm text-muted-foreground">Based on your patterns, goals, and recent activity</p>
              </div>
            </div>
          </div>
          {mockRecommendations.map((rec, index) => (
            <RecommendationArticleCard key={rec.id} recommendation={rec} index={index} />
          ))}
        </motion.div>
      )}
    </div>
  );
}

function ArticleCard({ article, index }: any) {
  const categoryConfig = categories.find(c => c.id === article.category) || categories[0];

  return (
    <motion.article
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.05 }}
      className="card-hover group"
      whileHover={{ y: -4 }}
    >
      {article.featured && (
        <div className="absolute top-4 right-4 z-10">
          <span className="px-2 py-1 rounded-full text-xs font-medium bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-300">
            Featured
          </span>
        </div>
      )}
      <div className="mb-4">
        <span className={cn('px-2 py-1 rounded-full text-xs font-medium', `bg-${categoryConfig.color}-100 dark:bg-${categoryConfig.color}-900/30 text-${categoryConfig.color}-700 dark:text-${categoryConfig.color}-300`)}>
          {categoryConfig.label}
        </span>
      </div>
      <h3 className="heading-6 mb-2 line-clamp-2">{article.title}</h3>
      <p className="text-sm text-muted-foreground mb-4 line-clamp-2">{article.subtitle}</p>
      <div className="flex flex-wrap gap-2 mb-4">
        {article.tags.slice(0, 3).map((tag: string) => (
          <span key={tag} className="px-2 py-0.5 rounded-full text-xs text-muted-foreground bg-muted-foreground/10">
            {tag}
          </span>
        ))}
      </div>
      <div className="flex items-center justify-between pt-4 border-t border-white/10 dark:border-white/5">
        <div className="flex items-center gap-3 text-sm text-muted-foreground">
          <span className="flex items-center gap-1">
            <Clock className="w-4 h-4" />
            {article.readTime} min read
          </span>
          <span className="flex items-center gap-1">
            <BookOpen className="w-4 h-4" />
            Level {article.difficulty}
          </span>
        </div>
        <div className="flex items-center gap-2">
          <span className={cn('px-2 py-1 rounded-full text-xs font-medium', 
            article.evidenceQuality === 'high' ? 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300' :
            article.evidenceQuality === 'moderate' ? 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-300' :
            'bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300'
          )}>
            {article.evidenceQuality}
          </span>
        </div>
      </div>
    </motion.article>
  );
}

function RecommendationArticleCard({ recommendation, index }: any) {
  const article = mockArticles.find(a => a.id === recommendation.articleId);
  if (!article) return null;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.05 }}
      className="card-hover p-5"
      whileHover={{ y: -2 }}
    >
      <div className="flex items-start justify-between gap-4 mb-3">
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-1">
            <span className="px-2 py-0.5 rounded-full text-xs font-medium bg-primary-100 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300">
              {Math.round(recommendation.relevance * 100)}% match
            </span>
            <span className="px-2 py-0.5 rounded-full text-xs font-medium bg-gray-100 dark:bg-gray-900/30 text-gray-700 dark:text-gray-300">
              {recommendation.trigger}
            </span>
          </div>
          <h4 className="font-semibold text-foreground">{article?.title}</h4>
          <p className="text-sm text-muted-foreground mt-1">{article?.subtitle}</p>
        </div>
        <div className="flex flex-col items-end gap-2">
          <div className="w-12 h-16 rounded-lg bg-gradient-to-br from-primary-500 to-secondary-500 flex items-center justify-center">
            <BookOpen className="w-8 h-8 text-white" />
          </div>
          <button className="btn-primary btn-sm">Read Now</button>
        </div>
      </div>
      <div className="glass-subtle p-3 rounded-xl text-sm">
        <p className="text-muted-foreground mb-2"><strong>Why this matters for you:</strong> {recommendation.reason}</p>
        <div className="flex items-center gap-2 text-xs text-muted-foreground">
          <Clock className="w-3 h-3" />
          <span>{article?.readTime} min read</span>
          <span>•</span>
          <span>Level {article?.difficulty}</span>
          <span>•</span>
          <span className={cn(
            article?.evidenceQuality === 'high' ? 'text-green-600' :
            article?.evidenceQuality === 'moderate' ? 'text-yellow-600' : 'text-blue-600'
          )}>
            {article?.evidenceQuality} evidence
          </span>
        </div>
      </div>
    </motion.div>
  );
}

// Missing imports
import { useState } from 'react';
import { Sparkles } from 'lucide-react';
