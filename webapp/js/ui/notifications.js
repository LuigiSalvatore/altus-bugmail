// ─── Toast Notification System ────────────────────────────────
// Lightweight toast notifications displayed at the bottom-right.

/**
 * Show a brief toast message.
 * @param {string} msg   Text to display.
 * @param {'info'|'success'|'error'} type  Visual style.
 */
export function toast(msg, type = 'info') {
  const el = document.createElement('div');
  el.className = `toast ${type}`;
  el.innerHTML = `<div class="toast-dot"></div><span>${msg}</span>`;
  document.getElementById('toast-container').appendChild(el);
  setTimeout(() => el.remove(), 3500);
}
