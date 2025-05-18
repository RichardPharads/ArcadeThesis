import pygame
from utils import get_asset_path

class WaterBottle(pygame.sprite.Sprite):
    def __init__(self, pos, groups):
        super().__init__(groups)
        # Load and process the water bottle image with transparency
        original_image = pygame.image.load(get_asset_path("TrafficDash", "graphics", "bottle", "Waterbottle.png")).convert_alpha()
        # Scale to approximately the size of the green object
        self.image = pygame.transform.scale(original_image, (64, 64))
        self.rect = self.image.get_rect(center=pos)
        # Create a mask for precise collision detection
        self.mask = pygame.mask.from_surface(self.image)
        self.name = 'waterbottle' 