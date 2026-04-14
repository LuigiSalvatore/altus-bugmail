import requests

BUGZILLA_URL = "https://bugzilla.yourcompany.com/rest"

def get_bug(bug_id):
    r = requests.get(f"{BUGZILLA_URL}/bug/{bug_id}")
    return r.json()