from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel, QFrame
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QPalette, QColor
import subprocess
import sys
import os

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Recycle Arcade")
        self.setMinimumSize(400, 500)
        self.setStyleSheet("""
            QWidget {
                background-color: #1a1a2e;
                color: #ffffff;
            }
            QLabel#welcome {
                font-size: 32px;
                color: #4ecca3;
                padding: 20px;
                border-radius: 10px;
                background-color: #16213e;
                margin: 20px;
                text-align: center;
                font-weight: bold;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QPushButton {
                font-size: 18px;
                color: #ffffff;
                border: none;
                padding: 15px;
                border-radius: 8px;
                background-color: #0f3460;
                margin: 10px 20px;
                text-align: center;
                font-weight: bold;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QPushButton:hover {
                background-color: #4ecca3;
                color: #1a1a2e;
                transition: all 0.3s;
            }
            QPushButton:pressed {
                background-color: #2a9d8f;
            }
        """)

        # Create main layout with spacing
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Welcome label with modern styling
        self.label = QLabel("Welcome to\nRecycle Arcade")
        self.label.setObjectName('welcome')
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Create buttons with modern styling
        self.play_button = QPushButton("🚀 Play Asteroid Game")
        self.play_button.clicked.connect(self.launch_game)
        self.play_button.setCursor(Qt.CursorShape.PointingHandCursor)

        self.play_button2 = QPushButton("🌲 Play Cycle Forest")
        self.play_button2.clicked.connect(self.launch_game2)
        self.play_button2.setCursor(Qt.CursorShape.PointingHandCursor)

        self.play_button3 = QPushButton("🚗 Play Traffic Dash")
        self.play_button3.clicked.connect(self.launch_game3)
        self.play_button3.setCursor(Qt.CursorShape.PointingHandCursor)

        # Add widgets to layout
        layout.addWidget(self.label)
        layout.addStretch(1)
        layout.addWidget(self.play_button)
        layout.addWidget(self.play_button2)
        layout.addWidget(self.play_button3)
        layout.addStretch(1)

        self.setLayout(layout)

    def launch_game(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        subprocess.Popen([sys.executable, os.path.join(current_dir, "GameShooter", "asteriodShooter.py")])
        self.close()

    def launch_game2(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        subprocess.Popen([sys.executable, os.path.join(current_dir, "Cycleforest", "main.py")])
        self.close()

    def launch_game3(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        subprocess.Popen([sys.executable, os.path.join(current_dir, "TrafficDash", "main.py")])
        self.close()

    def closeEvent(self, event):
        subprocess.Popen([sys.executable, "app.py"])
        event.accept()

app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec())
