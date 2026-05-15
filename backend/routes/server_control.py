# ---------------------------------------------------------------------------
# Server Control Routes (Stop / Restart)
# ---------------------------------------------------------------------------

from flask import Blueprint, jsonify
from backend.utils.server_lifecycle import shutdown_server, spawn_server_process

bp = Blueprint('server_control', __name__)

# Reference to the guard socket, set by server.py at startup
_guard_ref = {'socket': None}


def set_guard_socket(sock):
    """Store a reference to the single-instance guard socket."""
    _guard_ref['socket'] = sock


@bp.route('/api/stop', methods=['POST'])
def api_stop():
    try:
        shutdown_server()
        return jsonify({'ok': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/api/restart', methods=['POST'])
def api_restart():
    try:
        sock = _guard_ref['socket']
        if sock is not None:
            try:
                sock.close()
            except Exception:
                pass
            _guard_ref['socket'] = None
        spawn_server_process()
        shutdown_server()
        return jsonify({'ok': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
