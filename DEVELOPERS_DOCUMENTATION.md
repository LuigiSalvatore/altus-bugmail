# 1. System Overview

**Purpose** – A lightweight Bugzilla tracking UI that runs locally as a Flask web server (or as a legacy Tkinter desktop app) and communicates with a remote Bugzilla REST endpoint.
**Major subsystems**

| Subsystem | Description |
|---|---|
| **Flask backend (`server.py`)** | Serves static SPA assets, provides JSON REST endpoints for configuration, data refresh, bug CRUD, and server control. |
| **Bugzilla client (`apiBugzilla.py`)** | Thin wrapper around Bugzilla’s REST API (GET `bug`, `bug/<id>`, comments, etc.). |
| **Tkinter desktop UI (`bugzilla_tracker.py`)** | Optional legacy GUI that mirrors the web UI behavior for local use. |
| **Web SPA (`webapp/index.html` + JS)** | Rich single‑page application: bug tables, current‑bug view, hold list, priority handling, and commit‑prompt pane. |
| **Auto‑refresh thread** | Background thread (in both back‑end and desktop UI) that periodically pulls bug data (default 60 s). |
| **Startup / single‑instance guard** | Socket guard ensures only one Flask server instance runs (port 5001). |

**Runtime architecture**
```
+-------------------+        HTTP (JSON)         +--------------------+
|  Browser / UI (SPA) | <----------------------> | Flask server (Python) |
+-------------------+                           +--------------------+
          |                                            |
          | uses                                       | uses
          v                                            v
   apiBugzilla client --------------------> Remote Bugzilla REST API
```

**Main execution flow**
1. **Start** – `server.py` acquires lock socket → launches Flask + auto‑refresh thread.
2. **Load config & persisted data** from JSON files.
3. **Serve SPA** (`/`) and static assets from `webapp/`.
4. **Client actions** (e.g. refresh, set current bug) call Flask endpoints (`/api/*`).
5. **Flask handlers** invoke `apiBugzilla` to query/update Bugzilla, update in‑memory state, persist to `bugzilla_data.json`.
6. **Auto‑refresh** thread repeats step 4 every 60 s.
7. **Shutdown** – `/api/stop` or user closing UI triggers graceful server termination.

**Important services / tasks**
| Service / Task | Role |
|---|---|
| `auto_refresh_loop` (thread) | Periodic data refresh from Bugzilla. |
| `api/refresh` endpoint | On‑demand refresh of all bug lists. |
| `api/current-bug` (POST/DELETE) | Set / clear the “current bug”. |
| `api/hold` (POST/DELETE) | Move bugs to/from the hold list. |
| `api/stop` / `api/restart` | Remote control of the Flask process. |
| `single‑instance guard` | Prevents multiple servers on same port. |

**External interfaces** – HTTP (REST) to Bugzilla (`https://…/rest/`), local HTTP API (`/api/*`), optional Windows Task Scheduler/VBScript for background startup, and the SPA’s WebSocket‑free AJAX calls.

---
# 2. Directory / Module Map

## `.` (project root)

**Purpose** – Container for source, configuration, data, and deployment scripts.

| File | Purpose |
|---|---|
| `server.py` | Flask backend, API routes, auto‑refresh, single‑instance guard. |
| `apiBugzilla.py` | Minimal Bugzilla REST client wrapper. |
| `bugzilla_tracker.py` | Legacy Tkinter desktop UI (mirrors web UI functionality). |
| `bugzilla_config.json` | Persistent user configuration (URL, API key, email, view settings). |
| `bugzilla_data.json` | Cached bug data and UI state (current bug, on‑hold list, etc.). |
| `requirements.txt` | Python dependencies (`Flask`, `requests`, …). |
| `webapp/` | SPA static assets (`index.html`, `style.css`, `manifest.json`, `sw.js`). |
| `run_tracker.bat` / `install_startup.bat` / `uninstall_startup.bat` / `launch.vbs` | Windows‑specific launch scripts and background startup helpers. |
| `README.md` | Project description & usage. |
| `test_*.py` | Unit‑style endpoint tests (auth/no‑auth). |
| `validate_imports.py` | Helper for CI linting. |

**Important globals / state** – `CONFIG_FILE`, `DATA_FILE`, Flask `app`, `_state` dict (config, data, lock). 

**Dependencies** – Standard library (`os`, `json`, `threading`, `socket`, `subprocess`), third‑party (`Flask`, `requests`). 

**Lifecycle notes**
| Phase | Action |
|---|---|
| **Init** | Load config (`load_config()`), load cached data (`load_data()`), create single‑instance socket guard, start auto‑refresh thread, launch browser. |
| **Run** | Serve static SPA, handle API requests, background refresh loop updates `_state['data']`. |
| **Shutdown** | `/api/stop` triggers Werkzeug shutdown; thread flag stops auto‑refresh; socket guard is closed. |

## `webapp`

**Purpose** – Frontend SPA files (HTML, CSS, Manifest, Service Worker). 

| File | Purpose |
|---|---|
| `index.html` | Main UI layout, tab navigation, bug tables, current‑bug view, hold list, commit pane. |
| `style.css` *(not listed but present)* | Visual styling (modern, glass‑morphism‑style, responsive). |
| `manifest.json` | PWA manifest (icons, theme colour). |
| `sw.js` | Service‑worker placeholder for offline caching. |

**Important globals / state** – `state` JS object (config, data, UI flags). 

**Dependencies** – Browser native APIs (`fetch`, `localStorage`). 

**Lifecycle notes** – On load: fetch config → load cached data → render UI → start auto‑refresh countdown → if API key present, perform first data refresh.

---
# 3. File‑Level Documentation

## `server.py`

**Purpose** – Expose a Flask HTTP API that proxies Bugzilla calls, persists configuration/data, and runs an auto‑refresh background thread.

**Main components**
| Component | Type | Description |
|---|---|---|
| `app` | `Flask` instance | Serves static files and JSON API routes. |
| `_state` | dict | Holds `config`, `data`, and a thread `Lock`. |
| `auto_refresh_loop()` | function | Background loop sleeping 60 s, invoking `do_refresh`. |
| `create_client()` | function | Returns a `Bugzilla` client (or `None` if API key missing). |
| `do_refresh()` | function | Pulls assigned, resolved, and review bugs from Bugzilla, updates `_state['data']`. |
| Route handlers (`/api/*`) | Flask view functions | CRUD for config, data, current bug, hold list, server control. |
| Single‑instance guard (`_guard` socket) | socket object | Binds to `127.0.0.1:5001` to ensure one server instance. |

**Important functions**
- `load_config() -> dict`
- `save_config(config) -> None`
- `load_data() -> dict`
- `save_data(data) -> None`
- `create_client(config) -> Bugzilla|None`
- `normalize_bug(bug) -> dict`
- `fetch_bugs(client, filters) -> list[dict]`
- `fetch_single_bug(client, bug_id) -> dict|None`
- `do_refresh(config, data) -> bool`
- `auto_refresh_loop()` (daemon thread)
- API endpoints: `api_stop`, `api_restart`, `api_refresh`, `api_current_bug`, `api_hold`, etc.

**Important globals** – `BASE_DIR`, `CONFIG_FILE`, `DATA_FILE`, `_state`, `_guard`, `app`.

**Notes** – All API routes return JSON; errors are wrapped with appropriate HTTP status. Auto‑refresh thread runs even when no client is connected (if API key configured). `do_refresh` uses the user’s email (`config['user_email']`) as the assigned‑to filter; review bugs use `qa_contact`.

## `apiBugzilla.py`

**Purpose** – Encapsulate Bugzilla REST calls needed by the server and desktop UI.

**Main components**
| Component | Type | Description |
|---|---|---|
| `Bugzilla` class | Wrapper | Holds API key, base URL, common request headers. |
| `MakeRequest` | method | Generic bug list query (`GET /bug`). |
| `Get_Bug_Information` | method | Retrieve single bug (`GET /bug/<id>`). |
| `Get_Bug_Comment` | method | Retrieve comments for a bug (`GET /bug/<id>/comment`). |
| Additional helper methods (`Get_Activity_Information`, `Get_QAContact_Bugs`, …) | methods | Various filtered queries for activities, QA contact, etc. |

**Important functions / signatures**
- `Bugzilla(API_KEY: str, url: str|None = None)` – initialise client.
- `MakeRequest(self, data: dict, *include_fields: str) -> list[dict]`
- `Get_Bug_Information(self, bug_id: str, *fields: str) -> list[dict]`
- `Get_Bug_Comment(self, bug_id: str) -> list[dict]`
- (Other filtered query methods.)

**Notes** – `self.Url_Bugzilla` always ends with a trailing slash. All methods raise `requests` exceptions on HTTP errors; callers handle them.

## `bugzilla_tracker.py`

**Purpose** – Legacy Tkinter GUI that provides similar functionality to the web SPA for environments without a browser.

**Main components**
| Component | Type | Description |
|---|---|---|
| `BugzillaTracker` class | Tkinter window manager | Holds UI widgets, config, data, Bugzilla client, auto‑update thread. |
| Config / data loaders (`load_config`, `load_data`) | methods | Same JSON schema as Flask server. |
| `create_bugzilla_client` | method | Returns `Bugzilla` client. |
| UI builders (`create_menu`, `create_ui`, `create_main_page`, `create_bugs_view`, `create_bug_tree`) | methods | Build menus, notebook tabs, Treeviews. |
| Auto‑update (`auto_update_loop`, `start_auto_update`) | thread functions | Refresh data every 60 s. |
| Bug actions (`add_current_bug`, `complete_current_bug`, `put_on_hold`, `remove_from_hold`) | methods | Mirrored server‑side actions, operate on local cached data. |
| Data fetch helpers (`fetch_bug`, `fetch_bugs`, `fetch_comments`) | methods | Directly call `Bugzilla` client. |
| `refresh_all_bugs` | method | Pulls all categories, updates UI. |
| `update_bug_trees`, `populate_tree`, `update_main_page` | methods | Refresh UI widgets with current data. |
| Server control (`api_stop`, `api_restart`) | methods | Issue HTTP calls to Flask server (if running). |

**Important functions (signatures)** – `load_config() -> dict`, `save_config(config)`, `load_data() -> dict`, `save_data()`, `create_bugzilla_client() -> Bugzilla|None`, `fetch_bug(bug_id)`, `fetch_bugs(filters)`, `refresh_all_bugs()`, `add_current_bug()`, `complete_current_bug()`, `put_on_hold()`, `remove_from_hold(index)`, `auto_update_loop()`, `start_auto_update()`.

**Important globals / state** – `self.config`, `self.data`, `self.bugzilla_client`, `self.auto_update_running`, UI widgets (Treeviews, Listboxes).

**Notes** – UI updates run on the Tkinter main thread; background thread uses `self.auto_update_running` flag. All persistence mirrors Flask server’s JSON files, allowing cross‑process sharing.

## `webapp/index.html` (excerpt – core UI)

**Purpose** – SPA entry point providing a tabbed interface for current bug, hold list, all bug tables, and a commit‑prompt pane.

**Main components**
- Header with actions (`Refresh`, `Stop Server`, `Restart Server`, `Settings`).
- Status bar (`#status-bar`) showing connection state & countdown.
- Main notebook (`#tab-nav` + `.panel`s) – tabs: “Current Bug”, “All Bugs”, “Commit Prompt”.
- Current‑bug card (`#current-bug-card`) – displays bug details, description, comments, action buttons.
- Hold list (`#hold-list`) – list of bugs on hold with “Make Current” button.
- Bug table (`#bug-table`) – dynamic `<table>` built by JavaScript; columns toggled via UI checkboxes; priority cells support click‑to‑set.
- Commit Prompt (collapsible `<details>` element) – inline form for generating commit messages.
- Settings modal (`#settings-modal`) – edit Bugzilla URL, user email, API key, column visibility.
- Add‑Bug dialog (`#bug-id-modal`) – prompt for bug ID to set as current.
- JavaScript module (embedded) – state management, API wrapper, UI rendering, localStorage handling for priorities.

**Important globals (JS)** – `state` object holds `config`, `data`, UI flags (`visibleCols`, `activeTab`, `sortCol`, `sortDir`, `countdown`).

**Notes** – Dynamic column toggles (`state.visibleCols`) persisted to the server config via `/api/config`. Local priority/sub‑priority stored in `localStorage` keys `bz_local_prio` and `bz_local_sub_prio`.

---
# 4. Function Index

## `load_config()`
File: `server.py`

**Purpose** – Read `bugzilla_config.json` or create defaults.
**Parameters** – none
**Returns** – `dict` with keys `bugzilla_url`, `api_key`, `user_email`, `view_settings`.
**Side Effects** – None
**Threading** – Called during start‑up; safe in main thread.
**Called by** – module init, `/api/config` GET, and on config update.

## `save_config(config)`
File: `server.py`

**Purpose** – Write the provided config dict to JSON file.
**Parameters** – `config: dict`
**Returns** – `None`
**Side Effects** – File I/O (overwrites `bugzilla_config.json`).
**Threading** – Called in Flask request handling (single‑threaded by default).
**Called by** – `post_config()` endpoint after user changes.

## `load_data()`
File: `server.py`

**Purpose** – Load persisted bug state or initialise empty structure.
**Parameters** – none
**Returns** – `dict` with keys `current_bug`, `on_hold_bugs`, `assigned_bugs`, `resolved_fixed_bugs`, `resolved_implemented_bugs`, `review_bugs`, `all_bugs`, `last_update`.
**Side Effects** – File read.
**Threading** – Called during start‑up; safe.
**Called by** – module init, `/api/data` GET, and when refreshing.

## `save_data(data)`
File: `server.py`

**Purpose** – Persist bug state (adds timestamp).
**Parameters** – `data: dict`
**Returns** – `None`
**Side Effects** – Writes `bugzilla_data.json`.
**Threading** – Invoked under lock (`_state['lock']`) in refresh and API handlers.
**Called by** – `do_refresh()`, bug‑state mutating endpoints.

## `create_client(config)`
File: `server.py`

**Purpose** – Instantiate a `Bugzilla` client if API key present.
**Parameters** – `config: dict`
**Returns** – `Bugzilla` instance or `None`.
**Side Effects** – None
**Threading** – Used in request handlers; safe.

## `normalize_bug(bug)`
File: `server.py`

**Purpose** – Extract a flat bug dict with only fields the UI needs.
**Parameters** – `bug: dict` (raw Bugzilla object)
**Returns** – `dict` with keys `id`, `summary`, `status`, `priority`, `severity`, `assigned_to`, `qa_contact`, `product`, `activity`, `sub_activity`, `importance`, `version`, `deadline`, `description`, `resolution`, `last_change_time`.
**Side Effects** – None

## `fetch_bugs(client, filters=None)`
File: `server.py`

**Purpose** – Retrieve a list of bugs matching optional filters.
**Parameters** – `client: Bugzilla`, `filters: dict|None`
**Returns** – `list[dict]` (normalized bugs).
**Side Effects** – Network request to Bugzilla.
**Threading** – May block; invoked in auto‑refresh thread and API endpoints.

## `fetch_single_bug(client, bug_id)`
File: `server.py`

**Purpose** – Get full bug details plus comments.
**Parameters** – `client: Bugzilla`, `bug_id: str`
**Returns** – `dict` (normalized bug with `comments`) or `None`.
**Side Effects** – Network I/O.

## `do_refresh(config, data)`
File: `server.py`

**Purpose** – Core refresh logic: populate all bug categories (assigned, resolved, review) for the configured user.
**Parameters** – `config: dict`, `data: dict`
**Returns** – `bool` (True if successful).
**Side Effects** – Updates `data` in‑place, writes to disk via `save_data`.
**Threading** – Called by auto‑refresh thread (holds `_state['lock']`).

## `auto_refresh_loop()`
File: `server.py`

**Purpose** – Periodically invoke `do_refresh` every 60 s while API key present.
**Parameters** – none
**Returns** – none (runs forever)
**Side Effects** – Repeated network calls, data persistence.
**Threading** – Runs in a daemon thread started at module load.

## `api_stop()` (POST `/api/stop`)
File: `server.py`

**Purpose** – Shut down the Flask development server.
**Parameters** – none
**Returns** – JSON `{ok: true}` or error.
**Side Effects** – Calls Werkzeug shutdown, terminates process.

## `api_restart()` (POST `/api/restart`)
File: `server.py`

**Purpose** – Spawn a detached copy of the server process, then stop the current one.
**Parameters** – none
**Returns** – JSON `{ok: true}` or error.

## `api_refresh()` (POST `/api/refresh`)
File: `server.py`

**Purpose** – Public endpoint to trigger a data refresh on demand.
**Parameters** – none
**Returns** – Full refreshed data JSON.

## `api_current_bug` (POST/DELETE `/api/current-bug`)
File: `server.py`

**Purpose** – Set or clear the “current bug” in persisted state.
**Parameters** – POST body `{'bug_id': <id>}` for set; DELETE has no body.
**Returns** – Bug JSON on set, `{ok:true}` on clear.

## `api_hold` (POST `/api/hold`, DELETE `/api/hold/<index>`)
File: `server.py`

**Purpose** – Move current bug to the hold list, or promote a held bug to current.
**Parameters** – POST: none; DELETE: `index` path param.
**Returns** – `{'ok': true}` or bug JSON.

## `Bugzilla.__init__(API_KEY, url=None)`
File: `apiBugzilla.py`

**Purpose** – Create client with API key and base URL.
**Parameters** – `API_KEY: str`, `url: str|None`
**Returns** – Instance.

## `Bugzilla.MakeRequest(data, *include_fields)`
File: `apiBugzilla.py`

**Purpose** – GET `/bug` with query params and optional field list.
**Parameters** – `data: dict`, `*include_fields: str`
**Returns** – List of bug dicts (`['bugs']`).

## `Bugzilla.Get_Bug_Information(bug_id, *include_fields)`
File: `apiBugzilla.py`

**Purpose** – GET single bug (`/bug/<id>`).
**Parameters** – `bug_id: str`, `*include_fields`.
**Returns** – List of bug dicts (usually length 1).

## `Bugzilla.Get_Bug_Comment(bug_id)`
File: `apiBugzilla.py`

**Purpose** – GET comments for bug.
**Parameters** – `bug_id: str`
**Returns** – List of comment dicts.

## `BugzillaTracker.__init__(root)`
File: `bugzilla_tracker.py`

**Purpose** – Initialise Tkinter UI, load config/data, start auto‑update thread, and perform initial refresh.
**Parameters** – `root: tk.Tk`
**Returns** – Instance.

## `BugzillaTracker.refresh_all_bugs()`
File: `bugzilla_tracker.py`

**Purpose** – Pull all bug categories for the configured user and update UI.
**Parameters** – none
**Returns** – `None`

## `BugzillaTracker.auto_update_loop()`
File: `bugzilla_tracker.py`

**Purpose** – Background loop (60 s) calling `refresh_all_bugs`.
**Parameters** – none
**Returns** – `None` (daemon thread).

## `BugzillaTracker.add_current_bug()`
File: `bugzilla_tracker.py`

**Purpose** – Prompt user for bug ID, fetch it, set as current bug, persist.
**Parameters** – none
**Returns** – `None`

## `BugzillaTracker.complete_current_bug()`
File: `bugzilla_tracker.py`

**Purpose** – Mark current bug as completed, remove from state, adjust sub‑priority ordering.
**Parameters** – none
**Returns** – `None`

## `BugzillaTracker.put_on_hold()`
File: `bugzilla_tracker.py`

**Purpose** – Move current bug to hold list, clear current bug.
**Parameters** – none
**Returns** – `None`

---
# 5. Execution Flows

## Server Startup Flow
```
if __name__ == '__main__':
    _guard = socket.socket(...)
    _guard.bind(('127.0.0.1', 5001))   # single‑instance guard
    start_auto_update_thread()       # launches auto_refresh_loop()
    threading.Thread(target=open_browser, daemon=True).start()
    app.run(host='127.0.0.1', port=5000)
```
*Guard* prevents multiple processes; *auto_update_thread* keeps data fresh; *open_browser* launches UI.
**Failure handling** – If bind fails (port in use) the process exits silently (`sys.exit(0)`).

## Data Refresh Flow (manual or auto)
```
do_refresh(config, data):
    client = create_client(config)
    assigned_to = config['user_email']
    data['all_bugs']               = fetch_bugs(client, {'assigned_to': assigned_to})
    data['assigned_bugs']          = fetch_bugs(client, {'assigned_to': assigned_to, 'status': 'ASSIGNED'})
    data['resolved_fixed_bugs']    = fetch_bugs(client, {'assigned_to': assigned_to, 'status': 'RESOLVED', 'resolution': 'FIXED'})
    data['resolved_implemented_bugs']= fetch_bugs(..., 'IMPLEMENTED')
    data['review_bugs']            = fetch_bugs(client, {'qa_contact': assigned_to})
    save_data(data)
```
**Failure handling** – Network errors are caught in `fetch_bugs`; the function returns an empty list and prints the error.

## Current‑Bug Set Flow (SPA)
1. User clicks “Set Current Bug” → opens dialog → enters bug ID.
2. JS `api('POST', '/api/current-bug', {bug_id})` → Flask `set_current_bug()` → `fetch_single_bug()` → adds `comments`.
3. Server returns bug JSON; client stores in `state.data.current_bug` → UI re‑renders.
**Recovery** – If the API call fails the UI shows an error toast; current bug remains unchanged.

## Hold → Current Bug Flow
1. User presses “Make Current” on a hold item → JS calls `api('DELETE', '/api/hold/<idx>')`.
2. Flask `remove_from_hold()` moves bug from `on_hold_bugs` to `current_bug`.
3. Client updates UI (`renderCurrentBug`, `renderHoldList`).

---
# 6. Shared State / Globals

## `_state` (named `g_state` in docs)
| Variable | Type | Purpose | Modified By | Read By |
|---|---|---|---|---|
| `config` | `dict` | Loaded configuration (URL, API key, email, view settings). | `post_config()`, `save_config()`, server start. | All request handlers, auto‑refresh. |
| `data` | `dict` | Cached bug lists & UI state (`current_bug`, `on_hold_bugs`, category lists). | `do_refresh()`, bug‑state endpoints (`/api/current-bug`, `/api/hold`). | UI routes (`/api/data`), refresh, UI rendering. |
| `lock` | `threading.Lock` | Guard concurrent access between Flask workers and auto‑refresh thread. | `auto_refresh_loop()`, every endpoint that mutates `data` or `config`. | All. |
| `_guard` | `socket.socket` | Single‑instance sentinel. | Created at start. | N/A |
| `app` | `Flask` | Web framework object. | N/A | All route registrations. |

**Concurrency notes** – All mutations to `config` or `data` happen under `with _state['lock']:` to avoid race conditions between the background auto‑refresh thread and incoming HTTP requests.

---
# 7. Dangerous / Sensitive Areas
- **Single‑instance guard** – If another process already bound port 5001, the server exits silently; users may think the server failed to start.
- **Auto‑refresh thread** – Runs indefinitely; a failure in `do_refresh` (e.g., malformed config) could leave the thread in a tight retry loop.
- **Concurrent writes** – `save_config` and `save_data` are called without acquiring `_state['lock']` in some code paths (e.g., `post_config`). If a refresh occurs simultaneously, file corruption is possible.
- **API key handling** – Masked in `/api/config` GET (`••••`), but POST accepts the full key; clients must ensure they do not expose the key (e.g., via browser console).
- **Local priority storage** – Priorities stored in `localStorage`; clearing browser data resets them, potentially breaking sub‑priority ordering.
- **Thread termination** – `auto_update_running = False` is set only on Flask shutdown or Tkinter close; a forced process kill may leave the thread orphaned (harmless on Windows).
- **`/api/stop` and `/api/restart`** – Calling these via a compromised client could shut down the server unexpectedly.

**Recommendations** – Wrap config/data writes in the lock, add logging for guard failures, consider persisting priorities server‑side for multi‑client consistency.

---
# 8. External Interfaces

## HTTP API (Flask)
| Method | Endpoint | Request body | Response | Notes |
|---|---|---|---|---|
| `GET` | `/api/config` | – | `{bugzilla_url, api_key (masked), user_email, view_settings}` | Returns masked API key. |
| `POST` | `/api/config` | `{bugzilla_url?, user_email?, api_key?, view_settings?}` | `{'ok': True}` | Updates config, persists. |
| `GET` | `/api/data` | – | Full cached bug data JSON. |
| `POST` | `/api/refresh` | – | Updated bug data JSON. |
| `GET` | `/api/bug/<bug_id>` | – | Single bug JSON with comments. |
| `POST` | `/api/current-bug` | `{bug_id}` | Bug JSON (set as current). |
| `DELETE` | `/api/current-bug` | – | `{'ok': True}` (clear). |
| `POST` | `/api/hold` | – | `{'ok': True}` (move current → hold). |
| `DELETE` | `/api/hold/<index>` | – | Bug JSON (promote). |
| `POST` | `/api/stop` | – | `{'ok': True}` (shutdown). |
| `POST` | `/api/restart` | – | `{'ok': True}` (restart). |

**Message formats** – All JSON; errors returned as `{error: <msg>}` with appropriate HTTP status.

## Bugzilla REST (via `apiBugzilla`)
| Endpoint | Method | Params | Returns |
|---|---|---|---|
| `/rest/bug` | `GET` | `api_key`, optional filters, `include_fields` | `{'bugs': [...]}` |
| `/rest/bug/<id>` | `GET` | `api_key`, optional `include_fields` | `{'bugs': [...]}` |
| `/rest/bug/<id>/comment` | `GET` | `api_key` | `{'bugs': {<id>: {'comments': [...]}}` |

**Authentication** – API key passed as query param `api_key`.

## Windows Startup Scripts
- `install_startup.bat` registers a scheduled task that runs `run_tracker.bat` at logon.
- `launch.vbs` is a VBScript wrapper used by the scheduled task to hide the console window.

**Environment assumptions** – Running on Windows with `python` in PATH; firewall permits localhost binding on ports 5000/5001.

---
# 9. Build / Deployment Notes

| Step | Command / Action | Details |
|---|---|---|
| **Install dependencies** | `pip install -r requirements.txt` | `Flask`, `requests`. |
| **Run server** | `python server.py` (or double‑click `run_tracker.bat`) | Binds to `127.0.0.1:5000`; opens default browser. |
| **Enable background start** | Run `install_startup.bat` (admin) → creates scheduled task that runs `run_tracker.bat` at logon. | Uses `launch.vbs` to hide console. |
| **Disable background start** | Run `uninstall_startup.bat` to remove scheduled task. |
| **Configuration** | Access Settings modal (gear icon) → set Bugzilla URL, user email, API key. | Changes saved to `bugzilla_config.json`. |
| **Data persistence** | `bugzilla_data.json` stores last refresh and UI state (current bug, hold list). |
| **Development** | Edit `server.py`, `apiBugzilla.py`, `bugzilla_tracker.py`, `webapp/*`. Restart server to apply changes. |
| **Production build** | (Optional) package with `pyinstaller` or Docker; ensure `bugzilla_config.json` is mounted/read‑only. |

**Important configs** – `bugzilla_url` must end with `/demandas` (or the code will append it). `view_settings` controls which columns the SPA shows by default.

---
*This documentation reflects the current repository state as of 2026‑05‑11. Unknown or undocumented behaviours are noted explicitly.*
