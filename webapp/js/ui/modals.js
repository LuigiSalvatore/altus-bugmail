// ─── Modal Management ─────────────────────────────────────────
// Handles opening/closing of the Settings modal and the Add Bug (bug-picker) modal.
// The Manage Dropdown modal is handled by commitView.js since it's tightly coupled.

import state from '../state/store.js';
import { api } from '../api/client.js';
import { toast } from './notifications.js';
import { esc } from '../utils/dom.js';
import { statusBadgeClass } from '../render/templates.js';

// ─── Settings Modal ──────────────────────────────────────────

export function openSettings() {
  document.getElementById('input-url').value = state.config?.bugzilla_url || '';
  document.getElementById('input-email').value = state.config?.user_email || '';
  document.getElementById('input-apikey').value = '';
  document.getElementById('settings-overlay').classList.add('open');
}

export function closeSettings() {
  document.getElementById('settings-overlay').classList.remove('open');
}

/**
 * Wire up the settings modal events.
 * @param {Function} doRefresh  Callback to trigger a data refresh after saving.
 */
export function initSettingsModal(doRefresh) {
  document.getElementById('btn-save-settings').addEventListener('click', async () => {
    const body = {
      bugzilla_url: document.getElementById('input-url').value.trim(),
      user_email: document.getElementById('input-email').value.trim(),
      view_settings: state.visibleCols
    };
    const key = document.getElementById('input-apikey').value.trim();
    if (key) body.api_key = key;
    try {
      await api('POST', '/api/config', body);
      state.config = { ...state.config, ...body };
      closeSettings();
      toast('Settings saved', 'success');
      doRefresh();
    } catch (e) {
      toast(e.message, 'error');
    }
  });

  // Cancel button
  document.getElementById('btn-cancel-settings').addEventListener('click', closeSettings);

  // Close on overlay click
  document.getElementById('settings-overlay').addEventListener('click', e => {
    if (e.target === e.currentTarget) closeSettings();
  });
}

// ─── Bug Picker Modal ─────────────────────────────────────────

/**
 * Open the "Set Current Bug" dialog with a searchable bug list.
 */
export function openAddBugDialog() {
  document.getElementById('input-bug-id').value = '';
  document.getElementById('bug-picker-search').value = '';
  populateBugPicker('');
  document.getElementById('bug-id-overlay').classList.add('open');
  setTimeout(() => document.getElementById('bug-picker-search').focus(), 50);
}

export function closeBugIdDialog() {
  document.getElementById('bug-id-overlay').classList.remove('open');
}

/**
 * Populate the bug picker dropdown, filtered by a search query.
 * @param {string} filter  Search string (matches bug ID or summary).
 * @param {Function} setCurrentBug  Callback to set a bug as current.
 */
export function populateBugPicker(filter, setCurrentBug) {
  const list = document.getElementById('bug-picker-list');
  const seen = new Set();
  const allBugs = [];
  const sources = ['assigned_bugs', 'review_bugs', 'all_bugs'];
  sources.forEach(key => {
    (state.data?.[key] || []).forEach(b => {
      if (!seen.has(b.id)) { seen.add(b.id); allBugs.push(b); }
    });
  });
  const q = filter.toLowerCase().trim();
  const filtered = q
    ? allBugs.filter(b => String(b.id).includes(q) || (b.summary || '').toLowerCase().includes(q))
    : allBugs;
  const currentId = state.data?.current_bug?.id;
  if (!filtered.length) {
    list.innerHTML = '<div class="bug-picker-empty">No bugs found</div>';
    return;
  }
  list.innerHTML = filtered.slice(0, 50).map(b => `
    <div class="bug-picker-item${b.id == currentId ? ' is-current' : ''}" data-id="${b.id}">
      <span class="bug-picker-id">#${b.id}</span>
      <span class="bug-picker-summary">${esc(b.summary || '')}</span>
      <span class="badge ${statusBadgeClass(b.status)}" style="flex-shrink:0;font-size:9px;">${esc(b.status || '')}</span>
    </div>
  `).join('');
  list.querySelectorAll('.bug-picker-item').forEach(el => {
    el.addEventListener('click', () => {
      closeBugIdDialog();
      const id = el.dataset.id;
      if (state.data?.current_bug && state.data.current_bug.id != id) {
        if (!confirm(`Replace current bug #${state.data.current_bug.id} with #${id}?`)) return;
      }
      if (setCurrentBug) setCurrentBug(id);
    });
  });
}

/**
 * Wire up the bug-picker modal events.
 * @param {Function} setCurrentBug  Callback to set a bug as current.
 */
export function initBugPickerModal(setCurrentBug) {
  // Search input filters the list
  document.getElementById('bug-picker-search').addEventListener('input', e => {
    populateBugPicker(e.target.value, setCurrentBug);
  });

  // Manual bug ID confirmation
  document.getElementById('btn-confirm-bug-id').addEventListener('click', async () => {
    const id = document.getElementById('input-bug-id').value.trim();
    if (!id) return;
    closeBugIdDialog();
    await setCurrentBug(id);
  });

  // Enter key on the manual input
  document.getElementById('input-bug-id').addEventListener('keydown', e => {
    if (e.key === 'Enter') document.getElementById('btn-confirm-bug-id').click();
  });

  // Cancel button
  document.getElementById('btn-cancel-bug-id').addEventListener('click', closeBugIdDialog);

  // Close on overlay click
  document.getElementById('bug-id-overlay').addEventListener('click', e => {
    if (e.target === e.currentTarget) closeBugIdDialog();
  });
}
