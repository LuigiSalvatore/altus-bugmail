# Refactor Notes

## What Changed

### Before (Monolithic)
```
server.py               454 lines — routes + persistence + refresh + lifecycle
bugzilla_tracker.py     673 lines — dead Tkinter GUI (fully replaced)
webapp/index.html      1318 lines — HTML + CSS + 1067 lines inline JavaScript
webapp/style.css       1230 lines — (unchanged)
bugzilla_config.json         root-level config
bugzilla_data.json           root-level data
```

### After (Modular)
```
server.py                ~85 lines — thin entry point (guard, thread, run)
backend/
├── __init__.py          ~25 lines — app factory
├── routes/ (5 files)   ~170 lines — blueprint endpoints
├── services/ (3 files) ~200 lines — persistence, state, bugzilla client
└── utils/ (1 file)      ~30 lines — lifecycle helpers
webapp/
├── index.html          ~200 lines — pure HTML
└── js/ (17 files)      ~2000 lines — modular ES modules
data/
├── bugzilla_config.json     moved from root
└── bugzilla_data.json       moved from root
```

## Migration Decisions

### Frontend

| Decision | Rationale |
|----------|-----------|
| ES Modules (no bundler) | Zero build step, native browser support, explicit dependency graph |
| `data-*` attributes instead of inline `onclick` | Cleaner separation, CSP-compatible, easier debugging |
| Callback injection for cross-module calls | Avoids circular import issues between views and api modules |
| Two commit form instances (inline + tab) | Preserved existing UX where commit form appears both in Current Bug panel and dedicated tab |
| localStorage for priorities | User-local preferences shouldn't be server-synced |

### Backend

| Decision | Rationale |
|----------|-----------|
| Blueprint per resource | Standard Flask pattern, easy to add/remove endpoints |
| Service layer between routes and external APIs | Routes stay thin, business logic is testable independently |
| Persistence auto-migration | Old root-level JSON files auto-move to `data/` on first run |
| State module with lock | Same threading pattern as original, just extracted to its own module |
| Keep `server.py` at root | All startup scripts (`launch.vbs`, batch files) reference it — avoids churn |

### Deleted

| File | Reason |
|------|--------|
| `bugzilla_tracker.py` | 673-line Tkinter GUI, fully replaced by web app, zero shared code |

## Known Technical Debt

1. **Werkzeug `server.shutdown`** — deprecated in newer Flask. Should migrate to `signal`-based shutdown.
2. **No authentication on local API** — the Flask server has no auth. Acceptable for a single-user localhost tool.
3. **Template strings in JS views** — `bugTableView.js` and `commitView.js` use large template literals. A lightweight template system could improve readability.
4. **Test coverage** — existing tests only cover Bugzilla API connectivity, not the Flask endpoints or frontend logic.
5. **Service worker cache invalidation** — cache version is manual (`v2`). Could be auto-versioned with a build hash.

## Future Improvements

- [ ] Add Flask endpoint tests using `pytest` + `app.test_client()`
- [ ] Add `component` column to the default visible columns if requested
- [ ] Implement keyboard shortcuts for common actions
- [ ] Add dark/light theme toggle (CSS custom properties already support it)
- [ ] Consider `lit-html` or similar for template rendering if views grow further
