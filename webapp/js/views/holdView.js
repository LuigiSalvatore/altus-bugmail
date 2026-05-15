// ─── Hold View ────────────────────────────────────────────────
// Renders the "On Hold" bugs list and handles resume-from-hold.

import state from '../state/store.js';
import { api } from '../api/client.js';
import { toast } from '../ui/notifications.js';
import { esc } from '../utils/dom.js';
import { renderCurrentBug } from './currentBugView.js';

/**
 * Render the on-hold bug list.
 */
export function renderHoldList() {
  const list = document.getElementById('hold-list');
  const bugs = state.data?.on_hold_bugs || [];
  if (!bugs.length) {
    list.innerHTML = '<div class="hold-empty">No bugs on hold</div>';
    return;
  }
  list.innerHTML = bugs.map((b, i) => `
    <div class="hold-item">
      <div class="hold-item-info">
        <div class="hold-item-id">#${b.id}</div>
        <div class="hold-item-summary">${esc(b.summary || '')}</div>
      </div>
      <button class="btn btn-outline btn-sm" data-hold-index="${i}">Make Current</button>
    </div>`).join('');

  // Wire up the "Make Current" buttons
  list.querySelectorAll('[data-hold-index]').forEach(btn => {
    btn.addEventListener('click', () => removeFromHold(parseInt(btn.dataset.holdIndex)));
  });
}

/**
 * Remove a bug from hold and make it the current bug.
 * @param {number} index  Index into the on_hold_bugs array.
 */
async function removeFromHold(index) {
  if (state.data?.current_bug) {
    if (!confirm('Replace current bug with this one?')) return;
  }
  try {
    const bug = await api('DELETE', `/api/hold/${index}`);
    state.data.current_bug = bug;
    state.data.on_hold_bugs.splice(index, 1);
    renderCurrentBug();
    renderHoldList();
    toast(`Bug #${bug.id} is now current`, 'success');
  } catch (e) {
    toast(e.message, 'error');
  }
}
