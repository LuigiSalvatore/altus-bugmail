import json
from collections import defaultdict

DATA_FILE = "bugs.json"
META_FILE = "meta.json"
bugs = defaultdict(list)
last_seen_times = {}

def load_data():
    global bugs, last_seen_times
    try:
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
            bugs = defaultdict(list, data)
    except:
        bugs = defaultdict(list)
    
    try:
        with open(META_FILE, "r") as f:
            last_seen_times = json.load(f)
    except:
        last_seen_times = {}

def save_data():
    with open(DATA_FILE, "w") as f:
        json.dump(bugs, f, indent=2)
    with open(META_FILE, "w") as f:
        json.dump(last_seen_times, f, indent=2)
