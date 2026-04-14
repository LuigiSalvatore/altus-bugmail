import pythoncom
import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer
from persist import load_data
from GUI import BugApp
from tray_icon import create_tray
from realtime_outlook import check_for_new_emails

def poll_emails():
    print("Polling for new emails...")
    check_for_new_emails()

def pump_messages():
    pythoncom.PumpWaitingMessages()

if __name__ == "__main__":
    load_data()

    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    
    window = BugApp()
    tray = create_tray(app, window)
    window.show()

    # Poll on startup
    poll_emails()

    # Poll every minute
    poll_timer = QTimer()
    poll_timer.timeout.connect(poll_emails)
    poll_timer.start(60000)

    # Pump Windows messages for Outlook events
    pump_timer = QTimer()
    pump_timer.timeout.connect(pump_messages)
    pump_timer.start(100) # Check every 100ms

    sys.exit(app.exec_())