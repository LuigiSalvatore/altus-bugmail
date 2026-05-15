# ---------------------------------------------------------------------------
# Server Lifecycle Utilities
# ---------------------------------------------------------------------------
# Handles server shutdown and process spawning for restart.

import os
import sys
import subprocess
from flask import request


def shutdown_server():
    """Shut down the Werkzeug development server."""
    func = request.environ.get('werkzeug.server.shutdown')
    if not func:
        raise RuntimeError('Not running with the Werkzeug server')
    func()


def spawn_server_process():
    """Spawn a new server process (used during restart)."""
    args = [sys.executable, os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'server.py'
    )]
    kwargs = {}
    if os.name == 'nt':
        kwargs['creationflags'] = (
            subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS
        )
    else:
        kwargs['close_fds'] = True
    return subprocess.Popen(args, **kwargs)
