import os
import email
from logic_proc import parse_email, extract_bug_id

def test_parsing():
    email_dir = "emails_extracted/emails"
    for filename in os.listdir(email_dir):
        if filename.endswith(".eml"):
            path = os.path.join(email_dir, filename)
            with open(path, "rb") as f:
                msg = email.message_from_binary_file(f)
                
                subject = msg["Subject"]
                bug_id = extract_bug_id(subject)
                
                body = ""
                if msg.is_multipart():
                    for part in msg.walk():
                        if part.get_content_type() == "text/plain":
                            body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                            break
                else:
                    body = msg.get_payload(decode=True).decode('utf-8', errors='ignore')
                
                print(f"File: {filename}")
                print(f"Bug ID: {bug_id}")
                updates = parse_email(body)
                for u in updates:
                    print(f"  Update: {u}")
                print("-" * 20)

if __name__ == "__main__":
    test_parsing()
