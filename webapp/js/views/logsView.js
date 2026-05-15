// ─── Logs View ────────────────────────────────────────────────
// Fetches and displays server log entries.

import { api } from '../api/client.js';
import { toast } from '../ui/notifications.js';

/**
 * Fetch server logs and render them into the logs panel.
 */
export function loadLogs() {
  api('GET', '/api/logs')
    .then(entries => {
      const container = document.getElementById('logs-section');
      container.innerHTML = entries
        .map(e => `<div><span>${e.ts}</span> <strong>${e.level}</strong> ${e.msg}</div>`)
        .join('');
    })
    .catch(e => toast(e.message, 'error'));
}

/**
 * Wire up the clear-logs button.
 */
export function initLogsView() {
  const btn = document.getElementById('btn-clear-logs');
  if (btn) {
    btn.addEventListener('click', () => {
      document.getElementById('logs-section').innerHTML = '';
      toast('Logs cleared (UI only)', 'info');
    });
  }
}
