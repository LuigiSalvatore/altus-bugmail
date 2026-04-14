import json
from collections import defaultdict

DATA_FILE = "bugs.json"
bugs = defaultdict(list)

def load_data():
    global bugs
    try:
        with open(DATA_FILE, "r") as f:
            bugs.update(json.load(f))
    except:
        pass

def save_data():
    with open(DATA_FILE, "w") as f:
        json.dump(bugs, f, indent=2)