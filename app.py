from Pyside6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel
from Pyside6.QtCore import Qt, QPropertyAnimation, QEasingCurve
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
                font-size: 28px;
                color: #00ff9d;
                border: none;
                padding: 15px;
                background-color: rgba(0, 255, 157, 0.1);
                margin: 15px;
                text-align: center;
                font-weight: bold;
                border-radius: 12px;
                letter-spacing: 1px;
            }
            
            QPushButton#add_token {
                font-size: 20px;
                color: #ffffff;
                border: none;
                padding: 15px;
                border-radius: 10px;
                background-color: #00ff9d;
                margin: 15px;
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
                font-size: 16px;
                color: #ffffff;
                margin: 10px;
                padding: 8px;
                background-color: rgba(255, 255, 255, 0.05);
                border-radius: 8px;
                text-align: center;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)
        
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
        
        # Set window flags for fullscreen
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.showFullScreen()
        
    def start_token_detection(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        subprocess.Popen([sys.executable, os.path.join(current_dir, "yolo.py")])
        self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = StartWindow()
    window.show()
    sys.exit(app.exec())
