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

export async function copyRichTextToClipboard(plainText, htmlText) {
    await navigator.clipboard.write([
        new ClipboardItem({
            'text/plain': new Blob(
                [plainText],
                { type: 'text/plain' }
            ),
            'text/html': new Blob(
                [htmlText],
                { type: 'text/html' }
            )
        })
    ]);
}

/**
 * Extract the numeric portion of a bug ID.
 */
export function extractNumericBugId(bugId) {
  const match = String(bugId).match(/(\d+)/);
  return match ? match[1] : '';
}

/**
 * Remove the bug ID prefix from a summary string.
 */
export function removeBugIdPrefix(summary, bugId) {
  if (!summary) return '';
  const escaped = String(bugId).replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  return summary
    .replace(new RegExp(`^${escaped}\\s*[-:]*\\s*`, 'i'), '')
    .trim();
}

/**
 * Build a markdown link for a bug ID and summary.
 */
export function buildBugMarkdownLink(bugId, summary) {
  const numericId = extractNumericBugId(bugId);
  if (!numericId) return '';
  const cleanSummary = removeBugIdPrefix(summary, bugId);
  return `[bug-${bugId}](https://vmbugzilla.altus.com.br/demandas/show_bug.cgi?id=${numericId}) - ${cleanSummary}`;
}

export function buildBugClipboardPayload(bugId, summary) {
    const numericId = extractNumericBugId(bugId);

    if (!numericId) {
        return null;
    }

    const cleanSummary = removeBugIdPrefix(summary, bugId);

    const url = `https://vmbugzilla.altus.com.br/demandas/show_bug.cgi?id=${numericId}`;

    return {
        plainText: `${bugId} - ${cleanSummary}`,
        htmlText: `<a href="${url}">${bugId}</a> - ${cleanSummary}`
    };
}
