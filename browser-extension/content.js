/**
 * Know Thyself Browser Extension - Content Script
 * Tracks page interactions and visibility
 */

let isVisible = !document.hidden;
let lastActivity = Date.now();
let scrollTimeout = null;
let clickCount = 0;
let keystrokeCount = 0;

// Connect to background
const port = chrome.runtime.connect({ name: 'content-script' });

// Notify background of page visibility
function notifyVisibility(visible) {
  isVisible = visible;
  port.postMessage({ type: visible ? 'PAGE_VISIBLE' : 'PAGE_HIDDEN' });
}

// Track interactions
function trackInteraction(type) {
  const now = Date.now();
  if (now - lastActivity > 1000) { // Throttle
    port.postMessage({ type: 'INTERACTION', interaction: type });
    lastActivity = now;
  }
}

// Scroll tracking
window.addEventListener('scroll', () => {
  if (scrollTimeout) clearTimeout(scrollTimeout);
  scrollTimeout = setTimeout(() => trackInteraction('scroll'), 100);
}, { passive: true });

// Click tracking
document.addEventListener('click', () => {
  clickCount++;
  trackInteraction('click');
}, { passive: true });

// Keystroke tracking
document.addEventListener('keydown', () => {
  keystrokeCount++;
  trackInteraction('keystroke');
}, { passive: true });

// Visibility tracking
document.addEventListener('visibilitychange', () => {
  notifyVisibility(!document.hidden);
});

// Page unload - final notification
window.addEventListener('beforeunload', () => {
  port.postMessage({ type: 'PAGE_UNLOAD' });
});

// Focus/blur
window.addEventListener('focus', () => {
  notifyVisibility(true);
});

window.addEventListener('blur', () => {
  notifyVisibility(false);
});

// Periodic heartbeat
setInterval(() => {
  if (isVisible) {
    port.postMessage({ type: 'HEARTBEAT' });
  }
}, 30000);

console.log('Know Thyself content script loaded');