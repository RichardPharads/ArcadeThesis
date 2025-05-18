import os
from typing import Dict, Any

# Get the base directory of the game
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Define different themes
THEMES = {
    "default": {
        "player": "king.png",
        "monster": "monster.png",
        "projectile": "fire.png",
        "background": "background.png",
        "music": "time_for_adventure.mp3",
        "scale": {
            "player": (150, 150),
            "monster": (200, 200),
            "projectile": (60, 60),
        }
    },
    "forest": {
        "player": "forest_spirit.png",
        "monster": "dark_creature.png",
        "projectile": "leaf.png",
        "background": "forest_bg.png",
        "music": "forest_theme.mp3",
        "scale": {
            "player": (150, 150),
            "monster": (200, 200),
            "projectile": (60, 60),
        }
    },
    # Add more themes here
}

class AssetLoader:
    def __init__(self, theme: str = "default"):
        self.theme = theme if theme in THEMES else "default"
        self.assets = THEMES[self.theme]
        
    def get_image_path(self, asset_name: str) -> str:
        """Get the full path for an image asset"""
        return os.path.join(BASE_DIR, 'image', self.assets[asset_name])
    
    def get_music_path(self) -> str:
        """Get the full path for the music file"""
        return os.path.join(BASE_DIR, 'music', self.assets["music"])
    
    def get_scale(self, asset_name: str) -> tuple:
        """Get the scale for an asset"""
        return self.assets["scale"].get(asset_name, None)
    
    def change_theme(self, theme: str) -> None:
        """Change the current theme"""
        if theme in THEMES:
            self.theme = theme
            self.assets = THEMES[theme]
            
    @staticmethod
    def get_available_themes() -> list:
        """Get list of available themes"""
        return list(THEMES.keys())
    
    def verify_assets_exist(self) -> bool:
        """Verify that all assets for the current theme exist"""
        missing_assets = []
        
        # Check image assets
        for key, filename in self.assets.items():
            if key != "scale" and key != "music":
                image_path = self.get_image_path(key)
                if not os.path.exists(image_path):
                    missing_assets.append(f"Image: {filename}")
        
        # Check music asset
        music_path = self.get_music_path()
        if not os.path.exists(music_path):
            missing_assets.append(f"Music: {self.assets['music']}")
        
        if missing_assets:
            print("Missing assets:")
            for asset in missing_assets:
                print(f"- {asset}")
            return False
        return True 