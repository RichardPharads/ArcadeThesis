import os

def get_project_root():
    """Get the absolute path to the project root directory."""
    return os.path.dirname(os.path.abspath(__file__))

def get_game_path(game_name):
    """Get the absolute path to a specific game directory."""
    return os.path.join(get_project_root(), game_name)

def get_asset_path(game_name, *paths):
    """
    Get the absolute path for game assets.
    Args:
        game_name (str): Name of the game directory
        *paths: Variable number of path components to join
    Returns:
        str: Absolute path to the asset
    """
    # Get the directory where the script is located
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Join the base directory with the provided paths, ignoring the game_name
    # since we're already in the game directory
    return os.path.join(base_dir, *paths) 