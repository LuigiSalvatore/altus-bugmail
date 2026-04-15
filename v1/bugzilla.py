import requests

BUGZILLA_URL = "https://vmbugzilla.altus.com.br/rest"

def get_bug(bug_id):
    r = requests.get(f"{BUGZILLA_URL}/bug/{bug_id}")
    return r.json()

def get_assigned_bugs(email):
    params = {
        'assigned_to': email,
        'include_fields': 'id,summary,last_change_time,assigned_to,status,resolution'
    }
    r = requests.get(f"{BUGZILLA_URL}/bug", params=params)
    return r.json().get('bugs', [])

def get_bug_history(bug_id):
    r = requests.get(f"{BUGZILLA_URL}/bug/{bug_id}/history")
    return r.json().get('bugs', [{}])[0].get('history', [])

def get_bug_comments(bug_id):
    r = requests.get(f"{BUGZILLA_URL}/bug/{bug_id}/comment")
    return r.json().get('bugs', {}).get(str(bug_id), {}).get('comments', [])
