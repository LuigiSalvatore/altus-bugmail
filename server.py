# ---------------------------------------------------------------------------
# Bugzilla Tracker — Entry Point
# ---------------------------------------------------------------------------
# Thin wrapper that bootstraps the Flask application.
# All logic lives in the backend/ package.

import os
import sys
import socket
import threading
import time
import webbrowser
from datetime import datetime
from logger import logger

# ---------------------------------------------------------------------------
# Auto-refresh background thread
# ---------------------------------------------------------------------------

def auto_refresh_loop():
    """Background thread that refreshes bug data every 60 seconds."""
    from backend.services.state import get_state
    from backend.services.bugzilla_service import do_refresh

    while True:
        time.sleep(60)
        st = get_state()
        with st['lock']:
            cfg = st['config']
            dat = st['data']
        if cfg.get('api_key') and cfg.get('user_email'):
            try:
                with st['lock']:
                    do_refresh(cfg, dat)
                    st['data'] = dat
                logger.info(f'auto-refresh completed at {datetime.now().strftime("%H:%M:%S")}')
            except Exception as e:
                logger.error(f'auto-refresh failed: {e}')


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    # Single-instance guard: bind a sentinel socket so only one server runs.
    _guard = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    _guard.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 0)
    try:
        _guard.bind(('127.0.0.1', 5001))
    except OSError:
        logger.warning(
            'server.py launched but instance already running on guard port 5001 — triggering restart'
        )
        try:
            import urllib.request
            urllib.request.urlopen(
                urllib.request.Request('http://127.0.0.1:5000/api/restart', method='POST'),
                timeout=3
            )
        except Exception as re:
            logger.error(f'restart request failed: {re}')
        sys.exit(0)

    # Create the Flask app
    from backend import create_app
    from backend.routes.server_control import set_guard_socket

    app = create_app()
    set_guard_socket(_guard)

    # Start auto-refresh daemon
    threading.Thread(target=auto_refresh_loop, daemon=True).start()

    logger.info('Starting Bugzilla Tracker server at http://localhost:5000')

    # Open browser after brief delay
    def open_browser():
        time.sleep(1)
        webbrowser.open('http://localhost:5000')

    threading.Thread(target=open_browser, daemon=True).start()

    app.run(host='127.0.0.1', port=5000, debug=False)
