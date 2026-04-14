import re
from persist import bugs, save_data
from toast import notify

def extract_bug_id(subject):
    m = re.search(r'\[Bug (\d+)\]', subject)
    return m.group(1) if m else None

def parse_email(body):
    updates = []
    
    # Check for the table pattern
    # What    |Removed                     |Added
    # ----------------------------------------------------------------------------
    # Assignee|igor.franco@altus.com.br    |luigi.salvatore@altus.com.b
    
    table_match = re.search(r'What\s+\|Removed\s+\|Added\s+\n-+\n(.*?)\n\n', body, re.DOTALL)
    if table_match:
        rows = table_match.group(1).split('\n')
        for row in rows:
            parts = [p.strip() for p in row.split('|')]
            if len(parts) >= 3:
                field, removed, added = parts[0], parts[1], parts[2]
                updates.append(f"{field}: {removed} -> {added}")
    
    # Check for comments
    comment_match = re.search(r'--- Comment #\d+ from (.*?) ---.*?\n(.*?)\n--', body, re.DOTALL)
    if comment_match:
        who = comment_match.group(1).strip()
        comment = comment_match.group(2).strip()
        updates.append(f"Comment from {who}: {comment}")

    return updates

def process_message(msg):
    try:
        subject = str(msg.Subject)
    except Exception as e:
        print(f"Error getting subject: {e}")
        return

    if "[Bug" not in subject:
        return

    bug_id = extract_bug_id(subject)
    if not bug_id:
        return

    try:
        body = str(msg.Body)
    except Exception as e:
        print(f"Error getting body: {e}")
        return

    updates = parse_email(body)

    if updates:
        if bug_id not in bugs:
            bugs[bug_id] = []
        
        # Avoid duplicate updates (crude check)
        for u in updates:
            if u not in bugs[bug_id]:
                bugs[bug_id].append(u)
        
        save_data()
        notify(f"Bug {bug_id}", "\n".join(updates))