// ─── Local Sub-Priority System ────────────────────────────────
// Manages per-bug priority ordering stored in localStorage.
// Only applies to the "To Work" tab (assigned + reopened bugs).

import state from '../state/store.js';
import { LS_SUB_PRIO } from './constants.js';

/**
 * Read the sub-priority map from localStorage.
 * @returns {Object<string, number>} Map of bug ID → rank number.
 */
export function getLocalSubPrios() {
  try {
    return JSON.parse(localStorage.getItem(LS_SUB_PRIO)) || {};
  } catch (e) {
    return {};
  }
}

/**
 * Set (or delete) a single bug's sub-priority.
 */
export function setLocalSubPrio(bugId, val) {
  const p = getLocalSubPrios();
  if (val === null) delete p[String(bugId)];
  else p[String(bugId)] = val;
  localStorage.setItem(LS_SUB_PRIO, JSON.stringify(p));
}

/**
 * Swap a bug's rank with its neighbour.
 * @param {number} bugId
 * @param {number} dir  -1 = move up, +1 = move down
 * @param {Function} rerenderTable  callback to re-render the bug table
 */
export function moveSubPrio(bugId, dir, rerenderTable) {
  const subPrios = getLocalSubPrios();
  const myRank = subPrios[String(bugId)];
  if (myRank === undefined) return;
  const targetRank = myRank + dir;
  const swapId = Object.keys(subPrios).find(id => subPrios[id] === targetRank);
  if (!swapId) return; // already at boundary
  subPrios[String(bugId)] = targetRank;
  subPrios[swapId] = myRank;
  localStorage.setItem(LS_SUB_PRIO, JSON.stringify(subPrios));
  if (rerenderTable) rerenderTable();
}

/**
 * Return the sort value for a bug.  Bugs without a rank sort to the end.
 */
export function subPrioSortVal(bugId) {
  const sp = getLocalSubPrios()[String(bugId)];
  return (sp !== undefined && sp !== null) ? sp : 999999;
}

/**
 * Remove sub-priorities for bugs that are no longer in the "To Work" set.
 */
export function purgeNonAssignedPrios() {
  const assigned = state.data?.assigned_bugs || [];
  const reopened = (state.data?.all_bugs || []).filter(
    b => String(b.status).toUpperCase() === 'REOPENED'
  );
  const toWorkIds = new Set([...assigned, ...reopened].map(b => String(b.id)));
  let subPrios = getLocalSubPrios();
  let changed = false;
  Object.keys(subPrios).forEach(id => {
    if (!toWorkIds.has(id)) { delete subPrios[id]; changed = true; }
  });
  if (changed) {
    localStorage.setItem(LS_SUB_PRIO, JSON.stringify(subPrios));
  }
}

/**
 * Auto-assign ranks to newly-appeared bugs that don't have one yet.
 */
export function autoAssignSubPrios() {
  const assigned = state.data?.assigned_bugs || [];
  const reopened = (state.data?.all_bugs || []).filter(
    b => String(b.status).toUpperCase() === 'REOPENED'
  );
  const toWork = [...assigned, ...reopened];
  if (!toWork.length) return;
  const subPrios = getLocalSubPrios();
  const ranked = toWork.filter(
    b => subPrios[String(b.id)] !== undefined && subPrios[String(b.id)] !== null
  );
  const unranked = toWork.filter(
    b => subPrios[String(b.id)] === undefined || subPrios[String(b.id)] === null
  );
  if (!unranked.length) return;
  const maxRank = ranked.length
    ? Math.max(...ranked.map(b => subPrios[String(b.id)]))
    : 0;
  unranked.forEach((b, i) => { subPrios[String(b.id)] = maxRank + i + 1; });
  localStorage.setItem(LS_SUB_PRIO, JSON.stringify(subPrios));
}

/**
 * Compact ranks to 1..N with no gaps, preserving relative order.
 */
export function normaliseSubPrios() {
  const subPrios = getLocalSubPrios();
  const entries = Object.entries(subPrios).sort((a, b) => a[1] - b[1]);
  entries.forEach(([id], i) => { subPrios[id] = i + 1; });
  localStorage.setItem(LS_SUB_PRIO, JSON.stringify(subPrios));
}
