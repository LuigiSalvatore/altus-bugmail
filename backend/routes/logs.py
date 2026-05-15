# ---------------------------------------------------------------------------
# Logs Route
# ---------------------------------------------------------------------------

import os
from flask import Blueprint, jsonify, request
from logger import logger, LOG_FILE

bp = Blueprint('logs', __name__)


@bp.route('/api/logs')
def get_logs():
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
                    entries.append({
                        'ts': f'{parts[0]} {parts[1]}',
                        'level': level,
                        'msg': parts[3]
                    })
                else:
                    entries.append({'ts': '', 'level': 'DEBUG', 'msg': line})
    except Exception as e:
        logger.error(f'/api/logs read error: {e}')
        return jsonify({'error': str(e)}), 500
    return jsonify(entries)
