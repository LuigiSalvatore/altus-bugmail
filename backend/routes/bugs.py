# ---------------------------------------------------------------------------
# Bug CRUD & Hold Routes
# ---------------------------------------------------------------------------

from flask import Blueprint, jsonify, request
from backend.services.state import get_state
from backend.services.bugzilla_service import create_client, fetch_single_bug
from backend.services.persistence import save_data

bp = Blueprint('bugs', __name__)


@bp.route('/api/bug/<bug_id>', methods=['GET'])
def get_bug(bug_id):
    st = get_state()
    with st['lock']:
        cfg = st['config']
    client = create_client(cfg)
    try:
        bug = fetch_single_bug(client, bug_id)
        if bug:
            return jsonify(bug)
        return jsonify({'error': 'Bug not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/api/current-bug', methods=['POST'])
def set_current_bug():
    body = request.get_json()
    bug_id = body.get('bug_id')
    if not bug_id:
        return jsonify({'error': 'bug_id required'}), 400
    st = get_state()
    with st['lock']:
        cfg = st['config']
    client = create_client(cfg)
    try:
        bug = fetch_single_bug(client, bug_id)
        if not bug:
            return jsonify({'error': 'Bug not found'}), 404
        with st['lock']:
            st['data']['current_bug'] = bug
            save_data(st['data'])
        return jsonify(bug)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/api/current-bug', methods=['DELETE'])
def clear_current_bug():
    st = get_state()
    with st['lock']:
        st['data']['current_bug'] = None
        save_data(st['data'])
    return jsonify({'ok': True})


@bp.route('/api/hold', methods=['POST'])
def put_on_hold():
    st = get_state()
    with st['lock']:
        dat = st['data']
        if not dat['current_bug']:
            return jsonify({'error': 'No current bug'}), 400
        dat['on_hold_bugs'].append(dat['current_bug'])
        dat['current_bug'] = None
        save_data(dat)
    return jsonify({'ok': True})


@bp.route('/api/hold/<int:index>', methods=['DELETE'])
def remove_from_hold(index):
    st = get_state()
    with st['lock']:
        dat = st['data']
        if index < 0 or index >= len(dat['on_hold_bugs']):
            return jsonify({'error': 'Invalid index'}), 400
        bug = dat['on_hold_bugs'].pop(index)
        dat['current_bug'] = bug
        save_data(dat)
    return jsonify(bug)
