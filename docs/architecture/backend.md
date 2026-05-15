# Backend Architecture

## Directory Structure

```
backend/
├── __init__.py              App factory (create_app), static file serving
├── routes/
│   ├── __init__.py          Blueprint registration
│   ├── config.py            GET/POST /api/config
│   ├── data.py              GET /api/data, POST /api/refresh
│   ├── bugs.py              Bug CRUD + hold endpoints
│   ├── logs.py              GET /api/logs
│   └── server_control.py    POST /api/stop, POST /api/restart
├── services/
│   ├── __init__.py
│   ├── persistence.py       JSON file I/O (config + data)
│   ├── state.py             Thread-safe shared state
│   └── bugzilla_service.py  Bugzilla API client wrapper
└── utils/
    ├── __init__.py
    └── server_lifecycle.py  Server shutdown + process spawning

server.py                    Thin entry point (guard socket, auto-refresh, app.run)
logger.py                    Logging configuration
apiBugzilla.py               Low-level Bugzilla REST client
```

## API Routes

| Route | Method | Blueprint | Description |
|-------|--------|-----------|-------------|
| `/` | GET | app factory | Serve `index.html` |
| `/api/config` | GET | config | Get config (API key masked) |
| `/api/config` | POST | config | Update config |
| `/api/data` | GET | data | Get cached bug data |
| `/api/refresh` | POST | data | Trigger full Bugzilla refresh |
| `/api/bug/<id>` | GET | bugs | Fetch a single bug with comments |
| `/api/current-bug` | POST | bugs | Set current working bug |
| `/api/current-bug` | DELETE | bugs | Clear current bug (complete) |
| `/api/hold` | POST | bugs | Put current bug on hold |
| `/api/hold/<index>` | DELETE | bugs | Resume bug from hold |
| `/api/stop` | POST | server_control | Shut down server |
| `/api/restart` | POST | server_control | Restart server process |
| `/api/logs` | GET | logs | Read server log entries |

## Service Layer

### `persistence.py`
- `load_config()` / `save_config()` — JSON I/O for `data/bugzilla_config.json`
- `load_data()` / `save_data()` — JSON I/O for `data/bugzilla_data.json`
- Auto-migrates files from old root location on first run

### `state.py`
- `_state` dict with `config`, `data`, and `lock` (threading.Lock)
- `get_state()` returns the shared dict
- All route handlers acquire lock before reading/writing

### `bugzilla_service.py`
- `create_client(config)` — instantiates `Bugzilla` REST client
- `normalize_bug(bug)` — flattens raw API response to consistent shape
- `fetch_bugs(client, filters)` — parameterised bug list query
- `fetch_single_bug(client, bug_id)` — single bug + comments
- `do_refresh(config, data)` — full refresh of all bug lists

## Threading Model

```
Main Thread                     Daemon Thread
===========                     =============
Flask.run()                     auto_refresh_loop()
  ├── Handle HTTP requests        └── sleep(60)
  ├── Acquire lock for state          acquire lock
  └── Respond                         do_refresh()
                                      release lock
                                      repeat
```

Both threads share `_state` and protect it with the same `threading.Lock`.

## Server Lifecycle

1. **Start**: `python server.py` → guard socket → create_app → start thread → app.run
2. **Stop**: POST `/api/stop` → `werkzeug.server.shutdown()` → process exits
3. **Restart**: POST `/api/restart` → close guard socket → spawn new process → shutdown old
4. **Duplicate prevention**: Second instance detects port 5001 occupied → sends restart to first
