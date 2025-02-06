# lighting_app.py - Advanced Control Center
import sys
import json
import asyncio
import qasync
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QTabWidget,
                            QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
                            QTimeEdit, QCheckBox, QSystemTrayIcon, QMenu,
                            QAction, QMessageBox, QListWidget, QLineEdit,
                            QDialog, QGridLayout, QComboBox)
from PyQt5.QtCore import Qt, QTimer, QDateTime, QSettings
from PyQt5.QtGui import QIcon, QPalette, QColor
from zeroconf import ServiceBrowser, Zeroconf
from aiohttp import ClientSession

class DeviceManager(QWidget):
    def __init__(self):
        super().__init__()
        self.devices = []
        self.session = ClientSession()
        self.init_ui()
        self.start_discovery()

    def init_ui(self):
        self.setWindowTitle('Lighting Controller')
        self.layout = QVBoxLayout()
        
        # Device List
        self.device_list = QListWidget()
        self.layout.addWidget(self.device_list)
        
        # Connection Info
        self.info_label = QLabel('No device selected')
        self.layout.addWidget(self.info_label)
        
        # Schedule Editor
        self.schedule_tab = ScheduleEditor()
        self.layout.addWidget(self.schedule_tab)
        
        self.setLayout(self.layout)

    def start_discovery(self):
        self.zeroconf = Zeroconf()
        self.listener = MyListener(self)
        self.browser = ServiceBrowser(self.zeroconf, "_http._tcp.local.", self.listener)

class MyListener:
    def __init__(self, manager):
        self.manager = manager

    def add_service(self, zeroconf, type, name):
        info = zeroconf.get_service_info(type, name)
        if info and 'lightctrl' in name.lower():
            ip = socket.inet_ntoa(info.addresses[0])
            self.manager.add_device({
                'name': name,
                'ip': ip,
                'port': info.port
            })

class ScheduleEditor(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.layout = QGridLayout()
        
        # Day Selection
        self.days = []
        for i, day in enumerate(['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']):
            cb = QCheckBox(day)
            self.layout.addWidget(cb, 0, i)
            self.days.append(cb)
        
        # Time Inputs
        self.on_time = QTimeEdit()
        self.off_time = QTimeEdit()
        self.layout.addWidget(QLabel('On Time:'), 1, 0)
        self.layout.addWidget(self.on_time, 1, 1)
        self.layout.addWidget(QLabel('Off Time:'), 1, 2)
        self.layout.addWidget(self.off_time, 1, 3)
        
        # Astro Options
        self.astro_combo = QComboBox()
        self.astro_combo.addItems(['Fixed Time', 'Sunrise', 'Sunset'])
        self.layout.addWidget(self.astro_combo, 2, 0, 1, 4)
        
        # Save Button
        self.save_btn = QPushButton('Save Schedule')
        self.save_btn.clicked.connect(self.save_schedule)
        self.layout.addWidget(self.save_btn, 3, 0, 1, 4)

    def save_schedule(self):
        # Schedule saving logic
        pass

class AuthDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Authentication')
        layout = QVBoxLayout()
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.Password)
        layout.addWidget(QLabel('Enter Admin Password:'))
        layout.addWidget(self.password)
        btn = QPushButton('Authenticate')
        btn.clicked.connect(self.verify)
        layout.addWidget(btn)
        self.setLayout(layout)

    def verify(self):
        # Password verification logic
        self.accept()

@qasync.asyncClose
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings = QSettings('YourCompany', 'LightingControl')
        self.init_ui()
        self.init_tray()

    def init_ui(self):
        self.device_manager = DeviceManager()
        self.setCentralWidget(self.device_manager)
        self.setGeometry(300, 300, 800, 600)
        self.apply_styles()

    def apply_styles(self):
        self.setStyleSheet("""
            QWidget {
                font-size: 12px;
            }
            QListWidget {
                border: 1px solid #444;
                border-radius: 4px;
            }
            QPushButton {
                background: #2c3e50;
                color: white;
                padding: 5px;
                border-radius: 3px;
            }
        """)

    def init_tray(self):
        self.tray = QSystemTrayIcon(self)
        self.tray.setIcon(QIcon('icon.png'))
        menu = QMenu()
        menu.addAction(QAction("Open", self, triggered=self.show))
        menu.addAction(QAction("Exit", self, triggered=QApplication.quit))
        self.tray.setContextMenu(menu)
        self.tray.show()

    def closeEvent(self, event):
        event.ignore()
        self.hide()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    loop = qasync.QEventLoop(app)
    asyncio.set_event_loop(loop)
    
    window = MainWindow()
    window.show()
    
    with loop:
        loop.run_forever()