// ─── Current Bug View ─────────────────────────────────────────
// Renders the "Current Bug" card and handles bug-related actions
// (set current, complete, put on hold).

import state from '../state/store.js';
import { api } from '../api/client.js';
import { toast } from '../ui/notifications.js';
import { setStatus } from '../ui/statusbar.js';
import { esc } from '../utils/dom.js';
import { statusBadgeClass } from '../render/templates.js';
import { getLocalSubPrios } from '../utils/priorities.js';
import { LS_SUB_PRIO as _LS } from '../utils/constants.js';

/**
 * Render the current bug card (or the empty-state placeholder).
 */
export function renderCurrentBug() {
  const bug = state.data?.current_bug;
  const empty = document.getElementById('current-bug-empty');
  const details = document.getElementById('current-bug-details');
  if (!bug) {
    empty.style.display = 'flex';
    details.style.display = 'none';
    return;
  }
  empty.style.display = 'none';
  details.style.display = 'flex';

  document.getElementById('current-bug-id').textContent = `#${bug.id}`;
  document.getElementById('current-bug-id').className = 'badge badge-assigned';

  const sb = document.getElementById('current-bug-status-badge');
  sb.textContent = bug.status || '';
  sb.className = `badge ${statusBadgeClass(bug.status)}`;

  document.getElementById('current-bug-summary').innerHTML =
    `<div id="current-bug-summary" style="font-size:16px;font-weight:600;color:var(--text-primary);letter-spacing:-0.01em;margin-bottom:12px;line-height:1.4;">${esc(bug.summary || '')}</div>`;

  const baseUrl = (state.config?.bugzilla_url || '').replace(/\/+$/, '');
  document.getElementById('current-bug-link').href = `${baseUrl}/show_bug.cgi?id=${bug.id}`;

  const meta = [
    ['Priority', bug.priority], ['Severity', bug.severity], ['Assignee', bug.assigned_to],
    ['Product', bug.product], ['Activity', bug.activity], ['Sub-Activity', bug.sub_activity],
    ['Importance', bug.importance], ['Version', bug.version], ['Deadline', bug.deadline]
  ];
  document.getElementById('current-bug-meta').innerHTML = meta.map(([l, v]) => v ? `
    <div class="bug-meta-item">
      <div class="bug-meta-label">${l}</div>
      <div class="bug-meta-value">${esc(v)}</div>
    </div>` : '').join('');

  document.getElementById('current-bug-desc').textContent = bug.description || 'No description.';

  const comments = bug.comments || [];
  const cl = document.getElementById('comments-label');
  cl.style.display = comments.length ? '' : 'none';
  document.getElementById('current-bug-comments').innerHTML = comments.map(c => `
    <div class="comment-item">
      <div class="comment-meta">
        <span class="comment-author">${esc(c.author || '')}</span>
        <span>${esc(c.creation_time || '')}</span>
      </div>
      <div class="comment-text">${esc(c.text || '')}</div>
    </div>`).join('');
}

/**
 * Set a bug as the current working bug by ID.
 * @param {string|number} bugId
 * @param {Function} [renderBugTable]  Optional callback to re-render the table.
 */
export async function setCurrentBug(bugId, renderBugTable) {
  setStatus('loading', `Fetching bug #${bugId}…`);
  try {
    const bug = await api('POST', '/api/current-bug', { bug_id: bugId });
    state.data = state.data || {};
    state.data.current_bug = bug;
    renderCurrentBug();
    if (renderBugTable) renderBugTable();
    setStatus('active', 'Up to date');
    toast(`Bug #${bugId} set as current`, 'success');
  } catch (e) {
    setStatus('error', e.message);
    toast(e.message, 'error');
  }
}

/**
 * Set a bug as current from the table (with confirmation if one already exists).
 * Exposed on window for inline onclick handlers in generated HTML.
 */
export async function setCurrentFromTable(bugId, ev, renderBugTable) {
  ev.stopPropagation();
  if (state.data?.current_bug?.id == bugId) {
    toast('Already the current bug', 'info');
    return;
  }
  if (state.data?.current_bug && !confirm(`Replace current bug #${state.data.current_bug.id} with #${bugId}?`)) return;
  await setCurrentBug(bugId, renderBugTable);
}

/**
 * Wire up the current-bug action buttons.
 * @param {Object} callbacks
 * @param {Function} callbacks.openAddBugDialog
 * @param {Function} callbacks.renderBugTable
 * @param {Function} callbacks.renderHoldList
 */
export function initCurrentBugActions({ openAddBugDialog, renderBugTable, renderHoldList }) {
  document.getElementById('btn-add-bug').addEventListener('click', openAddBugDialog);

  document.getElementById('btn-complete').addEventListener('click', async () => {
    if (!state.data?.current_bug) { toast('No current bug', 'error'); return; }
    const completedId = state.data.current_bug.id;
    if (!confirm(`Complete bug #${completedId}?`)) return;
    try {
      const subPrios = getLocalSubPrios();
      const completedSP = subPrios[String(completedId)];
      if (completedSP !== undefined && completedSP !== null) {
        delete subPrios[String(completedId)];
        Object.keys(subPrios).forEach(id => {
          if (subPrios[id] > completedSP) subPrios[id] -= 1;
        });
        localStorage.setItem(_LS, JSON.stringify(subPrios));
      }
      await api('DELETE', '/api/current-bug');
      state.data.current_bug = null;
      renderCurrentBug();
      renderBugTable();
      toast('Bug completed — sub-priorities updated', 'success');
    } catch (e) { toast(e.message, 'error'); }
  });

  document.getElementById('btn-hold').addEventListener('click', async () => {
    if (!state.data?.current_bug) { toast('No current bug to hold', 'error'); return; }
    try {
      await api('POST', '/api/hold');
      const bug = state.data.current_bug;
      state.data.on_hold_bugs = state.data.on_hold_bugs || [];
      state.data.on_hold_bugs.push(bug);
      state.data.current_bug = null;
      renderCurrentBug();
      renderHoldList();
      toast(`Bug #${bug.id} put on hold`, 'info');
    } catch (e) { toast(e.message, 'error'); }
  });
}
