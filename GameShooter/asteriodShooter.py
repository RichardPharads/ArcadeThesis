import pygame, sys, os
from random import randint, uniform
from pygame.locals import *

class AssetManager:
    def __init__(self):
        self.current_dir = os.path.dirname(__file__)
        self.graphics = {}
        self.sounds = {}
        self.fonts = {}
        
        # Define asset paths
        self.asset_paths = {
            'graphics': {
                'ship': "graphics/ship2.png",
                'background': "graphics/images.png",
                'laser': "graphics/laser.png",
                'meteor': "graphics/waterbottle.png"
            },
            'sounds': {
                'laser': "sounds/laser.ogg",
                'explosion': "sounds/explosion.wav",
                'background_music': "sounds/music.wav"
            },
            'fonts': {
                'main': "graphics/subatomic.ttf"
            }
        }
        
        self.load_all_assets()
    
    def get_path(self, file_path):
        return os.path.join(self.current_dir, file_path)
    
    def load_all_assets(self):
        # Load graphics
        for key, path in self.asset_paths['graphics'].items():
            full_path = self.get_path(path)
            self.graphics[key] = pygame.image.load(full_path).convert_alpha()
            
        # Special case for background to use convert() instead of convert_alpha()
        self.graphics['background'] = pygame.image.load(
            self.get_path(self.asset_paths['graphics']['background'])
        ).convert()
        
        # Load sounds
        for key, path in self.asset_paths['sounds'].items():
            full_path = self.get_path(path)
            self.sounds[key] = pygame.mixer.Sound(full_path)
            
        # Load fonts
        for key, path in self.asset_paths['fonts'].items():
            full_path = self.get_path(path)
            self.fonts[key] = pygame.font.Font(full_path, 50)

def laser_update(laser_list, speed=300):
    for rect in laser_list[:]:  # Iterate over a copy to safely remove items
        rect.y -= speed * dt
        if rect.bottom < 0:
            laser_list.remove(rect)

def meteor_update(meteor_list, speed=200):
    for meteor_tuple in meteor_list[:]:  # Iterate over a copy to safely remove items
        direction = meteor_tuple[1]
        meteor_rect = meteor_tuple[0]
        meteor_rect.center += direction * speed * dt
        if meteor_rect.top > WINDOW_HEIGHT:
            meteor_list.remove(meteor_tuple)            

def display_score():
    score_text = f'Survival Score: {pygame.time.get_ticks() // 1000}'
    text_surf = assets.fonts['main'].render(score_text, True, (255,255,255))
    text_rect = text_surf.get_rect(midbottom=(WINDOW_WIDTH/2, WINDOW_HEIGHT-80))
    display_surface.blit(text_surf, text_rect)
    pygame.draw.rect(display_surface, (255,255,255), text_rect.inflate(30,30), width=8, border_radius=5)

def laser_cooldown(can_shoot, duration=0):
    if not can_shoot:
        current_time = pygame.time.get_ticks()
        if current_time - shoot_time > duration:
            can_shoot = True
    return can_shoot        

# Game init 
pygame.init()
WINDOW_WIDTH, WINDOW_HEIGHT = 1280, 720
display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption('Meteor Shooter')
clock = pygame.time.Clock()

# Initialize asset manager
assets = AssetManager()

# Controller setup
pygame.joystick.init()
joysticks = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]
for joystick in joysticks:
    joystick.init()

# Deadzone for analog sticks and movement speed
DEADZONE = 0.2
SHIP_SPEED = 800  # Higher speed for smoother controller movement

# Game objects setup
ship_rect = assets.graphics['ship'].get_rect(center=(WINDOW_WIDTH/2, WINDOW_HEIGHT/2))
laser_list = []
meteor_list = []

# Laser cooldown
can_shoot = True
shoot_time = None

# Start background music
assets.sounds['background_music'].play(loops=-1)

# Meteor timer
meteor_timer = pygame.event.custom_type()
pygame.time.set_timer(meteor_timer, 500)

# Game state
game_active = True

while True:
    # Event loop
    for event in pygame.event.get():    
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
        
        # Controller connection/disconnection handling
        if event.type == JOYDEVICEADDED:
            joysticks = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]
            for joystick in joysticks:
                joystick.init()
        elif event.type == JOYDEVICEREMOVED:
            joysticks = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]
        
        # Controller button press (for shooting)
        if event.type == JOYBUTTONDOWN and can_shoot and game_active:
            # Check common shoot buttons (A/X on Xbox-style, Cross/Circle on PlayStation)
            if event.button in (0, 1, 2, 3):  # Adjust based on your controller
                laser_rect = assets.graphics['laser'].get_rect(midbottom=ship_rect.midtop)
                laser_list.append(laser_rect)
                can_shoot = False
                shoot_time = pygame.time.get_ticks()
                assets.sounds['laser'].play()
        
        # Keyboard shooting (spacebar)
        if event.type == KEYDOWN and can_shoot and game_active:
            if event.key == K_SPACE:
                laser_rect = assets.graphics['laser'].get_rect(midbottom=ship_rect.midtop)
                laser_list.append(laser_rect)
                can_shoot = False
                shoot_time = pygame.time.get_ticks()
                assets.sounds['laser'].play()
        
        if event.type == meteor_timer and game_active:
            x_pos = randint(-100, WINDOW_WIDTH + 100)
            y_pos = randint(-100, -50)
            meteor_rect = assets.graphics['meteor'].get_rect(center=(x_pos, y_pos))
            direction = pygame.math.Vector2(uniform(-0.5, 0.5), 1)
            meteor_list.append((meteor_rect, direction))

    # Delta time for frame-rate independent movement
    dt = clock.tick(120) / 1000

    if game_active:
        # Controller movement
        if joysticks:
            joystick = joysticks[0]  # Use first controller
            
            # Left stick movement with deadzone
            axis_x = joystick.get_axis(0)
            axis_y = joystick.get_axis(1)
            
            # Apply deadzone and normalize
            if abs(axis_x) < DEADZONE:
                axis_x = 0
            else:
                axis_x = (abs(axis_x) - DEADZONE) * (axis_x / abs(axis_x))
            
            if abs(axis_y) < DEADZONE:
                axis_y = 0
            else:
                axis_y = (abs(axis_y) - DEADZONE) * (axis_y / abs(axis_y))
            
            # Move ship based on controller input
            ship_rect.x += int(axis_x * SHIP_SPEED * dt)
            ship_rect.y += int(axis_y * SHIP_SPEED * dt)
        
        # Mouse movement (only if no controller connected)
        if not joysticks:
            ship_rect.center = pygame.mouse.get_pos()
        
        # Keep ship on screen
        ship_rect.clamp_ip(pygame.Rect(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT))
        
        # Shooting (mouse or controller button held)
        if (pygame.mouse.get_pressed()[0] or (joysticks and joystick.get_button(0))) and can_shoot:
            laser_rect = assets.graphics['laser'].get_rect(midbottom=ship_rect.midtop)
            laser_list.append(laser_rect)
            can_shoot = False
            shoot_time = pygame.time.get_ticks()
            assets.sounds['laser'].play()
        
        # Update game elements
        laser_update(laser_list)
        meteor_update(meteor_list)
        can_shoot = laser_cooldown(can_shoot, 400)
        
        # Meteor-ship collisions
        ship_mask = pygame.mask.from_surface(assets.graphics['ship'])
        meteor_mask = pygame.mask.from_surface(assets.graphics['meteor'])
        for meteor_tuple in meteor_list[:]:
            meteor_rect = meteor_tuple[0]
            if ship_rect.colliderect(meteor_rect): #This line is still useful for optimization
                offset_x = meteor_rect.left - ship_rect.left
                offset_y = meteor_rect.top - ship_rect.top
                overlap = ship_mask.overlap(meteor_mask, (offset_x, offset_y))
                if overlap:
                    assets.sounds['explosion'].play()
                    game_active = False  # Game over instead of immediate exit
                    break #Exit the loop after a collision is detected
        
        # Laser-meteor collisions
        for laser_rect in laser_list[:]:
            for meteor_tuple in meteor_list[:]:
                if laser_rect.colliderect(meteor_tuple[0]):
                    meteor_list.remove(meteor_tuple)
                    laser_list.remove(laser_rect)
                    assets.sounds['explosion'].play()
                    break

    # Drawing
    display_surface.blit(assets.graphics['background'], (0, 0))
    
    if game_active:
        for rect in laser_list:
            display_surface.blit(assets.graphics['laser'], rect)
        
        for meteor_tuple in meteor_list:
            display_surface.blit(assets.graphics['meteor'], meteor_tuple[0])
        
        display_surface.blit(assets.graphics['ship'], ship_rect)
        display_score()
    else:
        # Game over screen
        game_over_text = assets.fonts['main'].render("GAME OVER", True, (255, 0, 0))
        restart_text = assets.fonts['main'].render("Press Button O to restart", True, (255, 255, 255))
        display_surface.blit(game_over_text, (WINDOW_WIDTH/2 - game_over_text.get_width()/2, WINDOW_HEIGHT/2 - 50))
        display_surface.blit(restart_text, (WINDOW_WIDTH/2 - restart_text.get_width()/2, WINDOW_HEIGHT/2 + 50))
        
        # Restart game
        keys = pygame.key.get_pressed()
        if keys[K_r]:
            game_active = True
            ship_rect.center = (WINDOW_WIDTH/2, WINDOW_HEIGHT/2)
            laser_list.clear()
            meteor_list.clear()
            can_shoot = True
            pygame.time.set_timer(meteor_timer, 500)  # Reset meteor timer
        if event.type == pygame.JOYBUTTONDOWN and not game_active:
            if event.button == 1:  # Circle button (adjust if needed)
                game_active = True
                ship_rect.center = (WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2)
                laser_list.clear()
                meteor_list.clear()
                can_shoot = True
                pygame.time.set_timer(meteor_timer, 500)

            if event.button == 2:  # Square button (adjust if needed)
               pygame.quit()
               sys.exit()
            

    pygame.display.update()
