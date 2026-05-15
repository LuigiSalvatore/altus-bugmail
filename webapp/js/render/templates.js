// ─── Shared Rendering Helpers ─────────────────────────────────
// Template helpers and badge utilities used by multiple view modules.

/**
 * Return the CSS badge class for a bug status string.
 * @param {string} s  Bug status (e.g. 'ASSIGNED', 'RESOLVED').
 * @returns {string}  CSS class name.
 */
export function statusBadgeClass(s) {
  if (!s) return 'badge-default';
  s = s.toUpperCase();
  if (s === 'ASSIGNED')  return 'badge-assigned';
  if (s === 'RESOLVED')  return 'badge-resolved';
  if (s === 'NEW' || s === 'UNCONFIRMED') return 'badge-new';
  if (s === 'REOPENED')  return 'badge-reopened';
  return 'badge-default';
}
