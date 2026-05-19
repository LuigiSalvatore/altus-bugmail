# ---------------------------------------------------------------------------
# Config Routes
# ---------------------------------------------------------------------------

from flask import Blueprint, jsonify, request
from backend.services.state import get_state
from backend.services.persistence import save_config

bp = Blueprint('config', __name__)


@bp.route('/api/config', methods=['GET'])
def get_config():
    st = get_state()
    with st['lock']:
        cfg = dict(st['config'])
    # Mask API key for safety
    safe = dict(cfg)
    if safe.get('api_key'):
        safe['api_key'] = '•' * 8 + safe['api_key'][-4:]
    return jsonify(safe)


@bp.route('/api/config', methods=['POST'])
def post_config():
    body = request.get_json()
    st = get_state()
    with st['lock']:
        cfg = st['config']
        if 'bugzilla_url' in body:
            cfg['bugzilla_url'] = body['bugzilla_url'].rstrip('/')
        if 'user_email' in body:
            cfg['user_email'] = body['user_email']
        # Only update api_key if it's not the masked placeholder
        if 'api_key' in body and not body['api_key'].startswith('••••'):
            cfg['api_key'] = body['api_key']
        if 'view_settings' in body:
            cfg['view_settings'] = body['view_settings']
        if 'sort_col' in body:
            cfg['sort_col'] = body['sort_col']
        if 'sort_dir' in body:
            cfg['sort_dir'] = body['sort_dir']
        if 'col_widths' in body:
            cfg['col_widths'] = body['col_widths']
        save_config(cfg)
        st['config'] = cfg
    return jsonify({'ok': True})
