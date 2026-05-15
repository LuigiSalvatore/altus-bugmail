# File Index

Complete inventory of every file in the project with its purpose, responsibilities, and dependencies.

---

## Entry Points

| File | Purpose | Dependencies | Side Effects |
|------|---------|-------------|--------------|
| `server.py` | Application entry point | `backend`, `logger` | Binds ports 5000+5001, opens browser, starts thread |
| `launch.vbs` | Silent Windows launcher | `server.py` | Runs pythonw.exe (no console) |
| `run_tracker.bat` | Console launcher | `server.py` | Opens console window |

---

## Backend Package (`backend/`)

| File | Purpose | Exports | Dependencies |
|------|---------|---------|-------------|
| `__init__.py` | Flask app factory | `create_app()` | `routes`, Flask |
| `routes/__init__.py` | Blueprint registration | `register_routes()` | All route modules |
| `routes/config.py` | Config API endpoints | Blueprint `config` | `state`, `persistence` |
| `routes/data.py` | Data & refresh endpoints | Blueprint `data` | `state`, `bugzilla_service` |
| `routes/bugs.py` | Bug CRUD & hold endpoints | Blueprint `bugs` | `state`, `bugzilla_service`, `persistence` |
| `routes/logs.py` | Log viewer endpoint | Blueprint `logs` | `logger` |
| `routes/server_control.py` | Stop/restart endpoints | Blueprint `server_control` | `server_lifecycle` |
| `services/persistence.py` | JSON file I/O | `load_config`, `save_config`, `load_data`, `save_data` | `json`, `os` |
| `services/state.py` | Thread-safe state | `get_state()` | `persistence` |
| `services/bugzilla_service.py` | Bugzilla API wrapper | `create_client`, `normalize_bug`, `fetch_bugs`, `do_refresh` | `apiBugzilla`, `logger` |
| `utils/server_lifecycle.py` | Process management | `shutdown_server`, `spawn_server_process` | `subprocess`, `flask.request` |

---

## Core Libraries

| File | Purpose | Exports | Dependencies |
|------|---------|---------|-------------|
| `apiBugzilla.py` | Bugzilla REST client | `Bugzilla` class | `requests` |
| `logger.py` | Logging setup | `logger`, `LOG_FILE` | `logging` |

---

## Frontend (`webapp/`)

| File | Purpose | Exports | Dependencies |
|------|---------|---------|-------------|
| `index.html` | HTML layout (zero JS) | — | `style.css`, `js/app.js` |
| `style.css` | Design system (CSS vars + components) | — | — |
| `sw.js` | Service worker | — | — |
| `manifest.json` | PWA manifest | — | — |

### JavaScript Modules (`webapp/js/`)

| File | Purpose | Key Exports |
|------|---------|-------------|
| `app.js` | Bootstrap + orchestration | `renderAll()` (internal) |
| `api/client.js` | HTTP communication | `api()`, `doRefresh()`, `loadConfig()`, `loadData()`, `stopServer()`, `restartServer()` |
| `state/store.js` | Centralized state | `state` (default export) |
| `ui/tabs.js` | Tab navigation | `initMainTabs()`, `initSubTabs()` |
| `ui/modals.js` | Modal management | `openSettings()`, `openAddBugDialog()`, `initSettingsModal()`, `initBugPickerModal()` |
| `ui/notifications.js` | Toast system | `toast()` |
| `ui/countdown.js` | Refresh timer | `startCountdown()` |
| `ui/statusbar.js` | Status indicator | `setStatus()` |
| `views/currentBugView.js` | Current bug card | `renderCurrentBug()`, `setCurrentBug()`, `initCurrentBugActions()` |
| `views/bugTableView.js` | Bug table | `renderBugTable()`, `renderCounts()`, `renderColToggles()` |
| `views/holdView.js` | Hold list | `renderHoldList()` |
| `views/commitView.js` | Commit prompt system | `initCommitSystem()`, `autoFillBug()` |
| `views/logsView.js` | Log viewer | `loadLogs()`, `initLogsView()` |
| `render/templates.js` | Shared HTML helpers | `statusBadgeClass()` |
| `utils/constants.js` | Shared constants | `ALL_COLS`, `TAB_KEYS`, `COL_FIELD`, `LS_*`, `DEF_*` |
| `utils/dom.js` | DOM utilities | `esc()`, `copyBugId()`, `copyBugFullName()` |
| `utils/priorities.js` | Priority system | `getLocalSubPrios()`, `moveSubPrio()`, `purgeNonAssignedPrios()`, `autoAssignSubPrios()`, `normaliseSubPrios()` |
| `pwa/register.js` | SW registration | `registerServiceWorker()` |

---

## Data Files

| File | Purpose | Format |
|------|---------|--------|
| `data/bugzilla_config.json` | API credentials + preferences | JSON |
| `data/bugzilla_data.json` | Cached bug lists + current bug state | JSON |
| `logs/bugmail.log` | Application log | Text (timestamp + level + message) |

---

## Scripts & Deployment

| File | Purpose |
|------|---------|
| `install_startup.bat` | Install Windows Task Scheduler entry for auto-start |
| `uninstall_startup.bat` | Remove the Task Scheduler entry |
| `run_tracker.bat` | Manual console launch |
| `launch.vbs` | Silent launch for Task Scheduler |

---

## Tests

| File | Purpose |
|------|---------|
| `validate_imports.py` | Verify all project imports resolve correctly |
| `test_endpoints.py` | Test Bugzilla REST API endpoint discovery |
| `test_auth.py` | Test Bugzilla authentication methods |
| `test_noauth.py` | Test unauthenticated Bugzilla access |
