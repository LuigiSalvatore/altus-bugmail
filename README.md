# Bugzilla Bug Tracker

A Windows desktop GUI application for tracking Bugzilla bugs with real-time updates and persistent data storage.

## Features

### Main Page (Group 1)
- **Current Bug Information**: Display detailed information about the bug you're currently working on
- **Add Current Bug**: Select a bug to work on by entering its ID
- **Complete Bug**: Mark the current bug as complete and remove it
- **Put On Hold**: Move the current bug to the on-hold list
- **Remove from Hold**: Take a bug off hold and make it your current bug

### All Bugs View (Group 2)
- **All Bugs**: View all bugs from Bugzilla
- **Assigned Bugs**: View bugs assigned to you (filtered by your email)
- **Resolved - Fixed**: View all bugs with status RESOLVED and resolution FIXED
- **Resolved - Implemented**: View all bugs with status RESOLVED and resolution IMPLEMENTED

### Additional Features
- **Bugzilla Configuration**: Configure API key, user email, and Bugzilla URL
- **Persistent Data**: All data is saved locally and persists between sessions
- **Real-time Updates**: Automatically refreshes bug data every 60 seconds
- **REST API Integration**: Full integration with Bugzilla REST API

## Installation

### Prerequisites
- Python 3.7 or higher
- Windows OS

### Setup Steps

1. **Install Python** (if not already installed)
   - Download from https://www.python.org/downloads/
   - During installation, make sure to check "Add Python to PATH"

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Application**
   ```bash
   python bugzilla_tracker.py
   ```

## Configuration

On first run, configure your Bugzilla settings:

1. Click **Settings** → **Configure Bugzilla**
2. Enter:
   - **Bugzilla URL**: `https://vmbugzilla.altus.com.br`
   - **User Email**: Your Bugzilla email address
   - **API Key**: Your Bugzilla API key

### Getting Your API Key

1. Log in to Bugzilla
2. Go to **Preferences** → **API Keys**
3. Click **New API Key**
4. Give it a description and click **Submit**
5. Copy the generated API key

## Usage

### Working with Bugs

1. **Start Working on a Bug**:
   - Go to the "Current Bug" tab
   - Click "Add Current Bug"
   - Enter the bug ID
   - The bug details will be displayed

2. **Put a Bug On Hold**:
   - Click "Put On Hold" to move the current bug to the hold list
   - The bug will be saved and you can resume it later

3. **Resume a Bug from Hold**:
   - Select a bug from the "Bugs On Hold" list
   - Click "Remove from Hold"
   - The bug becomes your current bug

4. **Complete a Bug**:
   - Click "Complete Bug" to mark it as done
   - The bug will be removed from your current work

### Viewing Bugs

1. Go to the "All Bugs" tab
2. Switch between different views:
   - All Bugs
   - Assigned (bugs assigned to you)
   - Resolved - Fixed
   - Resolved - Implemented
3. Click "Refresh All Bugs" to manually update

### Auto-Updates

The application automatically refreshes bug data every 60 seconds to ensure you have the latest information.

## Data Storage

The application stores two files in the same directory:
- `bugzilla_config.json`: Your Bugzilla configuration (API key, email, URL)
- `bugzilla_data.json`: Your current bug, on-hold bugs, and cached bug lists

## Troubleshooting

### "Failed to fetch bug"
- Check your internet connection
- Verify your API key is correct
- Ensure the Bugzilla URL is accessible

### "Please configure Bugzilla settings first"
- Go to Settings → Configure Bugzilla
- Enter all required information

### Bugs not refreshing
- Check your API key is valid
- Ensure you're connected to the internet
- The Bugzilla server must be accessible

## Technical Details

- **GUI Framework**: Tkinter (built into Python)
- **HTTP Client**: Requests library
- **Data Format**: JSON for configuration and persistent storage
- **Update Interval**: 60 seconds (1 minute)
- **API**: Bugzilla REST API

## Security Notes

- Your API key is stored locally in `bugzilla_config.json`
- Keep this file secure and do not share it
- The API key is displayed as asterisks in the configuration dialog
- All API requests use HTTPS for secure communication
