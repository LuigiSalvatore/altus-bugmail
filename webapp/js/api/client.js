// ─── API Client ───────────────────────────────────────────────
// Centralized HTTP communication with the Flask backend.

import state from '../state/store.js';
import { toast } from '../ui/notifications.js';
import { setStatus } from '../ui/statusbar.js';

/**
 * Generic JSON API helper.
 * @param {'GET'|'POST'|'DELETE'} method
 * @param {string} path   API path (e.g. '/api/data').
 * @param {Object} [body] Request body (POST/DELETE with JSON).
 * @returns {Promise<any>}  Parsed JSON response.
 * @throws {Error}  On non-OK responses.
 */
export async function api(method, path, body) {
  const opts = { method, headers: { 'Content-Type': 'application/json' } };
  if (body) opts.body = JSON.stringify(body);
  const r = await fetch(path, opts);
  const contentType = r.headers.get('Content-Type') || '';
  if (!r.ok) {
    let errMsg = r.statusText;
    if (contentType.includes('application/json')) {
      try {
        const errJson = await r.json();
        errMsg = errJson.error || JSON.stringify(errJson);
      } catch (_) { /* ignore parse error */ }
    } else {
      try { errMsg = await r.text(); } catch (_) { /* ignore */ }
    }
    throw new Error(errMsg);
  }
  if (contentType.includes('application/json')) {
    try { return await r.json(); } catch (_) { return []; }
  }
  return await r.text();
}

/**
 * Low-level POST to a server control endpoint.
 * Handles the case where the connection is lost (server shutting down).
 */
export async function sendServerCommand(path) {
  const res = await fetch(path, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' }
  });
  if (!res.ok) {
    const json = await res.json().catch(() => ({}));
    throw new Error(json.error || res.statusText || 'Server request failed');
  }
  return res.json().catch(() => null);
}

// ─── High-level actions ───────────────────────────────────────

/**
 * Fetch config from the backend and apply view settings.
 * @param {Function} [renderColToggles]  Optional callback to render column toggles.
 */
export async function loadConfig(renderColToggles) {
  state.config = await api('GET', '/api/config');
  if (state.config.view_settings) {
    state.visibleCols = { ...state.visibleCols, ...state.config.view_settings };
  }
  if (state.config.sort_col !== undefined) {
    state.sortCol = state.config.sort_col;
  }
  if (state.config.sort_dir !== undefined) {
    state.sortDir = state.config.sort_dir;
  }
  if (renderColToggles) renderColToggles();
}

/**
 * Load cached bug data from the backend (no Bugzilla API call).
 * @param {Function} renderAll  Callback to re-render all views.
 */
export async function loadData(renderAll) {
  state.data = await api('GET', '/api/data');
  if (state.data) {
    setStatus('active', 'Loaded from cache');
    renderAll();
  }
}

/**
 * Trigger a full bug refresh via the backend (calls Bugzilla API).
 * @param {Function} renderAll       Callback to re-render all views.
 * @param {Function} startCountdown  Callback to restart the countdown timer.
 */
export async function doRefresh(renderAll, startCountdown) {
  setStatus('loading', 'Refreshing…');
  try {
    state.data = await api('POST', '/api/refresh');
    setStatus('active', 'Up to date');
    renderAll();
    startCountdown();
    toast('Bugs refreshed', 'success');
  } catch (e) {
    setStatus('error', 'Refresh failed');
    toast(e.message, 'error');
    // Still try to load cached data
    try {
      state.data = await api('GET', '/api/data');
      renderAll();
    } catch (_) { /* ignore */ }
  }
}

/**
 * Request the backend to stop the server.
 */
export async function stopServer() {
  if (!confirm('Stop backend server?')) return;
  setStatus('loading', 'Stopping backend…');
  try {
    await sendServerCommand('/api/stop');
    toast('Backend stopping…', 'success');
  } catch (e) {
    if (e.message.includes('Failed to fetch') || e.message.includes('NetworkError')) {
      toast('Backend stop requested', 'success');
    } else {
      setStatus('error', 'Stop failed');
      toast(e.message, 'error');
    }
  }
}

/**
 * Completely stop the server and wipe client data.
 */
export async function restartServer() {
  if (!confirm('Wipe all client data and completely stop the backend server?')) return;
  setStatus('loading', 'Wiping data and stopping server…');
  
  try {
    localStorage.clear();
    
    if ('serviceWorker' in navigator) {
      const registrations = await navigator.serviceWorker.getRegistrations();
      for (const registration of registrations) {
        await registration.unregister();
      }
    }
    
    if ('caches' in window) {
      const keys = await caches.keys();
      for (const key of keys) {
        await caches.delete(key);
      }
    }
  } catch (e) {
    console.error('Failed to wipe client data', e);
  }

  try {
    await sendServerCommand('/api/stop');
    document.body.innerHTML = '<div style="display:flex;align-items:center;justify-content:center;height:100vh;background:#0f172a;color:#fff;font-family:sans-serif;flex-direction:column;text-align:center;"><h1>Client Wiped & Server Stopped</h1><p style="color:#94a3b8;margin-top:10px;">You may now safely close this tab.</p></div>';
  } catch (e) {
    if (e.message.includes('Failed to fetch') || e.message.includes('NetworkError')) {
      document.body.innerHTML = '<div style="display:flex;align-items:center;justify-content:center;height:100vh;background:#0f172a;color:#fff;font-family:sans-serif;flex-direction:column;text-align:center;"><h1>Client Wiped & Server Stopped</h1><p style="color:#94a3b8;margin-top:10px;">You may now safely close this tab.</p></div>';
    } else {
      setStatus('error', 'Stop failed');
      toast(e.message, 'error');
    }
  }
}
