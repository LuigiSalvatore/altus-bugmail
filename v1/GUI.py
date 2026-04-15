from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem
from PyQt5.QtCore import QTimer
from persist import bugs

class BugApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Bugzilla Monitor")
        self.resize(800, 600)

        self.layout = QVBoxLayout()
        self.tree_widget = QTreeWidget()
        self.tree_widget.setHeaderLabels(["Bug / Update"])
        self.tree_widget.setColumnWidth(0, 600)

        self.layout.addWidget(self.tree_widget)
        self.setLayout(self.layout)

        self.refresh()

        # Update every minute
        self.timer = QTimer()
        self.timer.timeout.connect(self.refresh)
        self.timer.start(60000)

    def refresh(self):
        self.tree_widget.clear()
        # Sort bugs by ID
        sorted_bug_ids = sorted(bugs.keys(), key=lambda x: int(x) if x.isdigit() else 0, reverse=True)

        for bug_id in sorted_bug_ids:
            updates = bugs[bug_id]
            bug_item = QTreeWidgetItem(self.tree_widget)
            bug_item.setText(0, f"Bug {bug_id}")
            bug_item.setExpanded(True)

            for u in updates:
                update_item = QTreeWidgetItem(bug_item)
                update_item.setText(0, u)