// ─── Bug Table View ───────────────────────────────────────────
// Renders the sortable, filterable bug table in the "All Bugs" panel.
// Includes column toggles, sub-tab counts, sorting, and drag-and-drop reordering.

import state from '../state/store.js';
import { api } from '../api/client.js';
import { esc, buildBugClipboardPayload, copyRichTextToClipboard } from '../utils/dom.js';
import { ALL_COLS, TAB_KEYS, COL_FIELD } from '../utils/constants.js';
import { statusBadgeClass } from '../render/templates.js';
import {
  getLocalSubPrios, subPrioSortVal, moveSubPrio
} from '../utils/priorities.js';
import { LS_SUB_PRIO } from '../utils/constants.js';

// ─── Drag-and-drop state ─────────────────────────────────────
let _dragBugId = null;

// ─── Column helpers ───────────────────────────────────────────

/** Compute the active column list (fixed + user-toggled). */
export function getActiveColumns() {
  const base = ['ID', 'Summary', 'Status'];
  return base.concat(ALL_COLS.filter(c => state.visibleCols[c]));
}

// ─── Priority badge HTML (for To Work tab) ────────────────────

function prioBadgeHTML(bugId) {
  const sp = getLocalSubPrios()[String(bugId)] ?? '?';
  const toWork = (state.data?.assigned_bugs || []).concat(
    (state.data?.all_bugs || []).filter(b => String(b.status).toUpperCase() === 'REOPENED')
  );
  const total = toWork.length;
  const atTop = sp === 1;
  const atBot = sp === total;
  return `<div class="lp-cell-wrap">
    <span class="drag-handle" title="Drag to reorder">⠿</span>
    <div class="sp-rank" onclick="event.stopPropagation()">
      <button class="sp-arrow${atTop ? ' sp-arrow-disabled' : ''}" data-prio-move="${bugId},-1" title="Move up" ${atTop ? 'disabled' : ''}>▲</button>
      <span class="lp-sub-badge lp-num">${sp}</span>
      <button class="sp-arrow${atBot ? ' sp-arrow-disabled' : ''}" data-prio-move="${bugId},1" title="Move down" ${atBot ? 'disabled' : ''}>▼</button>
    </div>
  </div>`;
}

// ─── Main table render ────────────────────────────────────────

/**
 * Render the bug table for the currently active sub-tab.
 */
export function renderBugTable() {
  const cols = getActiveColumns();
  const isToWork = state.activeTab === 'to_work';

  // Determine which bugs to show
  let bugsList = [];
  if (state.activeTab === 'assigned') {
    bugsList = state.data.assigned_bugs || [];
  } else if (state.activeTab === 'to_work') {
    const assigned = state.data.assigned_bugs || [];
    const reopened = (state.data.all_bugs || []).filter(
      b => String(b.status).toUpperCase() === 'REOPENED'
    );
    bugsList = assigned.concat(reopened);
  } else if (state.activeTab === 'reopened') {
    bugsList = (state.data.all_bugs || []).filter(
      b => String(b.status).toUpperCase() === 'REOPENED'
    );
  } else {
    bugsList = state.data?.[TAB_KEYS[state.activeTab]] || [];
  }

  // Sort
  let sorted = [...bugsList];
  if (state.sortCol) {
    const field = COL_FIELD[state.sortCol] || state.sortCol.toLowerCase();
    sorted.sort((a, b) => {
      if (isToWork) {
        const spd = subPrioSortVal(a.id) - subPrioSortVal(b.id);
        if (spd !== 0) return spd;
      }
      const av = String(a[field] || ''), bv = String(b[field] || '');
      return av.localeCompare(bv) * state.sortDir;
    });
  } else if (isToWork) {
    sorted.sort((a, b) => subPrioSortVal(a.id) - subPrioSortVal(b.id));
  }

  // ── Table head ──
  const thead = document.getElementById('bug-table-head');
  const pHead = isToWork ? `<th class="lp-th" title="Priority order">★ Prio</th>` : '';
  thead.innerHTML = `<tr>${pHead}${cols.map(c => {
    const cls = state.sortCol === c ? (state.sortDir === 1 ? 'sort-asc' : 'sort-desc') : '';
    return `<th class="${cls}" data-col="${c}">${c}</th>`;
  }).join('')}</tr>`;
  thead.querySelectorAll('th[data-col]').forEach(th =>
    th.addEventListener('click', () => {
      if (state.sortCol === th.dataset.col) state.sortDir *= -1;
      else { state.sortCol = th.dataset.col; state.sortDir = 1; }
      renderBugTable();
    })
  );

  // ── Table body ──
  const baseUrl = (state.config?.bugzilla_url || '').replace(/\/+$/, '');
  document.getElementById('bug-table-body').innerHTML = sorted.map(bug => {
    const escapedSummary = esc(bug.summary || '').replace(/'/g, "\\'");
    const isCurrent = state.data?.current_bug?.id == bug.id;
    return `
    <tr data-id="${bug.id}" data-url="${baseUrl}/show_bug.cgi?id=${bug.id}"${isToWork ? ' draggable="true"' : ''}>
      ${isToWork ? `<td class="lp-cell">${prioBadgeHTML(bug.id)}</td>` : ''}
      ${cols.map(c => {
      if (c === 'ID') return `<td><div class="bug-id-cell"><span>${bug.id}</span><button class="copy-btn" data-copy-full="${bug.id}" data-copy-summary="${escapedSummary}" title="Copy full name"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg></button><button class="copy-btn" data-copy-id="${bug.id}" title="Copy bug ID"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 4h12v12H4z"/><path d="M8 8h12v12H8z"/></svg></button><button class="copy-btn" data-copy-link="${bug.id}" data-copy-summary="${escapedSummary}" title="Copy link as name"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/></svg></button><button class="copy-btn set-current-btn${isCurrent ? ' is-current' : ''}" data-set-current="${bug.id}" title="${isCurrent ? 'Currently working on' : 'Set as current bug'}"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg></button></div></td>`;
      if (c === 'Summary') return `<td class="col-summary"><div class="cell-truncate">${esc(bug.summary || '')}</div></td>`;
      if (c === 'Status') return `<td><span class="badge ${statusBadgeClass(bug.status)}">${esc(bug.status || '')}</span></td>`;
      const field = COL_FIELD[c] || c.toLowerCase();
      return `<td><div class="cell-truncate">${esc(bug[field] || '')}</div></td>`;
    }).join('')}
    </tr>`;
  }).join('');

  // ── Wire up row events ──
  _attachRowEvents(baseUrl);

  // ── Wire up inline button events ──
  _attachButtonEvents();

  // ── Drag-and-drop (To Work tab only) ──
  if (isToWork) _initDragReorder();
}

// ─── Event wiring helpers ─────────────────────────────────────

function _attachRowEvents(baseUrl) {
  document.querySelectorAll('#bug-table-body tr').forEach(tr => {
    tr.addEventListener('dblclick', () => window.open(tr.dataset.url, '_blank'));
    tr.addEventListener('keydown', e => { if (e.key === 'Enter') window.open(tr.dataset.url, '_blank'); });
    tr.setAttribute('tabindex', '0');
  });
}

function _attachButtonEvents() {
  const { toast } = _lazyToast();

  // Copy full name buttons
  document.querySelectorAll('[data-copy-full]').forEach(btn => {
    btn.addEventListener('click', async (ev) => {
      ev.stopPropagation();
      const bugId = btn.dataset.copyFull;
      const summary = btn.dataset.copySummary;
      const text = `BUG-${bugId} - ${summary}`;
      try { await navigator.clipboard.writeText(text); toast(`Copied: ${text}`, 'success'); }
      catch (e) { toast('Copy failed', 'error'); }
    });
  });

  // Copy ID buttons
  document.querySelectorAll('[data-copy-id]').forEach(btn => {
    btn.addEventListener('click', async (ev) => {
      ev.stopPropagation();
      const bugId = btn.dataset.copyId;
      try { await navigator.clipboard.writeText(String(bugId)); toast(`Copied: ${bugId}`, 'success'); }
      catch (e) { toast('Copy failed', 'error'); }
    });
  });

  // Copy link as name buttons
  document.querySelectorAll('[data-copy-link]').forEach(btn => {
    btn.addEventListener('click', async (ev) => {
      ev.stopPropagation();
      const bugId = btn.dataset.copyLink;
      const summary = btn.dataset.copySummary;
      
      const payload = buildBugClipboardPayload(bugId, summary);
      
      if (!payload) {
        toast('Unable to extract numeric bug ID', 'error');
        return;
      }
      
      try {
        await copyRichTextToClipboard(payload.plainText, payload.htmlText);
        toast('Copied bug link', 'success');
      } catch (e) { 
        toast('Copy failed', 'error'); 
      }
    });
  });

  // Set as current bug buttons
  document.querySelectorAll('[data-set-current]').forEach(btn => {
    btn.addEventListener('click', async (ev) => {
      ev.stopPropagation();
      const bugId = btn.dataset.setCurrent;
      if (state.data?.current_bug?.id == bugId) { toast('Already the current bug', 'info'); return; }
      if (state.data?.current_bug && !confirm(`Replace current bug #${state.data.current_bug.id} with #${bugId}?`)) return;
      // Lazy import to avoid circular dependency
      const { setCurrentBug } = await import('./currentBugView.js');
      await setCurrentBug(bugId, renderBugTable);
    });
  });

  // Priority move buttons
  document.querySelectorAll('[data-prio-move]').forEach(btn => {
    btn.addEventListener('click', (ev) => {
      ev.stopPropagation();
      const [bugId, dir] = btn.dataset.prioMove.split(',');
      moveSubPrio(parseInt(bugId), parseInt(dir), renderBugTable);
    });
  });
}

/** Lazy-load the toast function to avoid import ordering issues. */
function _lazyToast() {
  // Import is already available via static import at the module level
  // but we inline it here for the dynamically-wired handlers.
  let _toast = null;
  return {
    toast: (msg, type) => {
      if (!_toast) {
        // Synchronous fallback — the module is already loaded
        const el = document.createElement('div');
        el.className = `toast ${type}`;
        el.innerHTML = `<div class="toast-dot"></div><span>${msg}</span>`;
        document.getElementById('toast-container').appendChild(el);
        setTimeout(() => el.remove(), 3500);
      } else {
        _toast(msg, type);
      }
    }
  };
}

// ─── Drag-and-Drop Reordering ─────────────────────────────────

function _initDragReorder() {
  const tbody = document.getElementById('bug-table-body');
  const rows = tbody.querySelectorAll('tr[draggable="true"]');

  rows.forEach(tr => {
    tr.addEventListener('dragstart', e => {
      _dragBugId = tr.dataset.id;
      tr.classList.add('dragging');
      e.dataTransfer.effectAllowed = 'move';
      const ghost = tr.cloneNode(true);
      ghost.style.cssText = 'position:absolute;top:-9999px;opacity:0.7;background:var(--bg-elevated);';
      document.body.appendChild(ghost);
      e.dataTransfer.setDragImage(ghost, 0, 0);
      requestAnimationFrame(() => ghost.remove());
    });

    tr.addEventListener('dragend', () => {
      _dragBugId = null;
      tr.classList.remove('dragging');
      tbody.querySelectorAll('.drag-over-top,.drag-over-bottom').forEach(el => {
        el.classList.remove('drag-over-top', 'drag-over-bottom');
      });
    });

    tr.addEventListener('dragover', e => {
      e.preventDefault();
      e.dataTransfer.dropEffect = 'move';
      if (!_dragBugId || tr.dataset.id === _dragBugId) return;
      const rect = tr.getBoundingClientRect();
      const midY = rect.top + rect.height / 2;
      tbody.querySelectorAll('.drag-over-top,.drag-over-bottom').forEach(el => {
        el.classList.remove('drag-over-top', 'drag-over-bottom');
      });
      if (e.clientY < midY) {
        tr.classList.add('drag-over-top');
      } else {
        tr.classList.add('drag-over-bottom');
      }
    });

    tr.addEventListener('dragleave', () => {
      tr.classList.remove('drag-over-top', 'drag-over-bottom');
    });

    tr.addEventListener('drop', e => {
      e.preventDefault();
      if (!_dragBugId || tr.dataset.id === _dragBugId) return;
      const targetId = tr.dataset.id;
      const rect = tr.getBoundingClientRect();
      const midY = rect.top + rect.height / 2;
      const insertBefore = e.clientY < midY;

      const subPrios = getLocalSubPrios();
      const dragRank = subPrios[String(_dragBugId)];
      const targetRank = subPrios[String(targetId)];
      if (dragRank === undefined || targetRank === undefined) return;

      const ordered = Object.entries(subPrios).sort((a, b) => a[1] - b[1]);
      const dragIdx = ordered.findIndex(([id]) => id === String(_dragBugId));
      const [dragEntry] = ordered.splice(dragIdx, 1);
      let targetIdx = ordered.findIndex(([id]) => id === String(targetId));
      if (!insertBefore) targetIdx += 1;
      ordered.splice(targetIdx, 0, dragEntry);
      ordered.forEach(([id], i) => { subPrios[id] = i + 1; });
      localStorage.setItem(LS_SUB_PRIO, JSON.stringify(subPrios));

      _dragBugId = null;
      renderBugTable();

      // Inline toast
      const el = document.createElement('div');
      el.className = 'toast success';
      el.innerHTML = '<div class="toast-dot"></div><span>Priority reordered</span>';
      document.getElementById('toast-container').appendChild(el);
      setTimeout(() => el.remove(), 3500);
    });
  });
}

// ─── Counts ───────────────────────────────────────────────────

/**
 * Update the badge counts on each sub-tab.
 */
export function renderCounts() {
  if (!state.data) return;
  const el = id => document.getElementById(id);
  el('count-to_work').textContent =
    ((state.data.assigned_bugs || []).length +
      (state.data.all_bugs || []).filter(b => String(b.status).toUpperCase() === 'REOPENED').length);
  el('count-assigned').textContent = (state.data.assigned_bugs || []).length;
  el('count-review').textContent = (state.data.review_bugs || []).length;
  el('count-reopened').textContent =
    (state.data.all_bugs || []).filter(b => String(b.status).toUpperCase() === 'REOPENED').length;
  el('count-resolved_fixed').textContent = (state.data.resolved_fixed_bugs || []).length;
  el('count-resolved_implemented').textContent = (state.data.resolved_implemented_bugs || []).length;
  el('count-all').textContent = (state.data.all_bugs || []).length;
}

// ─── Column Toggles ──────────────────────────────────────────

/**
 * Render the column visibility toggle buttons.
 */
export function renderColToggles() {
  const c = document.getElementById('col-toggles');
  c.innerHTML = ALL_COLS.map(col => `
    <button class="col-toggle ${state.visibleCols[col] ? 'on' : ''}" data-col="${col}">${col}</button>
  `).join('');
  c.querySelectorAll('.col-toggle').forEach(btn =>
    btn.addEventListener('click', () => {
      const col = btn.dataset.col;
      state.visibleCols[col] = !state.visibleCols[col];
      btn.classList.toggle('on', state.visibleCols[col]);
      renderBugTable();
      api('POST', '/api/config', { view_settings: state.visibleCols });
    })
  );
}
