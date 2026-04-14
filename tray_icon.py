from PyQt5.QtWidgets import QSystemTrayIcon, QMenu, QAction
from PyQt5.QtGui import QIcon

def create_tray(app, window):
    tray = QSystemTrayIcon(QIcon("icon.png"), app)

    menu = QMenu()

    show_action = QAction("Show")
    quit_action = QAction("Quit")

    show_action.triggered.connect(window.show)
    quit_action.triggered.connect(app.quit)

    menu.addAction(show_action)
    menu.addAction(quit_action)

    tray.setContextMenu(menu)
    tray.show()

    return tray