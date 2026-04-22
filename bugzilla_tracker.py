import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import requests
import json
import os
import webbrowser
from datetime import datetime
import threading
import time
from apiBugzilla import Bugzilla

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
        self.view_settings = self.config.get('view_settings', {
            'Priority': True,
            'Assignee': True,
            'Product': False,
            'Activity': False,
            'Sub-Activity': False,
            'Importance': False,
            'Version': False
        })
        self.view_vars = {name: tk.BooleanVar(value=self.view_settings.get(name, default)) for name, default in {
            'Priority': True,
            'Assignee': True,
            'Product': False,
            'Activity': False,
            'Sub-Activity': False,
            'Importance': False,
            'Version': False
        }.items()}
        self.bugzilla_client = self.create_bugzilla_client()
        
        # Auto-update flag
        self.auto_update_running = False
        
        # Create UI
        self.create_menu()
        self.create_ui()
        
        # Start auto-update thread
        self.start_auto_update()
        
        # Initial data fetch
        if self.config.get('api_key'):
            self.refresh_all_bugs()
    
    def load_config(self):
        """Load Bugzilla configuration from file"""
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                config = json.load(f)
            config.setdefault('bugzilla_url', 'https://vmbugzilla.altus.com.br/demandas')
            config.setdefault('api_key', '')
            config.setdefault('user_email', '')
            config.setdefault('view_settings', {
                'Priority': True,
                'Assignee': True,
                'Product': False,
                'Activity': False,
                'Sub-Activity': False,
                'Importance': False,
                'Version': False
            })
            return config
        return {
            'bugzilla_url': 'https://vmbugzilla.altus.com.br/demandas',
            'api_key': '',
            'user_email': '',
            'view_settings': {
                'Priority': True,
                'Assignee': True,
                'Product': False,
                'Activity': False,
                'Sub-Activity': False,
                'Importance': False,
                'Version': False
            }
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
            'assigned_bugs': [],
            'resolved_fixed_bugs': [],
            'resolved_implemented_bugs': [],
            'all_bugs': [],
            'last_update': None
        }
    
    def create_bugzilla_client(self):
        """Create the Bugzilla API client using configured URL and API key."""
        if not self.config.get('api_key'):
            return None
        url = self.config.get('bugzilla_url', '').strip()
        if url:
            return Bugzilla(self.config['api_key'], url=url)
        return Bugzilla(self.config['api_key'])
    
    def normalize_bug(self, bug):
        return {
            'id': bug.get('id'),
            'summary': bug.get('summary'),
            'status': bug.get('status'),
            'priority': bug.get('priority'),
            'severity': bug.get('severity'),
            'assigned_to': bug.get('assigned_to_detail', {}).get('email', bug.get('assigned_to', 'Unassigned')),
            'product': bug.get('product', ''),
            'activity': bug.get('cf_activity', bug.get('activity', '')),
            'sub_activity': bug.get('cf_subactivity', bug.get('sub_activity', '')),
            'importance': bug.get('importance', ''),
            'version': bug.get('version', ''),
            'description': bug.get('description', ''),
            'resolution': bug.get('resolution', ''),
            'last_change_time': bug.get('last_change_time')
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

        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_checkbutton(label="Show Priority", variable=self.view_vars['Priority'], command=self.update_display_columns)
        view_menu.add_checkbutton(label="Show Assignee", variable=self.view_vars['Assignee'], command=self.update_display_columns)
        view_menu.add_checkbutton(label="Show Product", variable=self.view_vars['Product'], command=self.update_display_columns)
        view_menu.add_checkbutton(label="Show Activity", variable=self.view_vars['Activity'], command=self.update_display_columns)
        view_menu.add_checkbutton(label="Show Sub-Activity", variable=self.view_vars['Sub-Activity'], command=self.update_display_columns)
        view_menu.add_checkbutton(label="Show Importance", variable=self.view_vars['Importance'], command=self.update_display_columns)
        view_menu.add_checkbutton(label="Show Version", variable=self.view_vars['Version'], command=self.update_display_columns)
        view_menu.add_separator()
        view_menu.add_command(label="Move current main tab left", command=self.move_current_main_tab_left)
        view_menu.add_command(label="Move current main tab right", command=self.move_current_main_tab_right)
        view_menu.add_separator()
        view_menu.add_command(label="Move active bug category left", command=self.move_current_bug_category_left)
        view_menu.add_command(label="Move active bug category right", command=self.move_current_bug_category_right)
    
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
        self.bugs_notebook = ttk.Notebook(bugs_frame)
        self.bugs_notebook.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Assigned Bugs Tab
        self.assigned_bugs_tree = self.create_bug_tree(self.bugs_notebook, "Assigned")
        
        # Resolved Fixed Tab
        self.resolved_fixed_tree = self.create_bug_tree(self.bugs_notebook, "Resolved - Fixed")
        
        # Resolved Implemented Tab
        self.resolved_implemented_tree = self.create_bug_tree(self.bugs_notebook, "Resolved - Implemented")
                
        # All Bugs Tab
        self.all_bugs_tree = self.create_bug_tree(self.bugs_notebook, "All Bugs")
        
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
        
        tree = ttk.Treeview(
            tree_frame,
            columns=('ID', 'Summary', 'Status', 'Priority', 'Assignee', 'Product', 'Activity', 'Sub-Activity', 'Importance', 'Version'),
            show='headings',
            yscrollcommand=scrollbar.set
        )
        
        tree.heading('ID', text='Bug ID')
        tree.heading('Summary', text='Summary')
        tree.heading('Status', text='Status')
        tree.heading('Priority', text='Priority')
        tree.heading('Assignee', text='Assignee')
        tree.heading('Product', text='Product')
        tree.heading('Activity', text='Activity')
        tree.heading('Sub-Activity', text='Sub-Activity')
        tree.heading('Importance', text='Importance')
        tree.heading('Version', text='Version')
        
        tree.column('ID', width=80)
        tree.column('Summary', width=400)
        tree.column('Status', width=120)
        tree.column('Priority', width=80)
        tree.column('Assignee', width=150)
        tree.column('Product', width=120)
        tree.column('Activity', width=120)
        tree.column('Sub-Activity', width=120)
        tree.column('Importance', width=120)
        tree.column('Version', width=120)
        
        tree['displaycolumns'] = self.get_display_columns()
        
        tree.pack(side='left', fill='both', expand=True)
        scrollbar.config(command=tree.yview)
        
        # Bind double-click and Enter key to open bug in browser
        tree.bind('<Double-1>', lambda e: self.open_bug_in_browser(tree))
        tree.bind('<Return>', lambda e: self.open_bug_in_browser(tree))
        
        return tree
    
    def get_display_columns(self):
        columns = ['ID', 'Summary', 'Status']
        for name in ['Priority', 'Assignee', 'Product', 'Activity', 'Sub-Activity', 'Importance', 'Version']:
            if self.view_vars.get(name) and self.view_vars[name].get():
                columns.append(name)
        return columns
    
    def update_display_columns(self):
        self.view_settings = {name: var.get() for name, var in self.view_vars.items()}
        self.config['view_settings'] = self.view_settings
        self.save_config()
        for tree in [self.all_bugs_tree, self.assigned_bugs_tree, self.resolved_fixed_tree, self.resolved_implemented_tree]:
            tree['displaycolumns'] = self.get_display_columns()
    
    def move_current_main_tab_left(self):
        current = self.notebook.index(self.notebook.select())
        if current > 0:
            self.notebook.insert(current - 1, self.notebook.select())
    
    def move_current_main_tab_right(self):
        current = self.notebook.index(self.notebook.select())
        count = len(self.notebook.tabs())
        if current < count - 1:
            self.notebook.insert(current + 1, self.notebook.select())
    
    def move_current_bug_category_left(self):
        current = self.bugs_notebook.index(self.bugs_notebook.select())
        if current > 0:
            self.bugs_notebook.insert(current - 1, self.bugs_notebook.select())
    
    def move_current_bug_category_right(self):
        current = self.bugs_notebook.index(self.bugs_notebook.select())
        count = len(self.bugs_notebook.tabs())
        if current < count - 1:
            self.bugs_notebook.insert(current + 1, self.bugs_notebook.select())
    
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
            self.bugzilla_client = self.create_bugzilla_client()
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
            info += f"Product: {bug.get('product', 'N/A')}\n"
            info += f"Activity: {bug.get('activity', 'N/A')}\n"
            info += f"Sub-Activity: {bug.get('sub_activity', 'N/A')}\n"
            info += f"Importance: {bug.get('importance', 'N/A')}\n"
            info += f"Version: {bug.get('version', 'N/A')}\n"
            info += f"Severity: {bug.get('severity', 'N/A')}\n"
            info += f"\nDescription:\n{bug.get('description', 'N/A')}"
            comments = bug.get('comments', [])
            if comments:
                info += "\n\nComments:\n"
                for comment in comments:
                    author = comment.get('author', 'Unknown')
                    created = comment.get('creation_time', '')
                    text = comment.get('text', '').strip()
                    info += f"--- {author} {created} ---\n{text}\n\n"
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
        if not self.bugzilla_client:
            raise Exception("API key not configured")

        bugs = self.bugzilla_client.Get_Bug_Information(
            bug_id,
            'id',
            'summary',
            'status',
            'priority',
            'severity',
            'assigned_to',
            'product',
            'cf_activity',
            'cf_subactivity',
            'importance',
            'version',
            'description',
            'last_change_time'
        )
        if bugs and len(bugs) > 0:
            bug = self.normalize_bug(bugs[0])
            bug['comments'] = self.fetch_comments(bug_id)
            return bug
        return None
    
    def fetch_bugs(self, filters=None):
        """Fetch bugs from Bugzilla with optional filters"""
        if not self.bugzilla_client:
            return []
        
        params = filters or {}
        try:
            bugs = self.bugzilla_client.MakeRequest(
                params,
                'id',
                'summary',
                'status',
                'priority',
                'severity',
                'assigned_to',
                'assigned_to_detail',
                'product',
                'cf_activity',
                'cf_subactivity',
                'importance',
                'version',
                'description',
                'resolution',
                'last_change_time'
            )
            if not bugs:
                return []
            return [self.normalize_bug(bug) for bug in bugs]
        except Exception as e:
            print(f"Error fetching bugs: {e}")
            return []
    
    def refresh_all_bugs(self):
        """Refresh all bug lists from Bugzilla"""
        if not self.config.get('api_key'):
            messagebox.showwarning("Warning", "Please configure Bugzilla settings first")
            return
        
        if not self.config.get('user_email'):
            messagebox.showwarning("Warning", "Please configure user email to fetch assigned bugs")
            return
        
        try:
            assigned_to = self.config['user_email']
            
            # Fetch all bugs assigned to the configured user
            self.data['all_bugs'] = self.fetch_bugs({'assigned_to': assigned_to})
            
            # Fetch assigned bugs (only ASSIGNED status)
            self.data['assigned_bugs'] = self.fetch_bugs({
                'assigned_to': assigned_to,
                'status': 'ASSIGNED'
            })
            
            # Fetch resolved fixed bugs assigned to the configured user
            self.data['resolved_fixed_bugs'] = self.fetch_bugs({
                'assigned_to': assigned_to,
                'status': 'RESOLVED',
                'resolution': 'FIXED'
            })
            
            # Fetch resolved implemented bugs assigned to the configured user
            self.data['resolved_implemented_bugs'] = self.fetch_bugs({
                'assigned_to': assigned_to,
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
                bug.get('assigned_to', ''),
                bug.get('product', ''),
                bug.get('activity', ''),
                bug.get('sub_activity', ''),
                bug.get('importance', ''),
                bug.get('version', '')
            ))
    
    def fetch_comments(self, bug_id):
        if not self.bugzilla_client:
            return []
        try:
            return self.bugzilla_client.Get_Bug_Comment(bug_id) or []
        except Exception as e:
            print(f"Error fetching bug comments: {e}")
            return []
    
    def open_bug_in_browser(self, tree):
        """Open the selected bug in the default web browser"""
        selection = tree.selection()
        if selection:
            item = selection[0]
            values = tree.item(item, 'values')
            if values and len(values) > 0:
                bug_id = values[0]  # Bug ID is the first column
                if bug_id:
                    # Construct the Bugzilla URL
                    base_url = self.config.get('bugzilla_url', '').rstrip('/')
                    if '/demandas' not in base_url:
                        base_url += '/demandas'
                    bug_url = f"{base_url}/show_bug.cgi?id={bug_id}"
                    
                    try:
                        webbrowser.open(bug_url)
                    except Exception as e:
                        messagebox.showerror("Error", f"Failed to open browser: {str(e)}")
    
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
