try:
    import pythoncom
except ImportError:
    pythoncom = None

import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer
from persist import load_data
from GUI import BugApp
from tray_icon import create_tray
from realtime_outlook import check_for_new_emails
from bugzilla_proc import poll_bugzilla
from config import USER_EMAIL, BUGZILLA_POLL_INTERVAL

def poll_emails():
    print("Polling for new emails...")
    check_for_new_emails()

def poll_bz(initial_load=False):
    print(f"Polling Bugzilla API (initial_load={initial_load})...")
    poll_bugzilla(USER_EMAIL, initial_load=initial_load)

def pump_messages():
    if pythoncom:
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
    poll_bz(initial_load=True)

    # Poll Outlook every minute
    poll_timer = QTimer()
    poll_timer.timeout.connect(poll_emails)
    poll_timer.start(60000)

    # Poll Bugzilla API every minute
    bz_timer = QTimer()
    bz_timer.timeout.connect(poll_bz)
    bz_timer.start(BUGZILLA_POLL_INTERVAL)

    # Pump Windows messages for Outlook events
    if pythoncom:
        pump_timer = QTimer()
        pump_timer.timeout.connect(pump_messages)
        pump_timer.start(100) # Check every 100ms

    sys.exit(app.exec_())