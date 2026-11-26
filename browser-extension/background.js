/**
 * Know Thyself Browser Extension - Background Service Worker
 * Tracks active tab usage, idle time, and syncs with backend
 */

const API_BASE = 'http://localhost:8000/api/v1';
const SYNC_INTERVAL = 5 * 60 * 1000; // 5 minutes
const IDLE_THRESHOLD = 60; // seconds

// State
let currentTab = null;
let currentUrl = null;
let currentDomain = null;
let sessionStart = null;
let lastActiveTime = Date.now();
let idleTime = 0;
let isTracking = false;
let authToken = null;
let userId = null;
let pendingActivities = [];
let tabSwitchCount = 0;
let scrollCount = 0;
let clickCount = 0;
let keystrokeCount = 0;

// Initialize
chrome.runtime.onInstalled.addListener(async () => {
  console.log('Know Thyself extension installed');
  await loadAuth();
  if (authToken) {
    startTracking();
    scheduleSync();
  }
});

chrome.runtime.onStartup.addListener(async () => {
  await loadAuth();
  if (authToken) {
    startTracking();
    scheduleSync();
  }
});

// Authentication
async function loadAuth() {
  const data = await chrome.storage.local.get(['authToken', 'userId']);
  authToken = data.authToken;
  userId = data.userId;
  console.log('Auth loaded:', !!authToken, userId);
}

export async function setAuth(token, id) {
  authToken = token;
  userId = id;
  await chrome.storage.local.set({ authToken: token, userId: id });
  if (token) {
    startTracking();
    scheduleSync();
  } else {
    stopTracking();
  }
}

// Tab tracking
chrome.tabs.onActivated.addListener(async (activeInfo) => {
  await handleTabSwitch(activeInfo.tabId);
});

chrome.tabs.onUpdated.addListener(async (tabId, changeInfo, tab) => {
  if (changeInfo.status === 'complete' && tab.active) {
    await handleTabUpdate(tab);
  }
});

chrome.windows.onFocusChanged.addListener(async (windowId) => {
  if (windowId === chrome.windows.WINDOW_ID_NONE) {
    await handleWindowBlur();
  } else {
    await handleWindowFocus();
  }
});

async function handleTabSwitch(tabId) {
  if (!isTracking) return;
  
  const now = Date.now();
  await finalizeCurrentSession(now);
  
  const tab = await chrome.tabs.get(tabId);
  if (tab && tab.url) {
    currentTab = tab;
    currentUrl = tab.url;
    currentDomain = extractDomain(tab.url);
    sessionStart = now;
    lastActiveTime = now;
    tabSwitchCount++;
    
    // Notify content script
    chrome.tabs.sendMessage(tabId, { type: 'TAB_ACTIVATED' }).catch(() => {});
  }
}

async function handleTabUpdate(tab) {
  if (!isTracking || !tab.active) return;
  
  const newUrl = tab.url;
  const newDomain = extractDomain(newUrl);
  
  if (newUrl !== currentUrl) {
    const now = Date.now();
    await finalizeCurrentSession(now);
    
    currentUrl = newUrl;
    currentDomain = newDomain;
    sessionStart = now;
    lastActiveTime = now;
  }
}

async function handleWindowBlur() {
  if (!isTracking) return;
  const now = Date.now();
  await finalizeCurrentSession(now);
  isTracking = false;
}

async function handleWindowFocus() {
  if (isTracking) return;
  isTracking = true;
  const tabs = await chrome.tabs.query({ active: true, currentWindow: true });
  if (tabs[0]) {
    await handleTabSwitch(tabs[0].id);
  }
}

// Idle detection
chrome.idle.setDetectionInterval(IDLE_THRESHOLD);
chrome.idle.onStateChanged.addListener((state) => {
  const now = Date.now();
  
  if (state === 'idle') {
    // User went idle
    if (sessionStart) {
      idleTime = now - lastActiveTime;
    }
  } else if (state === 'active') {
    // User became active again
    if (sessionStart) {
      lastActiveTime = now;
    }
  }
});

// Session finalization
async function finalizeCurrentSession(endTime) {
  if (!sessionStart || !currentUrl) return;
  
  const duration = endTime - sessionStart;
  const activeDuration = duration - idleTime;
  
  // Only record meaningful sessions (>5 seconds)
  if (duration > 5000) {
    const activity = {
      session_id: generateSessionId(),
      url: currentUrl,
      domain: currentDomain,
      title: currentTab?.title || '',
      favicon_url: currentTab?.favIconUrl || '',
      category: 'unclassified', // Will be classified by backend
      start_time: new Date(sessionStart).toISOString(),
      end_time: new Date(endTime).toISOString(),
      duration_seconds: Math.round(duration / 1000),
      active_seconds: Math.round(activeDuration / 1000),
      idle_seconds: Math.round(idleTime / 1000),
      tab_switches: tabSwitchCount,
      scroll_count: scrollCount,
      click_count: clickCount,
      keystroke_count: keystrokeCount,
      is_fullscreen: false, // Would need content script to detect
      is_incognito: currentTab?.incognito || false,
      window_id: currentTab?.windowId,
      tab_id: currentTab?.id,
      metadata: {
        user_agent: navigator.userAgent,
        screen_resolution: `${screen.width}x${screen.height}`,
      }
    };
    
    pendingActivities.push(activity);
    
    // Reset counters
    idleTime = 0;
    tabSwitchCount = 0;
    scrollCount = 0;
    clickCount = 0;
    keystrokeCount = 0;
    sessionStart = endTime;
    lastActiveTime = endTime;
  }
}

// Sync with backend
async function syncActivities() {
  if (pendingActivities.length === 0 || !authToken) return;
  
  try {
    const response = await fetch(`${API_BASE}/digital/activities/batch`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${authToken}`,
      },
      body: JSON.stringify({ activities: pendingActivities }),
    });
    
    if (response.ok) {
      console.log(`Synced ${pendingActivities.length} activities`);
      pendingActivities = [];
    } else if (response.status === 401) {
      // Token expired
      await handleAuthError();
    } else {
      console.error('Sync failed:', response.status);
    }
  } catch (error) {
    console.error('Sync error:', error);
  }
}

async function handleAuthError() {
  authToken = null;
  userId = null;
  await chrome.storage.local.remove(['authToken', 'userId']);
  stopTracking();
  
  // Notify popup
  chrome.runtime.sendMessage({ type: 'AUTH_EXPIRED' });
}

function scheduleSync() {
  setInterval(syncActivities, SYNC_INTERVAL);
  
  // Also sync on browser close
  chrome.runtime.onSuspend.addListener(() => {
    syncActivities();
  });
}

// Tracking control
function startTracking() {
  if (isTracking) return;
  isTracking = true;
  sessionStart = Date.now();
  lastActiveTime = Date.now();
  
  // Get current active tab
  chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
    if (tabs[0]) {
      handleTabSwitch(tabs[0].id);
    }
  });
  
  console.log('Tracking started');
}

function stopTracking() {
  if (!isTracking) return;
  isTracking = false;
  
  // Finalize current session
  finalizeCurrentSession(Date.now());
  
  console.log('Tracking stopped');
}

// Message handling
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  switch (message.type) {
    case 'GET_STATUS':
      sendResponse({ isTracking, pendingCount: pendingActivities.length, auth: !!authToken });
      break;
    case 'SET_AUTH':
      setAuth(message.token, message.userId).then(() => sendResponse({ success: true }));
      return true;
    case 'LOGOUT':
      setAuth(null, null).then(() => sendResponse({ success: true }));
      return true;
    case 'RECORD_INTERACTION':
      recordInteraction(message.interaction);
      break;
    case 'PING':
      sendResponse({ pong: true });
      break;
  }
  return true;
});

function recordInteraction(type) {
  switch (type) {
    case 'scroll':
      scrollCount++;
      break;
    case 'click':
      clickCount++;
      break;
    case 'keystroke':
      keystrokeCount++;
      break;
  }
  lastActiveTime = Date.now();
}

function generateSessionId() {
  return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
}

function extractDomain(url) {
  try {
    const hostname = new URL(url).hostname;
    return hostname.replace('www.', '');
  } catch {
    return 'unknown';
  }
}

// Handle content script messages
chrome.runtime.onConnect.addListener((port) => {
  if (port.name === 'content-script') {
    port.onMessage.addListener((message) => {
      if (message.type === 'INTERACTION') {
        recordInteraction(message.interaction);
      } else if (message.type === 'PAGE_VISIBLE') {
        lastActiveTime = Date.now();
      }
    });
  }
});

console.log('Know Thyself background worker loaded');