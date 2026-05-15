// ─── Application Bootstrap ────────────────────────────────────
// Entry point for the Bugzilla Tracker frontend.
// Imports all modules, wires events, and runs the init sequence.

import state from './state/store.js';
import { loadConfig, loadData, doRefresh, stopServer, restartServer } from './api/client.js';
import { toast } from './ui/notifications.js';
import { setStatus } from './ui/statusbar.js';
import { startCountdown } from './ui/countdown.js';
import { initMainTabs, initSubTabs } from './ui/tabs.js';
import { openSettings, initSettingsModal, openAddBugDialog, initBugPickerModal } from './ui/modals.js';
import { renderCurrentBug, setCurrentBug, initCurrentBugActions } from './views/currentBugView.js';
import { renderBugTable, renderCounts, renderColToggles } from './views/bugTableView.js';
import { renderHoldList } from './views/holdView.js';
import { initCommitSystem } from './views/commitView.js';
import { loadLogs, initLogsView } from './views/logsView.js';
import { registerServiceWorker } from './pwa/register.js';
import {
  purgeNonAssignedPrios, autoAssignSubPrios, normaliseSubPrios
} from './utils/priorities.js';

// ─── Orchestrated render ──────────────────────────────────────

/**
 * Re-render all views.  Called after data changes.
 */
function renderAll() {
  purgeNonAssignedPrios();
  autoAssignSubPrios();
  normaliseSubPrios();
  renderCurrentBug();
  renderHoldList();
  renderBugTable();
  renderCounts();
}

// ─── Bound callbacks (avoid circular deps) ────────────────────

/** doRefresh with renderAll + startCountdown bound in. */
function triggerRefresh() {
  doRefresh(renderAll, () => startCountdown(triggerRefresh));
}

/** startCountdown with doRefresh bound in. */
function triggerCountdown() {
  startCountdown(triggerRefresh);
}

// ─── Init ─────────────────────────────────────────────────────

(async () => {
  try {
    // 1. Load configuration
    await loadConfig(() => renderColToggles());

    // 2. Load cached data
    await loadData(renderAll);

    // 3. Render column toggles
    renderColToggles();

    // 4. Initialise sub-systems
    initCommitSystem();
    initLogsView();

    // 5. Wire up tabs
    initMainTabs({ onLogsTab: loadLogs });
    initSubTabs(renderBugTable);

    // 6. Wire up modals
    initSettingsModal(triggerRefresh);
    initBugPickerModal((bugId) => setCurrentBug(bugId, renderBugTable));

    // 7. Wire up current-bug action buttons
    initCurrentBugActions({
      openAddBugDialog,
      renderBugTable,
      renderHoldList
    });

    // 8. Wire up header buttons
    document.getElementById('btn-refresh').addEventListener('click', triggerRefresh);
    document.getElementById('btn-stop').addEventListener('click', stopServer);
    document.getElementById('btn-restart').addEventListener('click', restartServer);
    document.getElementById('btn-settings').addEventListener('click', openSettings);

    // 8b. Wire the empty-state "Add Current Bug" button
    document.getElementById('btn-add-bug-empty').addEventListener('click', openAddBugDialog);

    // 9. Start countdown
    triggerCountdown();

    // 10. Decide whether to auto-refresh or show cached/config prompt
    if (state.config?.api_key && !state.config.api_key.startsWith('••••')) {
      triggerRefresh();
    } else if (state.data?.last_update) {
      setStatus('active', `Cached: ${state.data.last_update.slice(0, 16).replace('T', ' ')}`);
    } else {
      setStatus('error', 'Not configured — open Settings');
      openSettings();
    }
  } catch (e) {
    setStatus('error', 'Failed to load');
    toast(e.message, 'error');
  }
})();

// 11. Register service worker
registerServiceWorker();
