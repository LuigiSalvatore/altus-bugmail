import pythoncom
import sys

if __name__ == "__main__":
    load_data()

    app = QApplication(sys.argv)
    window = BugApp()

    tray = create_tray(app, window)

    window.show()

    while True:
        pythoncom.PumpWaitingMessages()
        app.processEvents()