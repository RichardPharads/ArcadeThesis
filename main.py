from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout
import subprocess
import sys

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyQt6 to Pygame Launcher")
        layout = QVBoxLayout()

        self.play_button = QPushButton("Play Game")
        self.play_button.clicked.connect(self.launch_game)

        layout.addWidget(self.play_button)
        self.setLayout(layout)

    def launch_game(self):
        subprocess.Popen(["python", "GameShooter/asteriodShooter.py"])

app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec())
