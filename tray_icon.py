import os
from PyQt5.QtWidgets import QSystemTrayIcon, QMenu, QAction, QStyle
from PyQt5.QtGui import QIcon

def create_tray(app, window):
    if os.path.exists("icon.png"):
        tray_icon = QIcon("icon.png")
    else:
        tray_icon = app.style().standardIcon(QStyle.SP_MessageBoxInformation)
        
    tray = QSystemTrayIcon(tray_icon, app)

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