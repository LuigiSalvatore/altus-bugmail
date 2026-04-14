# Bugzilla Outlook Monitor

A Python application that monitors your Outlook inbox for Bugzilla update emails, parses them, and displays them in a organized, real-time GUI.

## Features

- **Outlook Integration**: Automatically polls for unread emails with `[Bug` in the subject.
- **Robust Parsing**: Extracts table-based field changes (Assignee, Status, etc.) and comments.
- **Hierarchical GUI**: Displays updates grouped by Bug ID using a Tree View.
- **System Tray**: Runs in the background with a tray icon for quick access.
- **Notifications**: Desktop toasts when new updates are detected.
- **Persistence**: Remembers your bug list across restarts via `bugs.json`.

## Requirements

- Windows (for Outlook/Toast integration)
- Python 3.x
- Outlook Desktop Client

## Installation

1. Install dependencies:
   ```bash
   pip install pywin32 PyQt5 win10toast requests
   ```
   *Or use the Makefile:* `make install`

## Usage

1. Run the application:
   ```bash
   python main_loop.py
   ```
   *Or use the Makefile:* `make run`

2. The app will appear in your taskbar/system tray.
3. It polls for new unread Bugzilla emails every 60 seconds.
4. Use the "Show" option in the tray icon context menu to bring the window to focus.

## Testing

You can verify the parsing logic against the sample emails in `emails_extracted/` by running:
```bash
python test_parser.py
```
*Or use the Makefile:* `make test`

## Project Structure

- `main_loop.py`: Application entry point and polling logic.
- `GUI.py`: PyQt5 TreeView interface.
- `logic_proc.py`: Email parsing and data processing.
- `realtime_outlook.py`: Outlook MAPI integration.
- `persist.py`: JSON data storage.
- `toast.py`: System notifications.
- `tray_icon.py`: System tray management.
