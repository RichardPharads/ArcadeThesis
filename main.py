from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout , QLabel
import subprocess
import sys
import os

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyQt6 to Pygame Launcher")
        self.setStyleSheet("""
            QLabel#welcome{
                font-size:24px;
                color: green;
            }
        
        """)
        layout = QVBoxLayout()

        self.play_button = QPushButton("Play Asteroid Game")
        self.play_button.clicked.connect(self.launch_game)

        self.play_button2 = QPushButton("Play Cycle Forest")
        self.play_button2.clicked.connect(self.launch_game2)

        self.play_button3 = QPushButton("Play Traffic Dash")
        self.play_button3.clicked.connect(self.launch_game3)

        self.label = QLabel("Welcome to Recyle Arcade")
        self.label.setObjectName('welcome')

        layout.addWidget(self.label)
        layout.addWidget(self.play_button)
        layout.addWidget(self.play_button2)
        layout.addWidget(self.play_button3)
        self.setLayout(layout)

    def launch_game(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        subprocess.Popen([sys.executable, os.path.join(current_dir, "GameShooter", "asteriodShooter.py")])

    def launch_game2(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        subprocess.Popen([sys.executable, os.path.join(current_dir, "Cycleforest", "main.py")])

    def launch_game3(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        subprocess.Popen([sys.executable, os.path.join(current_dir, "TrafficDash", "main.py")])

    def closeEvent(self, event):
        subprocess.Popen([sys.executable, "app.py"])
        event.accept()

app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec())
