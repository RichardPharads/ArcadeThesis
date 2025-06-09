from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve
import subprocess
import sys
import os

class StartWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Recycle Arcade - Starting Point")
        self.setStyleSheet("""
            QWidget {
                background-color: #1a1a1a;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            
            QLabel#title {
                font-size: 32px;
                color: #00ff9d;
                border: none;
                padding: 20px;
                background-color: rgba(0, 255, 157, 0.1);
                margin: 20px;
                text-align: center;
                font-weight: bold;
                border-radius: 15px;
                letter-spacing: 1px;
            }
            
            QPushButton#add_token {
                font-size: 22px;
                color: #ffffff;
                border: none;
                padding: 20px;
                border-radius: 12px;
                background-color: #00ff9d;
                margin: 20px;
                text-align: center;
                font-weight: bold;
                transition: all 0.3s;
            }
            
            QPushButton#add_token:hover {
                background-color: #00cc7d;
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(0, 255, 157, 0.3);
            }
            
            QPushButton#add_token:pressed {
                background-color: #00995e;
                transform: translateY(1px);
            }
            
            QLabel#instructions {
                font-size: 18px;
                color: #ffffff;
                margin: 15px;
                padding: 10px;
                background-color: rgba(255, 255, 255, 0.05);
                border-radius: 10px;
                text-align: center;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Title label
        self.title_label = QLabel("Welcome to Recycle Arcade")
        self.title_label.setObjectName("title")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Instructions label
        self.instructions = QLabel("Click 'Add Token' and show a bottle to start playing!")
        self.instructions.setObjectName("instructions")
        self.instructions.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Add Token button
        self.add_token_button = QPushButton("Add Token")
        self.add_token_button.setObjectName("add_token")
        self.add_token_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.add_token_button.clicked.connect(self.start_token_detection)
        
        layout.addWidget(self.title_label)
        layout.addWidget(self.instructions)
        layout.addWidget(self.add_token_button)
        self.setLayout(layout)
        
        # Set window size and position
        self.setMinimumSize(500, 400)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        
    def start_token_detection(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        subprocess.Popen([sys.executable, os.path.join(current_dir, "yolo.py")])
        self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = StartWindow()
    window.show()
    sys.exit(app.exec())
