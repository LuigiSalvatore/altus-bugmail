import json
from collections import defaultdict

DATA_FILE = "bugs.json"
bugs = defaultdict(list)

def load_data():
    global bugs
    try:
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
            bugs = defaultdict(list, data)
    except:
        bugs = defaultdict(list)

def save_data():
    with open(DATA_FILE, "w") as f:
        json.dump(bugs, f, indent=2)