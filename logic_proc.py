import re

def extract_bug_id(subject):
    m = re.search(r'\[Bug (\d+)\]', subject)
    return m.group(1) if m else None

def process_message(msg):
    subject = str(msg.Subject)

    if "[Bug" not in subject:
        return

    bug_id = extract_bug_id(subject)
    if not bug_id:
        return

    body = str(msg.Body)
    updates = parse_email(body)

    if updates:
        bugs[bug_id].extend(updates)
        save_data()

        notify(f"Bug {bug_id}", "\n".join(updates))