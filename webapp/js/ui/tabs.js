// ─── Tab Navigation ───────────────────────────────────────────
// Handles main sidebar tab switching and sub-tab switching in the All Bugs panel.

import state from '../state/store.js';

/**
 * Initialise main tab switching (Current Bug / All Bugs / Commit / Logs).
 * @param {Object} callbacks
 * @param {Function} callbacks.onLogsTab  Called when the Logs tab is activated.
 */
export function initMainTabs({ onLogsTab }) {
  document.querySelectorAll('.tab-btn').forEach(btn =>
    btn.addEventListener('click', () => {
      document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
      document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
      btn.classList.add('active');
      document.getElementById(`panel-${btn.dataset.panel}`).classList.add('active');
      state.activeTab = btn.dataset.panel;
      if (state.activeTab === 'logs' && onLogsTab) onLogsTab();
    })
  );
}

/**
 * Initialise sub-tab switching inside the All Bugs panel.
 * @param {Function} renderBugTable  Callback to re-render the bug table.
 */
export function initSubTabs(renderBugTable) {
  document.querySelectorAll('.sub-tab').forEach(btn =>
    btn.addEventListener('click', () => {
      document.querySelectorAll('.sub-tab').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      state.activeTab = btn.dataset.tab;
      state.sortCol = null;
      renderBugTable();
    })
  );
}
