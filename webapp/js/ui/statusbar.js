// ─── Status Bar ───────────────────────────────────────────────
// Controls the status dot indicator and text in the status bar.

/**
 * Update the status bar dot colour and text.
 * @param {'active'|'loading'|'error'} dotState  CSS class for the status dot.
 * @param {string} text  Status text to display.
 */
export function setStatus(dotState, text) {
  document.getElementById('status-dot').className = dotState;
  document.getElementById('status-text').textContent = text;
}
