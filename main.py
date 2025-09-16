#!/usr/bin/env python3
"""
Arcade Thesis - Main Game Launcher
A PySide6 application for launching games from the Arcade Thesis project
"""

import sys
import os
import subprocess
import platform
from pathlib import Path
from typing import Optional

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFrame, QScrollArea, QGridLayout,
    QMessageBox, QProgressBar, QSpacerItem, QSizePolicy
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

class GameLauncher(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Arcade Thesis - Game Launcher")
        self.setMinimumSize(800, 600)
        self.setup_ui()
        self.setup_styles()
        
    def setup_ui(self):
        """Setup the main user interface"""
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Header
        header = self.create_header()
        main_layout.addWidget(header)
        
        # Games section
        games_section = self.create_games_section()
        main_layout.addWidget(games_section)
        
        # Footer
        footer = self.create_footer()
        main_layout.addWidget(footer)
        
    def create_header(self) -> QWidget:
        """Create the header section"""
        header_widget = QWidget()
        header_layout = QVBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        # Title
        title_label = QLabel("🎮 Arcade Thesis")
        title_label.setAlignment(Qt.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        
        # Subtitle
        subtitle_label = QLabel("Choose your adventure from our collection of games")
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_font = QFont()
        subtitle_font.setPointSize(12)
        subtitle_label.setFont(subtitle_font)
        subtitle_label.setStyleSheet("color: #7f8c8d; margin-bottom: 20px;")
        
        header_layout.addWidget(title_label)
        header_layout.addWidget(subtitle_label)
        
        return header_widget
    
    def create_games_section(self) -> QWidget:
        """Create the games selection section"""
        games_widget = QWidget()
        games_layout = QVBoxLayout(games_widget)
        games_layout.setContentsMargins(0, 0, 0, 0)
        games_layout.setSpacing(20)
        
        # Games grid
        games_grid = QGridLayout()
        games_grid.setSpacing(20)
        
        # Define games
        games = [
            {
                "name": "Traffic Dash",
                "description": "Navigate through traffic and collect water bottles in this exciting driving game",
                "folder": "TrafficDash",
                "main_file": "main.py",
                "icon": "🚗",
                "color": "#3498db"
            },
            {
                "name": "Cycle Forest",
                "description": "Adventure through a mystical forest on your bicycle in this action-packed game",
                "folder": "Cycleforest",
                "main_file": "main.py",
                "icon": "🌲",
                "color": "#27ae60"
            },
            {
                "name": "Asteroid Shooter",
                "description": "Defend against asteroids in this classic space shooter game",
                "folder": "GameShooter",
                "main_file": "asteriodShooter.py",
                "icon": "🚀",
                "color": "#e74c3c"
            }
        ]
        
        # Create game cards
        for i, game in enumerate(games):
            game_card = self.create_game_card(game)
            row = i // 2
            col = i % 2
            games_grid.addWidget(game_card, row, col)
        
        games_layout.addLayout(games_grid)
        
        return games_widget
    
    def create_game_card(self, game_info: dict) -> QWidget:
        """Create a game card widget"""
        card = QFrame()
        card.setFrameStyle(QFrame.Box)
        card.setLineWidth(2)
        card.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border: 2px solid {game_info['color']};
                border-radius: 15px;
                padding: 20px;
            }}
            QFrame:hover {{
                background-color: #f8f9fa;
                border-color: {game_info['color']};
            }}
        """)
        
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(15)
        
        # Game icon and title
        header_layout = QHBoxLayout()
        
        icon_label = QLabel(game_info["icon"])
        icon_label.setFont(QFont("Arial", 32))
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet(f"color: {game_info['color']};")
        
        title_label = QLabel(game_info["name"])
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet(f"color: {game_info['color']};")
        
        header_layout.addWidget(icon_label)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        # Description
        desc_label = QLabel(game_info["description"])
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("color: #2c3e50; font-size: 12px;")
        
        # Launch button
        launch_btn = QPushButton("🎮 Launch Game")
        launch_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {game_info['color']};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px;
                font-size: 14px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {self.darken_color(game_info['color'])};
            }}
            QPushButton:pressed {{
                background-color: {self.darken_color(game_info['color'], 0.3)};
            }}
        """)
        
        # Connect button to launch function
        launch_btn.clicked.connect(lambda: self.launch_game(game_info))
        
        card_layout.addLayout(header_layout)
        card_layout.addWidget(desc_label)
        card_layout.addWidget(launch_btn)
        
        return card
    
    def create_footer(self) -> QWidget:
        """Create the footer section"""
        footer_widget = QWidget()
        footer_layout = QHBoxLayout(footer_widget)
        footer_layout.setContentsMargins(0, 0, 0, 0)
        
        # System info
        system_info = QLabel(f"System: {platform.system()} {platform.release()}")
        system_info.setStyleSheet("color: #7f8c8d; font-size: 10px;")
        
        # Version info
        version_info = QLabel("Arcade Thesis v1.0")
        version_info.setStyleSheet("color: #7f8c8d; font-size: 10px;")
        
        footer_layout.addWidget(system_info)
        footer_layout.addStretch()
        footer_layout.addWidget(version_info)
        
        return footer_widget
    
    def setup_styles(self):
        """Setup application-wide styles"""
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #ecf0f1, stop:1 #bdc3c7);
            }
            QWidget {
                font-family: 'Segoe UI', Arial, sans-serif;
            }
        """)
    
    def darken_color(self, color: str, factor: float = 0.2) -> str:
        """Darken a hex color by a factor"""
        # Remove # if present
        color = color.lstrip('#')
        
        # Convert to RGB
        r = int(color[0:2], 16)
        g = int(color[2:4], 16)
        b = int(color[4:6], 16)
        
        # Darken
        r = max(0, int(r * (1 - factor)))
        g = max(0, int(g * (1 - factor)))
        b = max(0, int(b * (1 - factor)))
        
        # Convert back to hex
        return f"#{r:02x}{g:02x}{b:02x}"
    
    def launch_game(self, game_info: dict):
        """Launch the selected game"""
        try:
            # Get the game directory
            current_dir = Path(__file__).parent
            game_dir = current_dir / game_info["folder"]
            main_file = game_dir / game_info["main_file"]
            
            # Check if game directory and main file exist
            if not game_dir.exists():
                QMessageBox.critical(
                    self,
                    "Game Not Found",
                    f"Game directory not found: {game_dir}"
                )
                return
            
            if not main_file.exists():
                QMessageBox.critical(
                    self,
                    "Game Not Found",
                    f"Main file not found: {main_file}"
                )
                return
            
            # Launch the game
            print(f"Launching {game_info['name']} from {main_file}")
            
            # Change to game directory and launch
            if platform.system() == "Windows":
                subprocess.Popen([
                    sys.executable, str(main_file)
                ], cwd=str(game_dir))
            else:
                subprocess.Popen([
                    sys.executable, str(main_file)
                ], cwd=str(game_dir))
            
            # Show success message and exit
            # Exit the main application to avoid interference with pygame
            self.close()
            sys.exit(0)
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Launch Error",
                f"Failed to launch {game_info['name']}:\n{str(e)}"
            )

class GameLauncherApp(QApplication):
    def __init__(self, argv):
        super().__init__(argv)
        self.setApplicationName("Arcade Thesis")
        self.setApplicationVersion("1.0")
        self.setOrganizationName("Arcade Thesis Project")

def main():
    """Main application entry point"""
    app = GameLauncherApp(sys.argv)
    
    # Create and show the main window
    window = GameLauncher()
    window.show()
    
    # Start the application event loop
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 