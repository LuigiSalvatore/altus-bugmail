# AI Agent Guide

Operational guide for AI coding agents working on the Bugzilla Tracker codebase.

## Quick Feature Location Map

| "I want to..." | Look in... |
|----------------|-----------|
| Add a new API endpoint | `backend/routes/` — create or edit a blueprint |
| Change bug table columns | `webapp/js/utils/constants.js` → `ALL_COLS`, `COL_FIELD` |
| Modify the refresh cycle | `webapp/js/api/client.js` → `doRefresh()`, `webapp/js/ui/countdown.js` |
| Change bug data normalization | `backend/services/bugzilla_service.py` → `normalize_bug()` |
| Add a new sub-tab | `webapp/index.html` (add button), `webapp/js/utils/constants.js` (add to `TAB_KEYS`), `webapp/js/views/bugTableView.js` (add filter logic) |
| Modify the current bug card | `webapp/js/views/currentBugView.js` → `renderCurrentBug()` |
| Change the commit prompt template | `webapp/js/views/commitView.js` → `buildPrompt()` |
| Add a new modal | `webapp/index.html` (add overlay HTML), `webapp/js/ui/modals.js` (add open/close/init functions), `webapp/js/app.js` (wire init) |
| Change persistence format | `backend/services/persistence.py` |
| Modify the design system | `webapp/style.css` — all tokens are CSS custom properties in `:root` |
| Add a toast notification | `import { toast } from './ui/notifications.js'` then call `toast(msg, type)` |
| Add a status bar update | `import { setStatus } from './ui/statusbar.js'` then call `setStatus(state, text)` |
| Copy a rich text bug link | `import { copyRichTextToClipboard, buildBugClipboardPayload } from '../utils/dom.js'` |

## Safe Modification Patterns

### Adding a New Backend Endpoint

1. Choose or create a blueprint in `backend/routes/`
2. Add the route function with `@bp.route()`
3. Access state via `from backend.services.state import get_state`
4. Always acquire `st['lock']` before reading/writing `st['config']` or `st['data']`
5. If the blueprint is new, register it in `backend/routes/__init__.py`

### Adding a New Frontend View

1. Create `webapp/js/views/myView.js`
2. Import state and any needed utilities
3. Export a render function and an init function
4. Import and call them from `webapp/js/app.js`
5. Add the JS file to `SHELL_ASSETS` in `webapp/sw.js`

### Adding a New Sub-Tab

1. Add the `<button class="sub-tab" data-tab="my_tab">` to `index.html`
2. Add `my_tab: 'my_tab_bugs'` to `TAB_KEYS` in `constants.js`
3. Add count element `<span id="count-my_tab">` to the button
4. Add filter logic in `bugTableView.js` `renderBugTable()` for the new tab key
5. Add count logic in `bugTableView.js` `renderCounts()`

## Dangerous Areas

> **State Mutation**: Never modify `state.data` or `state.config` without triggering a re-render. Always call `renderAll()` after changes.

> **Timer Management**: The countdown timer in `countdown.js` has a `clearInterval` guard. Never create a second timer without clearing the first.

> **Lock Contention**: Backend routes must acquire `_state['lock']` for the minimum necessary duration. Holding the lock during Bugzilla API calls will block all other requests.

> **Service Worker Cache**: After adding new JS files, always update `SHELL_ASSETS` in `sw.js` and bump the cache version.

> **Circular Imports**: Frontend modules avoid circular dependencies via callback injection. If module A needs to call module B and vice versa, pass the function as a callback parameter instead of importing directly.

## Architectural Invariants

1. **`index.html` has zero inline JavaScript** — all logic lives in `webapp/js/`
2. **State is a single object** — `webapp/js/state/store.js` exports one mutable object
3. **Routes are thin** — they delegate to services, never contain business logic
4. **`server.py` is a thin entry point** — all Flask logic lives in `backend/`
5. **JSON persistence only** — no database, no ORM
6. **No build step** — no bundler, no transpiler, ES modules load natively

## Extension Points

- **New bug data sources**: Add fetch calls in `bugzilla_service.py` `do_refresh()`
- **New column types**: Add to `ALL_COLS` and `COL_FIELD` in `constants.js`
- **Custom badge styles**: Add CSS class in `style.css`, return from `statusBadgeClass()` in `templates.js`
- **New localStorage keys**: Define in `constants.js`, use in the relevant view module
- **Webhook / notification support**: Add a new service in `backend/services/`, call from `do_refresh()`
