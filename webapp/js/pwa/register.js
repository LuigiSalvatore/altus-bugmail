// ─── PWA Service Worker Registration ──────────────────────────

/**
 * Register the service worker for PWA support.
 */
export function registerServiceWorker() {
  if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('/sw.js');
  }
}
