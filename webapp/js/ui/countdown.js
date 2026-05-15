// ─── Countdown Timer ──────────────────────────────────────────
// Manages the 60-second auto-refresh countdown displayed in the status bar.

import state from '../state/store.js';

/** Handle for the active interval so we can clear it. */
let _cdTimer = null;

/**
 * (Re)start the countdown from 60 seconds.
 * When it reaches 0, triggers the provided refresh callback and restarts.
 * @param {Function} onZero  Callback invoked when countdown reaches zero.
 */
export function startCountdown(onZero) {
  if (_cdTimer) clearInterval(_cdTimer);
  state.countdown = 60;
  document.getElementById('countdown').textContent = '60';
  _cdTimer = setInterval(() => {
    state.countdown--;
    document.getElementById('countdown').textContent = state.countdown;
    if (state.countdown <= 0) {
      state.countdown = 60;
      if (onZero) onZero();
    }
  }, 1000);
}
