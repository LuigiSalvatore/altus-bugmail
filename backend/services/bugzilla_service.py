# ---------------------------------------------------------------------------
# Bugzilla API Service
# ---------------------------------------------------------------------------
# Wraps the apiBugzilla client for use by route handlers.
# Handles client creation, bug normalisation, and data fetching.

from apiBugzilla import Bugzilla
from logger import logger
from backend.services.persistence import save_data


# Fields requested from the Bugzilla REST API
FIELDS = (
    'id', 'summary', 'status', 'priority', 'severity', 'assigned_to',
    'assigned_to_detail', 'qa_contact', 'qa_contact_detail', 'product',
    'cf_activity', 'cf_subactivity', 'importance', 'version', 'deadline',
    'description', 'resolution', 'last_change_time'
)


def create_client(config):
    """Create a Bugzilla REST client from the given config dict."""
    if not config.get('api_key'):
        return None
    url = config.get('bugzilla_url', '').strip()
    if url:
        return Bugzilla(config['api_key'], url=url)
    return Bugzilla(config['api_key'])


def normalize_bug(bug):
    """Flatten a raw Bugzilla bug dict into a consistent shape."""
    return {
        'id': bug.get('id'),
        'summary': bug.get('summary'),
        'status': bug.get('status'),
        'priority': bug.get('priority'),
        'severity': bug.get('severity'),
        'assigned_to': bug.get('assigned_to_detail', {}).get(
            'email', bug.get('assigned_to', 'Unassigned')
        ),
        'qa_contact': bug.get('qa_contact_detail', {}).get(
            'email', bug.get('qa_contact', '')
        ),
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


def fetch_bugs(client, filters=None):
    """Fetch a list of bugs matching the given filters."""
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
    """Fetch a single bug with its comments."""
    if not client:
        raise Exception('API key not configured')
    bugs = client.Get_Bug_Information(bug_id, *FIELDS)
    if bugs and len(bugs) > 0:
        bug = normalize_bug(bugs[0])
        bug['comments'] = fetch_comments(client, bug_id)
        return bug
    return None


def fetch_comments(client, bug_id):
    """Fetch comments for a specific bug."""
    if not client:
        return []
    try:
        return client.Get_Bug_Comment(bug_id) or []
    except Exception as e:
        logger.error(f'fetch_comments bug #{bug_id}: {e}')
        return []


def do_refresh(config, data):
    """Core refresh logic — fetches all bug lists from Bugzilla.
    
    Shared by the manual refresh endpoint and the auto-update thread.
    Returns True on success, False if client/email not configured.
    """
    client = create_client(config)
    if not client or not config.get('user_email'):
        return False
    assigned_to = config['user_email']
    data['all_bugs'] = fetch_bugs(client, {'assigned_to': assigned_to})
    data['assigned_bugs'] = fetch_bugs(
        client, {'assigned_to': assigned_to, 'status': 'ASSIGNED'}
    )
    data['resolved_fixed_bugs'] = fetch_bugs(
        client, {'assigned_to': assigned_to, 'status': 'RESOLVED', 'resolution': 'FIXED'}
    )
    data['resolved_implemented_bugs'] = fetch_bugs(
        client, {'assigned_to': assigned_to, 'status': 'RESOLVED', 'resolution': 'IMPLEMENTED'}
    )
    data['review_bugs'] = fetch_bugs(client, {'qa_contact': assigned_to})
    save_data(data)
    return True
