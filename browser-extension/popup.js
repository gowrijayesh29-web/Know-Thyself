/**
 * Know Thyself Browser Extension - Popup Script
 */

const API_BASE = 'http://localhost:8000/api/v1';

let authToken = null;
let isTracking = true;

// DOM Elements
const loginView = document.getElementById('login-view');
const dashboardView = document.getElementById('dashboard-view');
const loginForm = document.getElementById('login-form');
const loginError = document.getElementById('login-error');
const logoutBtn = document.getElementById('logout-btn');
const userEmail = document.getElementById('user-email');
const statsGrid = document.getElementById('stats-grid');
const trackingIndicator = document.getElementById('tracking-indicator');
const currentIcon = document.getElementById('current-icon');
const currentDomain = document.getElementById('current-domain');
const currentDuration = document.getElementById('current-duration');
const topSites = document.getElementById('top-sites');
const openDashboardBtn = document.getElementById('open-dashboard');
const pauseTrackingBtn = document.getElementById('pause-tracking');
const syncNowBtn = document.getElementById('sync-now');
const syncStatus = document.getElementById('sync-status');

// Initialize
document.addEventListener('DOMContentLoaded', async () => {
  await loadAuth();
  setupEventListeners();
  if (authToken) {
    showDashboard();
    await loadDashboardData();
    startAutoRefresh();
  } else {
    showLogin();
  }
});

async function loadAuth() {
  const data = await chrome.storage.local.get(['authToken', 'userId']);
  authToken = data.authToken;
}

function setupEventListeners() {
  loginForm.addEventListener('submit', handleLogin);
  logoutBtn.addEventListener('click', handleLogout);
  openDashboardBtn.addEventListener('click', () => {
    chrome.tabs.create({ url: 'http://localhost:3000' });
  });
  pauseTrackingBtn.addEventListener('click', toggleTracking);
  syncNowBtn.addEventListener('click', syncNow);

  // Listen for background messages
  chrome.runtime.onMessage.addListener((message) => {
    if (message.type === 'AUTH_EXPIRED') {
      handleAuthExpired();
    }
  });
}

async function handleLogin(e) {
  e.preventDefault();
  const email = document.getElementById('email').value;
  const password = document.getElementById('password').value;
  
  loginError.classList.add('hidden');
  
  try {
    const response = await fetch(`${API_BASE}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password, remember_me: true }),
    });
    
    const data = await response.json();
    
    if (!response.ok) {
      throw new Error(data.detail || 'Login failed');
    }
    
    authToken = data.access_token;
    await chrome.storage.local.set({ 
      authToken: data.access_token,
      userId: data.user.id 
    });
    
    // Notify background
    chrome.runtime.sendMessage({ type: 'SET_AUTH', token: data.access_token, userId: data.user.id });
    
    showDashboard();
    await loadDashboardData();
    startAutoRefresh();
    
  } catch (error) {
    loginError.textContent = error.message;
    loginError.classList.remove('hidden');
  }
}

async function handleLogout() {
  authToken = null;
  await chrome.storage.local.remove(['authToken', 'userId']);
  chrome.runtime.sendMessage({ type: 'LOGOUT' });
  showLogin();
}

function handleAuthExpired() {
  authToken = null;
  showLogin();
}

function showLogin() {
  loginView.classList.remove('hidden');
  dashboardView.classList.add('hidden');
}

function showDashboard() {
  loginView.classList.add('hidden');
  dashboardView.classList.remove('hidden');
}

async function loadDashboardData() {
  if (!authToken) return;
  
  try {
    // Load today's stats
    const today = new Date().toISOString().split('T')[0];
    const statsResponse = await fetch(`${API_BASE}/digital/activities/today`, {
      headers: { 'Authorization': `Bearer ${authToken}` },
    });
    
    if (statsResponse.ok) {
      const stats = await statsResponse.json();
      updateStats(stats);
    }
    
    // Load current activity
    const tabs = await chrome.tabs.query({ active: true, currentWindow: true });
    if (tabs[0]) {
      updateCurrentActivity(tabs[0]);
    }
    
    // Load top sites
    const sitesResponse = await fetch(`${API_BASE}/digital/activities?start_time=${today}T00:00:00`, {
      headers: { 'Authorization': `Bearer ${authToken}` },
    });
    
    if (sitesResponse.ok) {
      const data = await sitesResponse.json();
      updateTopSites(data.items);
    }
    
    syncStatus.textContent = `Last sync: ${new Date().toLocaleTimeString()}`;
    
  } catch (error) {
    console.error('Failed to load dashboard:', error);
  }
}

function updateStats(stats) {
  document.getElementById('screen-time').textContent = formatDuration(stats.active_seconds || stats.total_seconds);
  document.getElementById('focus-sessions').textContent = stats.session_count || 0;
  document.getElementById('productive-time').textContent = formatDuration(stats.productive_seconds);
  document.getElementById('distraction-time').textContent = formatDuration(stats.unproductive_seconds);
}

function updateCurrentActivity(tab) {
  if (!tab || !tab.url) {
    currentDomain.textContent = 'No active tab';
    currentDuration.textContent = '--';
    return;
  }
  
  const domain = extractDomain(tab.url);
  const favicon = tab.favIconUrl || '';
  
  currentDomain.textContent = domain;
  currentDomain.title = tab.title || domain;
  
  // Update icon based on domain
  updateActivityIcon(domain);
  
  // Calculate duration (would need background to track)
  currentDuration.textContent = 'Active now';
}

function updateActivityIcon(domain) {
  const icons = {
    'github.com': 'M9 19c-5 1.5-5-2.5-7-3m14 6v-3.87a3.37 3.37 0 0 0-.94-2.61c3.14-.35 6.44-1.54 6.44-7A5.44 5.44 0 0 0 20 4.77 5.07 5.07 0 0 0 19.91 1S18.73.65 16 2.48a13.38 13.38 0 0 0-7 0C6.27.65 5.09 1 5.09 1A5.07 5.07 0 0 0 5 4.77a5.44 5.44 0 0 0-1.5 3.78c0 5.42 3.3 6.61 6.44 7A3.37 3.37 0 0 0 9 18.13V22',
    'youtube.com': 'M23 4.5a2.5 2.5 0 0 0-5 0v15a2.5 2.5 0 0 0 5 0v-15zM17 12l-5 4.5V7.5L17 12z',
    'twitter.com': 'M23 3a10.9 10.9 0 0 1-3.14 1.53 4.48 4.48 0 0 0-7.86 3v1A10.66 10.66 0 0 1 3 4s-4 9 5 13a11.64 11.64 0 0 1-7 2c9 5 20 0 20-12.5a4.5 4.5 0 0 0-.08-.83A7.72 7.72 0 0 0 23 3z',
    'linkedin.com': 'M16 8a6 6 0 0 1 6 6v7h-4v-7a2 2 0 0 0-2-2 2 2 0 0 0-2 2v7h-4v-7a6 6 0 0 1 6-6zM2 9h4v12H2zM4 6a2 2 0 1 0 0-4 2 2 0 0 0 0 4z',
  };
  
  const path = icons[domain] || 'M21 12h-1M4 12H3m3.343-5.657l-.707-.707M18 18a2 2 0 000-4 2 2 0 000 4zm-6-2a2 2 0 01-2-2V6a2 2 0 012-2h6a2 2 0 012 2v10a2 2 0 01-2 2H9a2 2 0 01-2-2v-2a2 2 0 012-2h6a2 2 0 012 2v10a2 2 0 01-2 2H9a2 2 0 01-2 2z';
  currentIcon.innerHTML = `<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="${path}" />`;
}

function updateTopSites(sites) {
  if (!sites || sites.length === 0) {
    topSites.innerHTML = '<p class="text-sm text-gray-500 dark:text-gray-400 text-center py-4">No activity yet</p>';
    return;
  }
  
  // Group by domain
  const domainStats = {};
  sites.forEach(site => {
    const domain = extractDomain(site.url);
    if (!domainStats[domain]) {
      domainStats[domain] = { domain, time: 0, category: site.category };
    }
    domainStats[domain].time += site.active_seconds || 0;
  });
  
  // Sort and take top 5
  const sorted = Object.values(domainStats)
    .sort((a, b) => b.time - a.time)
    .slice(0, 5);
  
  topSites.innerHTML = sorted.map(site => `
    <div class="flex items-center justify-between p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800">
      <div class="flex items-center gap-3">
        <div class="w-8 h-8 rounded-lg bg-gradient-to-br from-green-500 to-purple-500 flex items-center justify-center">
          <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12h-1M4 12H3m3.343-5.657l-.707-.707M18 18a2 2 0 000-4 2 2 0 000 4zm-6-2a2 2 0 01-2-2V6a2 2 0 012-2h6a2 2 0 012 2v10a2 2 0 01-2 2H9a2 2 0 01-2-2v-2a2 2 0 012-2h6a2 2 0 012 2v10a2 2 0 01-2 2H9a2 2 0 01-2 2z" />
          </svg>
        </div>
        <div>
          <p class="text-sm font-medium truncate max-w-[160px]">${site.domain}</p>
          <p class="text-xs text-gray-500 dark:text-gray-400 capitalize">${site.category}</p>
        </div>
      </div>
      <span class="text-sm font-medium">${formatDuration(site.time)}</span>
    </div>
  `).join('');
}

function toggleTracking() {
  isTracking = !isTracking;
  chrome.runtime.sendMessage({ type: isTracking ? 'START_TRACKING' : 'STOP_TRACKING' });
  pauseTrackingBtn.textContent = isTracking ? 'Pause Tracking' : 'Resume Tracking';
  trackingIndicator.classList.toggle('bg-gray-400', !isTracking);
  trackingIndicator.classList.toggle('bg-green-500', isTracking);
}

async function syncNow() {
  syncNowBtn.textContent = 'Syncing...';
  syncNowBtn.disabled = true;
  
  try {
    await chrome.runtime.sendMessage({ type: 'SYNC_NOW' });
    await loadDashboardData();
  } catch (error) {
    console.error('Sync failed:', error);
  } finally {
    syncNowBtn.textContent = 'Sync Now';
    syncNowBtn.disabled = false;
  }
}

function startAutoRefresh() {
  // Refresh every 30 seconds
  setInterval(loadDashboardData, 30000);
}

function formatDuration(seconds) {
  if (!seconds || seconds < 60) return `${seconds || 0}s`;
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  if (hours > 0) return `${hours}h ${minutes}m`;
  return `${minutes}m`;
}

function extractDomain(url) {
  try {
    return new URL(url).hostname.replace('www.', '');
  } catch {
    return url;
  }
}

console.log('Know Thyself popup loaded');