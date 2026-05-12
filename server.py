import os
import sys
import socket
import subprocess
import json
import threading
import time
import webbrowser
from datetime import datetime
from flask import Flask, jsonify, request, send_from_directory
from apiBugzilla import Bugzilla
from logger import logger

app = Flask(__name__, static_folder='webapp', static_url_path='')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(BASE_DIR, 'bugzilla_config.json')
DATA_FILE = os.path.join(BASE_DIR, 'bugzilla_data.json')

# ---------------------------------------------------------------------------
# Persistence helpers
# ---------------------------------------------------------------------------

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
        config.setdefault('bugzilla_url', 'https://vmbugzilla.altus.com.br/demandas')
        config.setdefault('api_key', '')
        config.setdefault('user_email', '')
        config.setdefault('view_settings', {
            'Priority': True, 'Assignee': True, 'Product': False,
            'Activity': False, 'Sub-Activity': False, 'Importance': False, 'Version': False, 'Deadline': False
        })
        return config
    return {
        'bugzilla_url': 'https://vmbugzilla.altus.com.br/demandas',
        'api_key': '',
        'user_email': '',
        'view_settings': {
            'Priority': True, 'Assignee': True, 'Product': False,
            'Activity': False, 'Sub-Activity': False, 'Importance': False, 'Version': False, 'Deadline': False
        }
    }


def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)


def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            data = json.load(f)
        data.setdefault('review_bugs', [])
        return data
    return {
        'current_bug': None,
        'on_hold_bugs': [],
        'assigned_bugs': [],
        'resolved_fixed_bugs': [],
        'resolved_implemented_bugs': [],
        'review_bugs': [],
        'all_bugs': [],
        'last_update': None
    }


def save_data(data):
    data['last_update'] = datetime.now().isoformat()
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)


# ---------------------------------------------------------------------------
# Bugzilla client helpers
# ---------------------------------------------------------------------------

def create_client(config):
    if not config.get('api_key'):
        return None
    url = config.get('bugzilla_url', '').strip()
    if url:
        return Bugzilla(config['api_key'], url=url)
    return Bugzilla(config['api_key'])


def normalize_bug(bug):
    return {
        'id': bug.get('id'),
        'summary': bug.get('summary'),
        'status': bug.get('status'),
        'priority': bug.get('priority'),
        'severity': bug.get('severity'),
        'assigned_to': bug.get('assigned_to_detail', {}).get('email', bug.get('assigned_to', 'Unassigned')),
        'qa_contact': bug.get('qa_contact_detail', {}).get('email', bug.get('qa_contact', '')),
        'product': bug.get('product', ''),
        'activity': bug.get('cf_activity', bug.get('activity', '')),
        'sub_activity': bug.get('cf_subactivity', bug.get('sub_activity', '')),
        'importance': bug.get('importance', ''),
        'version': bug.get('version', ''),
        'deadline': bug.get('deadline', ''),
        'description': bug.get('description', ''),
        'resolution': bug.get('resolution', ''),
        'last_change_time': bug.get('last_change_time')
    }


FIELDS = ('id', 'summary', 'status', 'priority', 'severity', 'assigned_to',
          'assigned_to_detail', 'qa_contact', 'qa_contact_detail', 'product',
          'cf_activity', 'cf_subactivity', 'importance', 'version', 'deadline',
          'description', 'resolution', 'last_change_time')


def fetch_bugs(client, filters=None):
    if not client:
        return []
    params = filters or {}
    try:
        bugs = client.MakeRequest(params, *FIELDS)
        if not bugs:
            return []
        return [normalize_bug(b) for b in bugs]
    except Exception as e:
        logger.error(f'fetch_bugs failed: {e}')
        return []


def fetch_single_bug(client, bug_id):
    if not client:
        raise Exception('API key not configured')
    bugs = client.Get_Bug_Information(bug_id, *FIELDS)
    if bugs and len(bugs) > 0:
        bug = normalize_bug(bugs[0])
        bug['comments'] = fetch_comments(client, bug_id)
        return bug
    return None


def fetch_comments(client, bug_id):
    if not client:
        return []
    try:
        return client.Get_Bug_Comment(bug_id) or []
    except Exception as e:
        logger.error(f'fetch_comments bug #{bug_id}: {e}')
        return []


def do_refresh(config, data):
    """Core refresh logic shared by endpoint and auto-update thread."""
    client = create_client(config)
    if not client or not config.get('user_email'):
        return False
    assigned_to = config['user_email']
    data['all_bugs'] = fetch_bugs(client, {'assigned_to': assigned_to})
    data['assigned_bugs'] = fetch_bugs(client, {'assigned_to': assigned_to, 'status': 'ASSIGNED'})
    data['resolved_fixed_bugs'] = fetch_bugs(client, {'assigned_to': assigned_to, 'status': 'RESOLVED', 'resolution': 'FIXED'})
    data['resolved_implemented_bugs'] = fetch_bugs(client, {'assigned_to': assigned_to, 'status': 'RESOLVED', 'resolution': 'IMPLEMENTED'})
    data['review_bugs'] = fetch_bugs(client, {'qa_contact': assigned_to})
    save_data(data)
    return True


# ---------------------------------------------------------------------------
# Auto-refresh thread
# ---------------------------------------------------------------------------

_state = {
    'config': load_config(),
    'data': load_data(),
    'lock': threading.Lock()
}

_guard = None


def _spawn_server_process():
    args = [sys.executable, os.path.abspath(__file__)]
    kwargs = {}
    if os.name == 'nt':
        kwargs['creationflags'] = subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS
    else:
        kwargs['close_fds'] = True
    return subprocess.Popen(args, **kwargs)


def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if not func:
        raise RuntimeError('Not running with the Werkzeug server')
    func()


def auto_refresh_loop():
    while True:
        time.sleep(60)
        with _state['lock']:
            cfg = _state['config']
            dat = _state['data']
        if cfg.get('api_key') and cfg.get('user_email'):
            try:
                with _state['lock']:
                    do_refresh(cfg, dat)
                    _state['data'] = dat
                logger.info(f'auto-refresh completed at {datetime.now().strftime("%H:%M:%S")}')
            except Exception as e:
                logger.error(f'auto-refresh failed: {e}')


threading.Thread(target=auto_refresh_loop, daemon=True).start()


# ---------------------------------------------------------------------------
# Routes — frontend
# ---------------------------------------------------------------------------

@app.route('/')
def index():
    return send_from_directory('webapp', 'index.html')


# ---------------------------------------------------------------------------
# Routes — logs
# ---------------------------------------------------------------------------

@app.route('/api/logs')
def get_logs():
    from logger import LOG_FILE
    level_filter = request.args.get('level', '').upper()
    lines_limit = int(request.args.get('lines', 500))
    entries = []
    try:
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, 'r', encoding='utf-8') as f:
                raw_lines = f.readlines()[-lines_limit:]
            for line in raw_lines:
                line = line.rstrip()
                if not line:
                    continue
                # parse: 2026-05-12 14:00:00 INFO     message
                parts = line.split(' ', 3)
                if len(parts) >= 4:
                    level = parts[2].strip()
                    if level_filter and level != level_filter:
                        continue
                    entries.append({'ts': f'{parts[0]} {parts[1]}', 'level': level, 'msg': parts[3]})
                else:
                    entries.append({'ts': '', 'level': 'DEBUG', 'msg': line})
    except Exception as e:
        logger.error(f'/api/logs read error: {e}')
        return jsonify({'error': str(e)}), 500
    return jsonify(entries)


# ---------------------------------------------------------------------------
# Routes — config
# ---------------------------------------------------------------------------

@app.route('/api/config', methods=['GET'])
def get_config():
    with _state['lock']:
        cfg = dict(_state['config'])
    # mask api key
    safe = dict(cfg)
    if safe.get('api_key'):
        safe['api_key'] = '•' * 8 + safe['api_key'][-4:]
    return jsonify(safe)


@app.route('/api/config', methods=['POST'])
def post_config():
    body = request.get_json()
    with _state['lock']:
        cfg = _state['config']
        if 'bugzilla_url' in body:
            cfg['bugzilla_url'] = body['bugzilla_url'].rstrip('/')
        if 'user_email' in body:
            cfg['user_email'] = body['user_email']
        # Only update api_key if it's not the masked placeholder
        if 'api_key' in body and not body['api_key'].startswith('••••'):
            cfg['api_key'] = body['api_key']
        if 'view_settings' in body:
            cfg['view_settings'] = body['view_settings']
        save_config(cfg)
        _state['config'] = cfg
    return jsonify({'ok': True})


@app.route('/api/stop', methods=['POST'])
def api_stop():
    try:
        shutdown_server()
        return jsonify({'ok': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/restart', methods=['POST'])
def api_restart():
    global _guard
    try:
        if _guard is not None:
            try:
                _guard.close()
            except Exception:
                pass
            _guard = None
        _spawn_server_process()
        shutdown_server()
        return jsonify({'ok': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ---------------------------------------------------------------------------
# Routes — data
# ---------------------------------------------------------------------------

@app.route('/api/data', methods=['GET'])
def get_data():
    with _state['lock']:
        return jsonify(_state['data'])


@app.route('/api/refresh', methods=['POST'])
def refresh():
    with _state['lock']:
        cfg = _state['config']
        dat = _state['data']
    if not cfg.get('api_key'):
        return jsonify({'error': 'API key not configured'}), 400
    if not cfg.get('user_email'):
        return jsonify({'error': 'User email not configured'}), 400
    try:
        with _state['lock']:
            ok = do_refresh(cfg, dat)
            _state['data'] = dat
        return jsonify(_state['data'])
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ---------------------------------------------------------------------------
# Routes — single bug
# ---------------------------------------------------------------------------

@app.route('/api/bug/<bug_id>', methods=['GET'])
def get_bug(bug_id):
    with _state['lock']:
        cfg = _state['config']
    client = create_client(cfg)
    try:
        bug = fetch_single_bug(client, bug_id)
        if bug:
            return jsonify(bug)
        return jsonify({'error': 'Bug not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ---------------------------------------------------------------------------
# Routes — current bug management
# ---------------------------------------------------------------------------

@app.route('/api/current-bug', methods=['POST'])
def set_current_bug():
    body = request.get_json()
    bug_id = body.get('bug_id')
    if not bug_id:
        return jsonify({'error': 'bug_id required'}), 400
    with _state['lock']:
        cfg = _state['config']
    client = create_client(cfg)
    try:
        bug = fetch_single_bug(client, bug_id)
        if not bug:
            return jsonify({'error': 'Bug not found'}), 404
        with _state['lock']:
            _state['data']['current_bug'] = bug
            save_data(_state['data'])
        return jsonify(bug)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/current-bug', methods=['DELETE'])
def clear_current_bug():
    with _state['lock']:
        _state['data']['current_bug'] = None
        save_data(_state['data'])
    return jsonify({'ok': True})


# ---------------------------------------------------------------------------
# Routes — hold management
# ---------------------------------------------------------------------------

@app.route('/api/hold', methods=['POST'])
def put_on_hold():
    with _state['lock']:
        dat = _state['data']
        if not dat['current_bug']:
            return jsonify({'error': 'No current bug'}), 400
        dat['on_hold_bugs'].append(dat['current_bug'])
        dat['current_bug'] = None
        save_data(dat)
    return jsonify({'ok': True})


@app.route('/api/hold/<int:index>', methods=['DELETE'])
def remove_from_hold(index):
    with _state['lock']:
        dat = _state['data']
        if index < 0 or index >= len(dat['on_hold_bugs']):
            return jsonify({'error': 'Invalid index'}), 400
        bug = dat['on_hold_bugs'].pop(index)
        dat['current_bug'] = bug
        save_data(dat)
    return jsonify(bug)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    # Single-instance guard: bind a sentinel socket so only one server runs.
    _guard = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    _guard.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 0)
    try:
        _guard.bind(('127.0.0.1', 5001))
    except OSError:
        # Port already held — log and restart the existing instance, then exit.
        logger.warning('server.py launched but instance already running on guard port 5001 — triggering restart')
        try:
            import urllib.request
            urllib.request.urlopen(
                urllib.request.Request('http://127.0.0.1:5000/api/restart', method='POST'),
                timeout=3
            )
        except Exception as re:
            logger.error(f'restart request failed: {re}')
        sys.exit(0)

    logger.info('Starting Bugzilla Tracker server at http://localhost:5000')
    # Open browser after brief delay
    def open_browser():
        time.sleep(1)
        webbrowser.open('http://localhost:5000')
    threading.Thread(target=open_browser, daemon=True).start()
    app.run(host='127.0.0.1', port=5000, debug=False)
