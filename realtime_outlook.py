import win32com.client

class OutlookHandler:
    def OnNewMailEx(self, receivedItemsIDs):
        for entry_id in receivedItemsIDs.split(","):
            msg = outlook.Session.GetItemFromID(entry_id)
            process_message(msg)

outlook = win32com.client.DispatchWithEvents(
    "Outlook.Application", OutlookHandler
)