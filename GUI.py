from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QListWidget

class BugApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Bugzilla Monitor")

        self.layout = QVBoxLayout()
        self.list_widget = QListWidget()

        self.layout.addWidget(self.list_widget)
        self.setLayout(self.layout)

        self.refresh()

    def refresh(self):
        self.list_widget.clear()
        for bug, updates in bugs.items():
            self.list_widget.addItem(f"Bug {bug}")
            for u in updates:
                self.list_widget.addItem(f"  - {u}")