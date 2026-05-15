# ---------------------------------------------------------------------------
# Persistence Service
# ---------------------------------------------------------------------------
# Handles loading and saving of configuration and bug data JSON files.

import os
import json
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
os.makedirs(DATA_DIR, exist_ok=True)

CONFIG_FILE = os.path.join(DATA_DIR, 'bugzilla_config.json')
DATA_FILE = os.path.join(DATA_DIR, 'bugzilla_data.json')

# On first run, migrate files from the old root location if they exist
_OLD_CONFIG = os.path.join(BASE_DIR, 'bugzilla_config.json')
_OLD_DATA = os.path.join(BASE_DIR, 'bugzilla_data.json')

for _old, _new in [(_OLD_CONFIG, CONFIG_FILE), (_OLD_DATA, DATA_FILE)]:
    if os.path.exists(_old) and not os.path.exists(_new):
        os.rename(_old, _new)


_DEFAULT_VIEW_SETTINGS = {
    'Priority': True, 'Assignee': True, 'Product': False,
    'Activity': False, 'Sub-Activity': False, 'Importance': False,
    'Version': False, 'Deadline': False
}


def load_config():
    """Load Bugzilla configuration from JSON file."""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
        config.setdefault('bugzilla_url', 'https://vmbugzilla.altus.com.br/demandas')
        config.setdefault('api_key', '')
        config.setdefault('user_email', '')
        config.setdefault('view_settings', dict(_DEFAULT_VIEW_SETTINGS))
        return config
    return {
        'bugzilla_url': 'https://vmbugzilla.altus.com.br/demandas',
        'api_key': '',
        'user_email': '',
        'view_settings': dict(_DEFAULT_VIEW_SETTINGS)
    }


def save_config(config):
    """Save Bugzilla configuration to JSON file."""
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)


def load_data():
    """Load persistent bug data from JSON file."""
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
    """Save bug data to JSON file, updating the last_update timestamp."""
    data['last_update'] = datetime.now().isoformat()
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)
