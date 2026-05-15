# Data Flow

## Bug Data Lifecycle

```mermaid
sequenceDiagram
    participant BZ as Bugzilla API
    participant SVC as bugzilla_service
    participant ST as state.py
    participant FS as persistence.py
    participant FE as Frontend

    Note over FE: User clicks Refresh (or countdown hits 0)
    FE->>+ST: POST /api/refresh
    ST->>+SVC: do_refresh(config, data)
    SVC->>+BZ: GET /rest/bug?assigned_to=...&status=ASSIGNED
    BZ-->>-SVC: raw bug list
    SVC->>SVC: normalize_bug() for each
    SVC->>+BZ: GET /rest/bug?assigned_to=...&status=RESOLVED&resolution=FIXED
    BZ-->>-SVC: raw bug list
    SVC->>SVC: normalize_bug() for each
    SVC->>+BZ: GET /rest/bug?qa_contact=...
    BZ-->>-SVC: raw bug list (reviews)
    SVC->>FS: save_data(data) → data/bugzilla_data.json
    SVC-->>-ST: True
    ST-->>-FE: JSON response (full data object)
    FE->>FE: renderAll()
```

## API Request Lifecycle

```
Frontend                    Flask Route                 Service Layer
--------                    -----------                 -------------
api('POST', '/api/refresh')
    → HTTP POST             refresh() [routes/data.py]
                            acquire lock
                            → do_refresh()              bugzilla_service.do_refresh()
                                                        → create_client()
                                                        → fetch_bugs() × 5 queries
                                                        → normalize_bug() for each
                                                        → save_data()
                            release lock
                            ← jsonify(data)
    ← parsed JSON
    → renderAll()
```

## Current Bug State Transitions

```mermaid
stateDiagram-v2
    [*] --> Empty: App starts (no current bug)
    Empty --> Active: User sets a bug (POST /api/current-bug)
    Active --> Empty: User completes bug (DELETE /api/current-bug)
    Active --> OnHold: User puts on hold (POST /api/hold)
    OnHold --> Active: User resumes from hold (DELETE /api/hold/:index)
    Active --> Active: User replaces with different bug
```

## Local Priority Flow

```
To Work tab render
    ↓
getLocalSubPrios()          ← reads localStorage
    ↓
autoAssignSubPrios()        ← assigns ranks to unranked bugs
normaliseSubPrios()         ← compacts 1..N
    ↓
sort bugs by subPrioSortVal()
    ↓
render table with ▲/▼ buttons
    ↓
User clicks ▲ or drags row
    ↓
moveSubPrio() or drag handler
    ↓
setLocalSubPrio()           → writes localStorage
    ↓
renderBugTable()            ← re-render with new order
```

## Persistence Model

| File | Purpose | Written by | Read by |
|------|---------|-----------|---------|
| `data/bugzilla_config.json` | API credentials, URL, view settings | `save_config()` | `load_config()` |
| `data/bugzilla_data.json` | All bug lists, current bug, hold list | `save_data()` | `load_data()` |
| `logs/bugmail.log` | Application log entries | Python `logging` | `/api/logs` endpoint |
| `localStorage` (browser) | Sub-priorities, commit state, branches | Frontend JS | Frontend JS |
