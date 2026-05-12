// Logging system for Bugzilla Tracker Webapp
// Levels: debug, info, warning, error

const LOG_LEVELS = ['debug', 'info', 'warning', 'error'];
const LOG_COLORS = {
  debug: '#b3b3b3',
  info: '#4a90e2',
  warning: '#f5a623',
  error: '#d0021b'
};

let logs = [];

function logMessage(level, message) {
  if (!LOG_LEVELS.includes(level)) level = 'info';
  const entry = {
    level,
    message,
    time: new Date().toLocaleTimeString()
  };
  logs.push(entry);
  if (logs.length > 500) logs.shift();
  renderLogs();
}

function getLogs() {
  return logs;
}

function clearLogs() {
  logs = [];
  renderLogs();
}

function renderLogs() {
  const logPanel = document.getElementById('panel-logs');
  if (!logPanel) return;
  logPanel.innerHTML = logs.length ? logs.map(l =>
    `<div class="log-entry log-${l.level}">
      <span class="log-time">${l.time}</span>
      <span class="log-dot" style="background:${LOG_COLORS[l.level]}"></span>
      <span class="log-level">${l.level.toUpperCase()}</span>
      <span class="log-msg">${l.message}</span>
    </div>`
  ).join('') : '<div class="log-empty">No logs yet.</div>';
}

// Expose globally
window.logMessage = logMessage;
window.getLogs = getLogs;
window.clearLogs = clearLogs;
