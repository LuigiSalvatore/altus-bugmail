import requests
from persist import bugs, last_seen_times, save_data
from toast import notify
import bugzilla

def process_bug_updates(bug_id, summary=None, last_change_time=None, initial_load=False):
    bug_id_str = str(bug_id)
    
    # Check if bug has actually changed
    if last_change_time and last_seen_times.get(bug_id_str) == last_change_time:
        return
        
    print(f"Updating bug {bug_id_str}...")
    
    history = bugzilla.get_bug_history(bug_id)
    comments = bugzilla.get_bug_comments(bug_id)
    
    new_updates = []
    is_new_bug = bug_id_str not in bugs
    
    # If bug is new to us, initialize with summary
    if is_new_bug:
        bugs[bug_id_str] = []
        if summary:
            summary_str = f"Summary: {summary}"
            bugs[bug_id_str].append(summary_str)
            new_updates.append(summary_str)
    
    # Process history (field changes)
    for h in history:
        for change in h.get('changes', []):
            field = change.get('field_name')
            removed = change.get('removed')
            added = change.get('added')
            update_str = f"{field}: {removed} -> {added}"
            if update_str not in bugs[bug_id_str]:
                new_updates.append(update_str)
                bugs[bug_id_str].append(update_str)
    
    # Process comments
    for c in comments:
        who = c.get('author')
        text = c.get('text')
        if not text: continue
        update_str = f"Comment from {who}:\n{text}"
        if update_str not in bugs[bug_id_str]:
            new_updates.append(update_str)
            bugs[bug_id_str].append(update_str)
            
    if last_change_time:
        last_seen_times[bug_id_str] = last_change_time
        
    if new_updates or last_change_time:
        save_data()
        
    if new_updates and not initial_load:
        notify(f"Bug {bug_id}", "\n".join(new_updates))

def poll_bugzilla(email, initial_load=False):
    print(f"Polling Bugzilla for {email}...")
    try:
        assigned_bugs = bugzilla.get_assigned_bugs(email)
        for bug in assigned_bugs:
            bug_id = bug['id']
            summary = bug.get('summary')
            last_change_time = bug.get('last_change_time')
            process_bug_updates(bug_id, summary, last_change_time, initial_load)
    except Exception as e:
        print(f"Error polling Bugzilla: {e}")
        import traceback
        traceback.print_exc()
