import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import requests
from requests.auth import HTTPBasicAuth
import json
import os
from datetime import datetime
import threading
import time

class BugzillaTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Bugzilla Bug Tracker")
        self.root.geometry("1000x700")
        
        # Configuration file path
        self.config_file = "bugzilla_config.json"
        self.data_file = "bugzilla_data.json"
        
        # Load configuration and data
        self.config = self.load_config()
        self.data = self.load_data()
        
        # Auto-update flag
        self.auto_update_running = False
        
        # Create UI
        self.create_menu()
        self.create_ui()
        
        # Start auto-update thread
        self.start_auto_update()
        
        # Initial data fetch
        if self.config.get('api_key') and self.config.get('bugzilla_url'):
            self.refresh_all_bugs()
    
    def load_config(self):
        """Load Bugzilla configuration from file"""
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                return json.load(f)
        return {
            'bugzilla_url': 'https://vmbugzilla.altus.com.br',
            'api_key': '',
            'user_email': ''
        }
    
    def save_config(self):
        """Save Bugzilla configuration to file"""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def load_data(self):
        """Load persistent data from file"""
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r') as f:
                return json.load(f)
        return {
            'current_bug': None,
            'on_hold_bugs': [],
            'all_bugs': [],
            'assigned_bugs': [],
            'resolved_fixed_bugs': [],
            'resolved_implemented_bugs': [],
            'last_update': None
        }
    
    def save_data(self):
        """Save persistent data to file"""
        self.data['last_update'] = datetime.now().isoformat()
        with open(self.data_file, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def create_menu(self):
        """Create menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Settings menu
        settings_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Settings", menu=settings_menu)
        settings_menu.add_command(label="Configure Bugzilla", command=self.configure_bugzilla)
        settings_menu.add_separator()
        settings_menu.add_command(label="Refresh All", command=self.refresh_all_bugs)
    
    def create_ui(self):
        """Create the main UI"""
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Group 1: Main Page (Current Bug)
        self.create_main_page()
        
        # Group 2: All Bugs View
        self.create_bugs_view()
    
    def create_main_page(self):
        """Create the main page with current bug information"""
        main_frame = ttk.Frame(self.notebook)
        self.notebook.add(main_frame, text="Current Bug")
        
        # Current Bug Section
        current_frame = ttk.LabelFrame(main_frame, text="Currently Working On", padding=10)
        current_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Bug info display
        self.current_bug_text = tk.Text(current_frame, height=10, width=80, wrap=tk.WORD)
        self.current_bug_text.pack(fill='both', expand=True, pady=5)
        
        # Buttons frame
        buttons_frame = ttk.Frame(current_frame)
        buttons_frame.pack(fill='x', pady=5)
        
        ttk.Button(buttons_frame, text="Add Current Bug", command=self.add_current_bug).pack(side='left', padx=5)
        ttk.Button(buttons_frame, text="Complete Bug", command=self.complete_current_bug).pack(side='left', padx=5)
        ttk.Button(buttons_frame, text="Put On Hold", command=self.put_on_hold).pack(side='left', padx=5)
        
        # On Hold Section
        hold_frame = ttk.LabelFrame(main_frame, text="Bugs On Hold", padding=10)
        hold_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # On hold listbox with scrollbar
        hold_scroll_frame = ttk.Frame(hold_frame)
        hold_scroll_frame.pack(fill='both', expand=True)
        
        hold_scrollbar = ttk.Scrollbar(hold_scroll_frame)
        hold_scrollbar.pack(side='right', fill='y')
        
        self.hold_listbox = tk.Listbox(hold_scroll_frame, yscrollcommand=hold_scrollbar.set, height=8)
        self.hold_listbox.pack(side='left', fill='both', expand=True)
        hold_scrollbar.config(command=self.hold_listbox.yview)
        
        ttk.Button(hold_frame, text="Remove from Hold", command=self.remove_from_hold).pack(pady=5)
        
        # Update display
        self.update_main_page()
    
    def create_bugs_view(self):
        """Create the bugs view with multiple categories"""
        bugs_frame = ttk.Frame(self.notebook)
        self.notebook.add(bugs_frame, text="All Bugs")
        
        # Create sub-notebook for bug categories
        bugs_notebook = ttk.Notebook(bugs_frame)
        bugs_notebook.pack(fill='both', expand=True, padx=5, pady=5)
        
        # All Bugs Tab
        self.all_bugs_tree = self.create_bug_tree(bugs_notebook, "All Bugs")
        
        # Assigned Bugs Tab
        self.assigned_bugs_tree = self.create_bug_tree(bugs_notebook, "Assigned")
        
        # Resolved Fixed Tab
        self.resolved_fixed_tree = self.create_bug_tree(bugs_notebook, "Resolved - Fixed")
        
        # Resolved Implemented Tab
        self.resolved_implemented_tree = self.create_bug_tree(bugs_notebook, "Resolved - Implemented")
        
        # Refresh button
        ttk.Button(bugs_frame, text="Refresh All Bugs", command=self.refresh_all_bugs).pack(pady=5)
        
        # Status label
        self.status_label = ttk.Label(bugs_frame, text="Last update: Never")
        self.status_label.pack(pady=5)
    
    def create_bug_tree(self, parent, title):
        """Create a treeview for displaying bugs"""
        frame = ttk.Frame(parent)
        parent.add(frame, text=title)
        
        # Create treeview with scrollbar
        tree_frame = ttk.Frame(frame)
        tree_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side='right', fill='y')
        
        tree = ttk.Treeview(tree_frame, columns=('ID', 'Summary', 'Status', 'Priority', 'Assignee'), 
                           show='headings', yscrollcommand=scrollbar.set)
        
        tree.heading('ID', text='Bug ID')
        tree.heading('Summary', text='Summary')
        tree.heading('Status', text='Status')
        tree.heading('Priority', text='Priority')
        tree.heading('Assignee', text='Assignee')
        
        tree.column('ID', width=80)
        tree.column('Summary', width=400)
        tree.column('Status', width=120)
        tree.column('Priority', width=80)
        tree.column('Assignee', width=150)
        
        tree.pack(side='left', fill='both', expand=True)
        scrollbar.config(command=tree.yview)
        
        return tree
    
    def configure_bugzilla(self):
        """Open configuration dialog"""
        config_window = tk.Toplevel(self.root)
        config_window.title("Bugzilla Configuration")
        config_window.geometry("500x250")
        config_window.transient(self.root)
        config_window.grab_set()
        
        # Bugzilla URL
        ttk.Label(config_window, text="Bugzilla URL:").grid(row=0, column=0, padx=10, pady=10, sticky='w')
        url_entry = ttk.Entry(config_window, width=40)
        url_entry.insert(0, self.config.get('bugzilla_url', 'https://vmbugzilla.altus.com.br'))
        url_entry.grid(row=0, column=1, padx=10, pady=10)
        
        # User Email
        ttk.Label(config_window, text="User Email:").grid(row=1, column=0, padx=10, pady=10, sticky='w')
        email_entry = ttk.Entry(config_window, width=40)
        email_entry.insert(0, self.config.get('user_email', ''))
        email_entry.grid(row=1, column=1, padx=10, pady=10)
        
        # API Key
        ttk.Label(config_window, text="API Key:").grid(row=2, column=0, padx=10, pady=10, sticky='w')
        api_entry = ttk.Entry(config_window, width=40, show='*')
        api_entry.insert(0, self.config.get('api_key', ''))
        api_entry.grid(row=2, column=1, padx=10, pady=10)
        
        def save_config():
            self.config['bugzilla_url'] = url_entry.get().rstrip('/')
            self.config['user_email'] = email_entry.get()
            self.config['api_key'] = api_entry.get()
            self.save_config()
            messagebox.showinfo("Success", "Configuration saved successfully!")
            config_window.destroy()
            self.refresh_all_bugs()
        
        ttk.Button(config_window, text="Save", command=save_config).grid(row=3, column=0, columnspan=2, pady=20)
    
    def add_current_bug(self):
        """Add a bug to currently working on"""
        bug_id = simpledialog.askstring("Add Bug", "Enter Bug ID:")
        if bug_id:
            try:
                bug_info = self.fetch_bug(bug_id)
                if bug_info:
                    self.data['current_bug'] = bug_info
                    self.save_data()
                    self.update_main_page()
                    messagebox.showinfo("Success", f"Bug {bug_id} is now your current bug")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to fetch bug: {str(e)}")
    
    def complete_current_bug(self):
        """Mark current bug as complete and remove it"""
        if self.data['current_bug']:
            bug_id = self.data['current_bug'].get('id', 'Unknown')
            if messagebox.askyesno("Confirm", f"Mark Bug {bug_id} as complete?"):
                self.data['current_bug'] = None
                self.save_data()
                self.update_main_page()
                messagebox.showinfo("Success", "Current bug completed!")
        else:
            messagebox.showwarning("Warning", "No current bug to complete")
    
    def put_on_hold(self):
        """Put current bug on hold"""
        if self.data['current_bug']:
            bug = self.data['current_bug']
            self.data['on_hold_bugs'].append(bug)
            self.data['current_bug'] = None
            self.save_data()
            self.update_main_page()
            messagebox.showinfo("Success", "Bug put on hold")
        else:
            messagebox.showwarning("Warning", "No current bug to put on hold")
    
    def remove_from_hold(self):
        """Remove a bug from hold and make it current"""
        selection = self.hold_listbox.curselection()
        if selection:
            index = selection[0]
            bug = self.data['on_hold_bugs'][index]
            
            if self.data['current_bug']:
                if not messagebox.askyesno("Confirm", "Replace current bug with this one?"):
                    return
            
            self.data['current_bug'] = bug
            self.data['on_hold_bugs'].pop(index)
            self.save_data()
            self.update_main_page()
            messagebox.showinfo("Success", "Bug removed from hold")
        else:
            messagebox.showwarning("Warning", "Please select a bug from the hold list")
    
    def update_main_page(self):
        """Update the main page display"""
        # Update current bug display
        self.current_bug_text.delete('1.0', tk.END)
        if self.data['current_bug']:
            bug = self.data['current_bug']
            info = f"Bug ID: {bug.get('id', 'N/A')}\n"
            info += f"Summary: {bug.get('summary', 'N/A')}\n"
            info += f"Status: {bug.get('status', 'N/A')}\n"
            info += f"Priority: {bug.get('priority', 'N/A')}\n"
            info += f"Assignee: {bug.get('assigned_to', 'N/A')}\n"
            info += f"Severity: {bug.get('severity', 'N/A')}\n"
            info += f"\nDescription:\n{bug.get('description', 'N/A')}"
            self.current_bug_text.insert('1.0', info)
        else:
            self.current_bug_text.insert('1.0', "No bug currently being worked on")
        
        # Update hold list
        self.hold_listbox.delete(0, tk.END)
        for bug in self.data['on_hold_bugs']:
            display = f"Bug {bug.get('id', '?')}: {bug.get('summary', 'No summary')[:60]}"
            self.hold_listbox.insert(tk.END, display)
    
    def fetch_bug(self, bug_id):
        """Fetch a single bug from Bugzilla"""
        if not self.config.get('api_key'):
            raise Exception("API key not configured")
        
        url = f"{self.config['bugzilla_url']}/rest/bug/{bug_id}"
        headers = {'Authorization': f"Bearer {self.config['api_key']}"}
        
        response = requests.get(url, headers=headers, verify=True)
        response.raise_for_status()
        
        data = response.json()
        if 'bugs' in data and len(data['bugs']) > 0:
            bug = data['bugs'][0]
            return {
                'id': bug.get('id'),
                'summary': bug.get('summary'),
                'status': bug.get('status'),
                'priority': bug.get('priority'),
                'severity': bug.get('severity'),
                'assigned_to': bug.get('assigned_to_detail', {}).get('email', 'Unassigned'),
                'description': bug.get('description', ''),
                'last_change_time': bug.get('last_change_time')
            }
        return None
    
    def fetch_bugs(self, filters=None):
        """Fetch bugs from Bugzilla with optional filters"""
        if not self.config.get('api_key'):
            return []
        
        url = f"{self.config['bugzilla_url']}/rest/bug"
        headers = {'Authorization': f"Bearer {self.config['api_key']}"}
        
        params = filters or {}
        
        try:
            response = requests.get(url, headers=headers, params=params, verify=True)
            response.raise_for_status()
            
            data = response.json()
            bugs = []
            for bug in data.get('bugs', []):
                bugs.append({
                    'id': bug.get('id'),
                    'summary': bug.get('summary'),
                    'status': bug.get('status'),
                    'priority': bug.get('priority'),
                    'severity': bug.get('severity'),
                    'assigned_to': bug.get('assigned_to_detail', {}).get('email', 'Unassigned'),
                    'description': bug.get('description', ''),
                    'resolution': bug.get('resolution', ''),
                    'last_change_time': bug.get('last_change_time')
                })
            return bugs
        except Exception as e:
            print(f"Error fetching bugs: {e}")
            return []
    
    def refresh_all_bugs(self):
        """Refresh all bug lists from Bugzilla"""
        if not self.config.get('api_key'):
            messagebox.showwarning("Warning", "Please configure Bugzilla settings first")
            return
        
        try:
            # Fetch all bugs
            self.data['all_bugs'] = self.fetch_bugs()
            
            # Fetch assigned bugs
            if self.config.get('user_email'):
                self.data['assigned_bugs'] = self.fetch_bugs({'assigned_to': self.config['user_email']})
            
            # Fetch resolved fixed bugs
            self.data['resolved_fixed_bugs'] = self.fetch_bugs({
                'status': 'RESOLVED',
                'resolution': 'FIXED'
            })
            
            # Fetch resolved implemented bugs
            self.data['resolved_implemented_bugs'] = self.fetch_bugs({
                'status': 'RESOLVED',
                'resolution': 'IMPLEMENTED'
            })
            
            self.save_data()
            self.update_bug_trees()
            
            last_update = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.status_label.config(text=f"Last update: {last_update}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to refresh bugs: {str(e)}")
    
    def update_bug_trees(self):
        """Update all bug treeviews"""
        self.populate_tree(self.all_bugs_tree, self.data['all_bugs'])
        self.populate_tree(self.assigned_bugs_tree, self.data['assigned_bugs'])
        self.populate_tree(self.resolved_fixed_tree, self.data['resolved_fixed_bugs'])
        self.populate_tree(self.resolved_implemented_tree, self.data['resolved_implemented_bugs'])
    
    def populate_tree(self, tree, bugs):
        """Populate a treeview with bug data"""
        # Clear existing items
        for item in tree.get_children():
            tree.delete(item)
        
        # Add bugs
        for bug in bugs:
            tree.insert('', 'end', values=(
                bug.get('id', ''),
                bug.get('summary', '')[:100],
                bug.get('status', ''),
                bug.get('priority', ''),
                bug.get('assigned_to', '')
            ))
    
    def start_auto_update(self):
        """Start the auto-update thread"""
        self.auto_update_running = True
        self.auto_update_thread = threading.Thread(target=self.auto_update_loop, daemon=True)
        self.auto_update_thread.start()
    
    def auto_update_loop(self):
        """Auto-update loop that runs every 60 seconds"""
        while self.auto_update_running:
            time.sleep(60)  # Wait 1 minute
            if self.config.get('api_key'):
                try:
                    self.refresh_all_bugs()
                except:
                    pass  # Silently fail auto-updates
    
    def on_closing(self):
        """Handle window closing"""
        self.auto_update_running = False
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = BugzillaTracker(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
