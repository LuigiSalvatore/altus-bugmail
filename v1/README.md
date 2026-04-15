# Bugzilla Monitor

A Python application that monitors Bugzilla updates via the REST API and Outlook inbox emails, displaying them in an organized, real-time GUI.

## Features

- **Bugzilla REST API Integration**: Directly polls Bugzilla for assigned bugs.
- **Outlook Integration**: Polls for unread emails with `[Bug` in the subject.
- **Real-time Updates**: Automatically refreshes every minute.
- **Hierarchical GUI**: Displays updates grouped by Bug ID using a Tree View.
- **System Tray**: Runs in the background with a tray icon for quick access.
- **Notifications**: Desktop toasts when new updates are detected.
- **Persistence**: Remembers your bug list across restarts.

## Requirements

- Windows (for Outlook/Toast integration)
- Python 3.x
- Outlook Desktop Client (optional, for email monitoring)

## Installation

1. Clone the repository.
2. Install dependencies:
   ```bash
   pip install pywin32 PyQt5 win10toast requests
   ```
   *Or use the Makefile:* `make install`

3. **Configuration**:
   - Copy `config.py.example` to `config.py`.
   - Edit `config.py` and set `USER_EMAIL` to your Bugzilla email.

## Usage

1. Run the application:
   ```bash
   python main_loop.py
   ```
   *Or use the Makefile:* `make run`

2. The app will appear in your taskbar/system tray.
3. Use the "Show" option in the tray icon context menu to bring the window to focus.

## Project Structure

- `main_loop.py`: Application entry point and polling logic.
- `bugzilla.py`: Bugzilla REST API wrapper.
- `bugzilla_proc.py`: Logic for processing API data.
- `GUI.py`: PyQt5 TreeView interface.
- `logic_proc.py`: Email parsing and data processing.
- `realtime_outlook.py`: Outlook MAPI integration.
- `persist.py`: JSON data storage.
- `toast.py`: System notifications.
- `tray_icon.py`: System tray management.
