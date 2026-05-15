# ---------------------------------------------------------------------------
# Data & Refresh Routes
# ---------------------------------------------------------------------------

from flask import Blueprint, jsonify
from backend.services.state import get_state
from backend.services.bugzilla_service import do_refresh

bp = Blueprint('data', __name__)


@bp.route('/api/data', methods=['GET'])
def get_data():
    st = get_state()
    with st['lock']:
        return jsonify(st['data'])


@bp.route('/api/refresh', methods=['POST'])
def refresh():
    st = get_state()
    with st['lock']:
        cfg = st['config']
        dat = st['data']
    if not cfg.get('api_key'):
        return jsonify({'error': 'API key not configured'}), 400
    if not cfg.get('user_email'):
        return jsonify({'error': 'User email not configured'}), 400
    try:
        with st['lock']:
            do_refresh(cfg, dat)
            st['data'] = dat
        return jsonify(st['data'])
    except Exception as e:
        return jsonify({'error': str(e)}), 500
