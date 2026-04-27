# PWA + Silent Windows Startup

Flask web app at `c:\Users\luigi.salvatore\repos\bugmail`. Single `server.py`, static files in `webapp/`.

---

## Open Questions / Assumptions

> [!IMPORTANT]
> **Assumption A**: App stays on `localhost:5000`. No HTTPS cert needed — Chrome allows PWA install on `localhost` (special exception).

> [!IMPORTANT]
> **Assumption B**: "Normal user install" = run one script. No IT admin required. We won't use Windows Service (needs admin rights). We'll use **Task Scheduler** via a VBScript launcher — zero-console, reliable, no admin.

> [!NOTE]
> **PyInstaller vs Task Scheduler tradeoff** — see section below.

---

## Tradeoff: .EXE vs Task Scheduler

| | PyInstaller `.exe` | Task Scheduler + VBScript |
|---|---|---|
| **No console window** | ✅ (with `--noconsole`) | ✅ (VBScript `WScript.Run` hides window) |
| **Startup on login** | Needs extra step (Task Scheduler or Startup folder) | ✅ built-in |
| **Easy install** | Requires build step each code change | ✅ one `.bat` to register |
| **Antivirus flags** | Often triggers AV (unsigned PE) | Rarely flagged |
| **Code changes** | Must rebuild EXE | Edit `.py` files directly |
| **Python required** | ❌ (bundled) | ✅ Python must be installed |
| **File size** | ~50–80 MB | Tiny |

**Recommendation: Task Scheduler + VBScript.** User already has Python installed (they run `server.py` now). EXE adds AV friction and a build step. VBScript approach is transparent, easy to update, and zero-console.

If they later want a distributable EXE for machines without Python, PyInstaller instructions are included as a bonus.

---

## Part 1 — PWA

### How Chrome PWA install works on localhost

Chrome grants `localhost` the same trust as HTTPS. PWA requires:
1. Valid `manifest.json` linked from `<head>`
2. Service worker registered (must be on same origin, at root)
3. Icons: at least 192×192 and 512×512 PNG
4. `start_url`, `display: standalone`, `theme_color`

Flask must serve `manifest.json` and `sw.js` from the root. Currently Flask serves `webapp/` as root — both files go in `webapp/`.

### New files

```
webapp/
  manifest.json          ← PWA manifest
  sw.js                  ← Service worker (offline shell cache)
  icons/
    icon-192.png         ← Generated placeholder
    icon-512.png         ← Generated placeholder
```

### Changes to `index.html`

Add in `<head>`:
```html
<link rel="manifest" href="/manifest.json">
<meta name="theme-color" content="#0f1117">
<meta name="apple-mobile-web-app-capable" content="yes">
<link rel="apple-touch-icon" href="/icons/icon-192.png">
```

Add before `</body>`:
```html
<script>
  if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('/sw.js');
  }
</script>
```

### `manifest.json` key fields

```json
{
  "name": "Bugzilla Tracker",
  "short_name": "BugTrack",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#0f1117",
  "theme_color": "#7c6cf5",
  "icons": [...]
}
```

### `sw.js` strategy

App-shell cache: cache index.html + style.css on install. Serve from cache first, fall back to network. API calls always go to network (no caching of `/api/*`).

---

## Part 2 — Silent Windows Startup

### Architecture

```
bugmail/
  launch.vbs             ← Silent VBScript launcher (hides console)
  install_startup.bat    ← Registers Task Scheduler task (run once)
  uninstall_startup.bat  ← Removes task
```

**`launch.vbs`** — uses `WScript.CreateObject("WScript.Shell").Run` with `0` window style. Zero visible windows.

**`install_startup.bat`** — calls `schtasks /create` to register a Task Scheduler job that:
- Runs at logon for current user
- Launches `launch.vbs` via `wscript.exe`
- No elevation required

**`server.py` changes** — none to startup logic. Already opens browser. We add a small guard: only open browser if not already running (check port first). Also add a single-instance lock via a lock file or socket to avoid duplicate processes on re-login.

### Single-instance guard (server.py)

Add at top of `if __name__ == '__main__':`:
```python
import socket
_guard = socket.socket()
try:
    _guard.bind(('127.0.0.1', 5001))  # guard port
except OSError:
    sys.exit(0)  # already running
```

---

## Proposed Changes

### Frontend (`webapp/`)

#### [NEW] `webapp/manifest.json`
PWA manifest with name, icons, display mode, theme color.

#### [NEW] `webapp/sw.js`
Service worker: cache-first for shell assets, network-first for API.

#### [NEW] `webapp/icons/icon-192.png`
Generated icon (bug tracker themed, 192×192).

#### [NEW] `webapp/icons/icon-512.png`
Generated icon (bug tracker themed, 512×512).

#### [MODIFY] `webapp/index.html`
Add manifest link, theme-color meta, SW registration script.

---

### Backend / Server (`server.py`)

#### [MODIFY] `server.py`
Add single-instance guard via socket bind on port 5001.

---

### Windows Startup

#### [NEW] `launch.vbs`
Silent VBScript — runs `python server.py` with hidden window via `WScript.Shell.Run`.

#### [NEW] `install_startup.bat`
`schtasks /create` registers Task Scheduler job at logon, no admin needed.

#### [NEW] `uninstall_startup.bat`
`schtasks /delete` removes the task.

---

### Docs

#### [MODIFY] `README.md`
Add PWA install instructions + Windows startup sections.

---

## Verification Plan

### Automated
- Open `http://localhost:5000` in Chrome
- DevTools → Application → Manifest: verify no errors
- DevTools → Application → Service Workers: verify registered
- Look for install icon (⊕) in Chrome address bar

### Manual
1. Open Chrome → `http://localhost:5000` → address bar shows install button → click → "Install App" → app opens in standalone window ✅
2. Close standalone window → re-open from Start Menu / Desktop shortcut ✅
3. Offline test: stop server → reload → shell still loads (offline-capable shell) ✅
4. Run `install_startup.bat` → log off → log back in → server starts silently, browser opens ✅
5. Task Manager → no `cmd.exe` or `python.exe` console window visible ✅
