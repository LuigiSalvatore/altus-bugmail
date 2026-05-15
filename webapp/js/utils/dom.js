// ─── DOM Utilities ────────────────────────────────────────────
// HTML escaping and clipboard helpers used across the frontend.

import { toast } from '../ui/notifications.js';

/**
 * Escape a string for safe insertion into HTML.
 * Covers &, <, >, and double-quote characters.
 */
export function esc(s) {
  return String(s)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

/**
 * Copy a bug ID to the clipboard.
 * Stops event propagation so the table row click handler doesn't fire.
 */
export async function copyBugId(bugId, ev) {
  ev.stopPropagation();
  try {
    await navigator.clipboard.writeText(String(bugId));
    toast(`Copied: ${bugId}`, 'success');
  } catch (e) {
    toast('Copy failed', 'error');
  }
}

/**
 * Copy a bug's full name (BUG-{id} - {summary}) to the clipboard.
 * Stops event propagation so the table row click handler doesn't fire.
 */
export async function copyBugFullName(bugId, summary, ev) {
  ev.stopPropagation();
  const text = `BUG-${bugId} - ${summary}`;
  try {
    await navigator.clipboard.writeText(text);
    toast(`Copied: ${text}`, 'success');
  } catch (e) {
    toast('Copy failed', 'error');
  }
}
