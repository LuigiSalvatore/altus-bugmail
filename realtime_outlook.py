import win32com.client
from logic_proc import process_message

class OutlookHandler:
    def OnNewMailEx(self, receivedItemsIDs):
        for entry_id in receivedItemsIDs.split(","):
            try:
                msg = outlook.Session.GetItemFromID(entry_id)
                process_message(msg)
            except Exception as e:
                print(f"Error processing new mail: {e}")

try:
    outlook = win32com.client.DispatchWithEvents(
        "Outlook.Application", OutlookHandler
    )
except Exception as e:
    print(f"Could not connect to Outlook: {e}")
    outlook = None

def check_for_new_emails():
    """Polls the inbox for unread Bugzilla emails."""
    if not outlook:
        print("Outlook not available.")
        return
    try:
        ns = outlook.GetNamespace("MAPI")
        inbox = ns.GetDefaultFolder(6)  # 6 = olFolderInbox
        messages = inbox.Items
        # Filter for unread and containing [Bug
        messages = messages.Restrict("[Unread] = true AND ( [Subject] LIKE '%[Bug%' )")
        
        for msg in list(messages):
            process_message(msg)
            # Optional: mark as read if you want
            # msg.UnRead = False
    except Exception as e:
        print(f"Error polling emails: {e}")