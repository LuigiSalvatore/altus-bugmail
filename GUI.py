from PyQt5.QtWidgets import QWidget, QVBoxLayout, QListWidget
from PyQt5.QtCore import QTimer
from persist import bugs

class BugApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Bugzilla Monitor")
        self.resize(600, 400)

        self.layout = QVBoxLayout()
        self.list_widget = QListWidget()

        self.layout.addWidget(self.list_widget)
        self.setLayout(self.layout)

        self.refresh()

        # Update every minute
        self.timer = QTimer()
        self.timer.timeout.connect(self.refresh)
        self.timer.start(60000)

    def refresh(self):
        # Remember selection if possible
        current_row = self.list_widget.currentRow()
        
        self.list_widget.clear()
        # Sort bugs by ID
        sorted_bug_ids = sorted(bugs.keys(), key=lambda x: int(x) if x.isdigit() else 0, reverse=True)
        
        for bug_id in sorted_bug_ids:
            updates = bugs[bug_id]
            self.list_widget.addItem(f"Bug {bug_id}")
            for u in updates:
                item = self.list_widget.addItem(f"  - {u}")
                
        if current_row < self.list_widget.count():
            self.list_widget.setCurrentRow(current_row)