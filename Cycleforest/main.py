import pygame
import sys
import random
from os.path import join
from pygame.math import Vector2
from assets_config import AssetLoader

# Initialize pygame and mixer
pygame.init()
pygame.mixer.init()

# Initialize asset loader with default theme
asset_loader = AssetLoader("default")

# Verify assets exist
if not asset_loader.verify_assets_exist():
    print("Error: Some required assets are missing. Please check the assets directories.")
    pygame.quit()
    sys.exit(1)

# Load and play music
pygame.mixer.music.load(asset_loader.get_music_path())
pygame.mixer.music.play(-1)

# Set up display
clock = pygame.time.Clock()
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 480
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))


# Load images
def load_image(name, scale=None):
    try:
        img = pygame.image.load(asset_loader.get_image_path(name)).convert_alpha()
        return pygame.transform.scale(img, scale) if scale else img
    except:
        print(f"Failed to load image: {name}")
        return pygame.Surface((50, 50), pygame.SRCALPHA)


# Background
background = load_image("background", (SCREEN_WIDTH, SCREEN_HEIGHT))

# Player setup
player_surf = load_image("player", asset_loader.get_scale("player"))
player_rect = player_surf.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2))
player_direction = Vector2()  # For horizontal movement
player_speed = 300  # Reduced for smaller screen
facing_right = True  # Track which way player is facing
player_health = 3
invincible = False
invincible_timer = 0
invincible_duration = 1.0  # 1 second of invincibility after hit

# Fire projectile setup
fire_surf = load_image("projectile", asset_loader.get_scale("projectile"))
fire_projectiles = []
fire_speed = 400  # Reduced for smaller screen
fire_cooldown = 0.3  # seconds between shots
last_fire_time = 0

# Monster setup
monster_surf = load_image("monster", asset_loader.get_scale("monster"))
monsters = []
monster_spawn_timer = 0
monster_spawn_interval = 2.0  # seconds between spawns
monster_speed = 100  # Reduced for smaller screen

# Jumping and gravity variables
gravity = 800  # Reduced for smaller screen
jump_height = -400  # Reduced for smaller screen
vertical_velocity = 0
is_jumping = False
is_on_ground = True
double_jump_available = True
ground_level = SCREEN_HEIGHT  # Ground is at bottom of screen

# Game variables
running = True
score = 0
font = pygame.font.Font(None, 32)  # Slightly smaller font
controller_deadzone = 0.2

# Controller setup
joystick = None
if pygame.joystick.get_count() > 0:
    joystick = pygame.joystick.Joystick(0)
    joystick.init()
    print(f"Controller connected: {joystick.get_name()}")


def spawn_monster():
    """Spawn a new monster from left, right or ground level"""
    spawn_point = random.choice(["left", "right", "ground"])

    if spawn_point == "left":
        x = -monster_surf.get_width()
        y = ground_level - monster_surf.get_height()
        direction = Vector2(1, 0)  # Move right
    elif spawn_point == "right":
        x = SCREEN_WIDTH
        y = ground_level - monster_surf.get_height()
        direction = Vector2(-1, 0)  # Move left
    else:  # "ground"
        x = random.randint(0, SCREEN_WIDTH)
        y = ground_level - monster_surf.get_height()
        # Move toward player
        if x < player_rect.centerx:
            direction = Vector2(1, 0)  # Move right
        else:
            direction = Vector2(-1, 0)  # Move left

    monsters.append({
        'rect': pygame.Rect(x, y, monster_surf.get_width(), monster_surf.get_height()),
        'direction': direction,
        'speed': monster_speed
    })


def handle_controller_input():
    """Process continuous controller input for movement"""
    global player_direction, facing_right

    if not joystick:
        return

    # Left stick movement (axes 0 and 1)
    left_x = joystick.get_axis(0)
    left_y = joystick.get_axis(1)

    # Apply deadzone
    if abs(left_x) < controller_deadzone:
        left_x = 0
    if abs(left_y) < controller_deadzone:
        left_y = 0

    # Update facing direction
    if left_x > 0.1:
        facing_right = True
    elif left_x < -0.1:
        facing_right = False

    # Create a new vector for this frame's movement
    controller_vector = Vector2(left_x, 0)  # Only horizontal movement

    # Only update player_direction if there's significant input
    if controller_vector.length() > 0:
        player_direction.x = controller_vector.normalize().x


def handle_jump_input():
    """Handle jump input from both keyboard and controller"""
    global vertical_velocity, is_jumping, is_on_ground, double_jump_available

    # Keyboard jump (space key)
    keyboard_jump = pygame.key.get_pressed()[pygame.K_SPACE]

    # Controller jump (A button - button 0)
    controller_jump = joystick and joystick.get_button(0) if joystick else False

    if (keyboard_jump or controller_jump):
        if is_on_ground:
            vertical_velocity = jump_height
            is_jumping = True
            is_on_ground = False
        elif double_jump_available and not is_on_ground:
            vertical_velocity = jump_height * 0.8  # Slightly weaker double jump
            double_jump_available = False
            is_jumping = True


def fire_projectile():
    """Create a new fire projectile"""
    global last_fire_time

    current_time = pygame.time.get_ticks() / 1000  # Convert to seconds
    if current_time - last_fire_time < fire_cooldown:
        return  # Still on cooldown

    last_fire_time = current_time

    # Create projectile at player position
    direction = 1 if facing_right else -1
    projectile = {
        'rect': pygame.Rect(
            player_rect.centerx,
            player_rect.centery,
            fire_surf.get_width(),
            fire_surf.get_height()
        ),
        'direction': direction,
        'speed': fire_speed
    }
    fire_projectiles.append(projectile)


def update_projectiles(dt):
    """Update all active projectiles"""
    global score

    projectiles_to_keep = []
    for proj in fire_projectiles:
        proj['rect'].x += proj['direction'] * proj['speed'] * dt

        # Check for monster collisions
        hit_monster = False
        for monster in monsters[:]:
            if proj['rect'].colliderect(monster['rect']):
                monsters.remove(monster)
                hit_monster = True
                score += 10
                break

        # Keep projectiles that are still on screen and didn't hit anything
        if not hit_monster and 0 < proj['rect'].x < SCREEN_WIDTH:
            projectiles_to_keep.append(proj)

    # Update the projectiles list
    fire_projectiles.clear()
    fire_projectiles.extend(projectiles_to_keep)


def update_monsters(dt):
    """Update all monsters"""
    global player_health, invincible, invincible_timer

    for monster in monsters:
        monster['rect'].x += monster['direction'].x * monster['speed'] * dt
        monster['rect'].y += monster['direction'].y * monster['speed'] * dt

        # Check for player collision if not invincible
        if not invincible and monster['rect'].colliderect(player_rect):
            player_health -= 1
            invincible = True
            invincible_timer = pygame.time.get_ticks() / 1000
            # Knockback effect
            knockback_dir = Vector2(player_rect.centerx - monster['rect'].centerx,
                                    player_rect.centery - monster['rect'].centery).normalize()
            player_rect.x += knockback_dir.x * 50
            player_rect.y += knockback_dir.y * 50


def draw_health():
    """Draw player health as hearts"""
    heart_surf = pygame.Surface((20, 20), pygame.SRCALPHA)  # Smaller hearts
    pygame.draw.polygon(heart_surf, (255, 0, 0), [(10, 0), (0, 20), (20, 20)])
    pygame.draw.circle(heart_surf, (255, 0, 0), (6, 6), 6)
    pygame.draw.circle(heart_surf, (255, 0, 0), (14, 6), 6)

    for i in range(player_health):
        screen.blit(heart_surf, (10 + i * 25, 10))  # Adjusted spacing


def draw_score():
    """Draw the current score"""
    score_text = font.render(f"Score: {score}", True, (255, 255, 255))
    screen.blit(score_text, (SCREEN_WIDTH - 100, 10))  # Adjusted position


def change_theme(new_theme):
    """Change the game theme and reload all assets"""
    global background, player_surf, fire_surf, monster_surf
    
    asset_loader.change_theme(new_theme)
    
    # Reload all assets with new theme
    background = load_image("background", (SCREEN_WIDTH, SCREEN_HEIGHT))
    player_surf = load_image("player", asset_loader.get_scale("player"))
    fire_surf = load_image("projectile", asset_loader.get_scale("projectile"))
    monster_surf = load_image("monster", asset_loader.get_scale("monster"))
    
    # Load and play new music
    pygame.mixer.music.load(asset_loader.get_music_path())
    pygame.mixer.music.play(-1)


# Main game loop
while running:
    dt = clock.tick(60) / 1000  # Delta time in seconds

    # Spawn monsters periodically
    current_time = pygame.time.get_ticks() / 1000
    if current_time - monster_spawn_timer > monster_spawn_interval:
        spawn_monster()
        monster_spawn_timer = current_time

    # Handle invincibility timer
    if invincible:
        if current_time - invincible_timer > invincible_duration:
            invincible = False

    # Reset horizontal direction each frame
    player_direction.x = 0

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_q):
            running = False

        # Music and theme controls
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                pygame.mixer.music.pause()
            elif event.key == pygame.K_o:
                pygame.mixer.music.unpause()
            elif event.key == pygame.K_x:  # Fire projectile with X key
                fire_projectile()
            # Theme switching with number keys
            elif event.key in [pygame.K_1, pygame.K_2]:
                themes = asset_loader.get_available_themes()
                theme_index = event.key - pygame.K_1
                if theme_index < len(themes):
                    change_theme(themes[theme_index])

        # Controller button events
        if joystick and event.type == pygame.JOYBUTTONDOWN:
            if event.button == 0:  # A button - jump
                handle_jump_input()
            elif event.button == 1:  # B button - fire projectile
                fire_projectile()

    # Keyboard movement input
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] or keys[pygame.K_RIGHT]:
        # Update facing direction
        if keys[pygame.K_RIGHT]:
            facing_right = True
        if keys[pygame.K_LEFT]:
            facing_right = False

        # Create keyboard vector
        keyboard_vector = Vector2(
            keys[pygame.K_RIGHT] - keys[pygame.K_LEFT],
            0  # Only horizontal movement
        )
        if keyboard_vector.length() > 0:
            player_direction.x = keyboard_vector.normalize().x

    # Handle jump input (space key)
    if keys[pygame.K_SPACE]:
        handle_jump_input()

    # Controller movement input
    handle_controller_input()

    # Apply gravity
    vertical_velocity += gravity * dt
    player_rect.y += vertical_velocity * dt

    # Apply horizontal movement
    player_rect.x += player_direction.x * player_speed * dt

    # Ground collision
    if player_rect.bottom >= ground_level:
        player_rect.bottom = ground_level
        vertical_velocity = 0
        is_on_ground = True
        is_jumping = False
        double_jump_available = True
    else:
        is_on_ground = False

    # Keep player on screen horizontally
    player_rect.left = max(0, player_rect.left)
    player_rect.right = min(SCREEN_WIDTH, player_rect.right)

    # Keep player on screen vertically
    player_rect.top = max(0, player_rect.top)
    player_rect.bottom = min(SCREEN_HEIGHT, player_rect.bottom)

    # Update game objects
    update_projectiles(dt)
    update_monsters(dt)

    # Game over check
    if player_health <= 0:
        running = False

    # Drawing
    screen.blit(background, (0, 0))

    # Draw all monsters
    for monster in monsters:
        screen.blit(monster_surf, monster['rect'])

    # Draw all projectiles
    for proj in fire_projectiles:
        screen.blit(fire_surf, proj['rect'])

    # Draw player (flip image if facing left) with invincibility flash
    if not invincible or int(current_time * 10) % 2 == 0:  # Flash when invincible
        player_image = player_surf if facing_right else pygame.transform.flip(player_surf, True, False)
        screen.blit(player_image, player_rect)

    # Draw UI
    draw_health()
    draw_score()

    pygame.display.update()

# Game over screen
screen.fill((0, 0, 0))
game_over_text = font.render("GAME OVER", True, (255, 0, 0))
final_score_text = font.render(f"Final Score: {score}", True, (255, 255, 255))
screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
screen.blit(final_score_text, (SCREEN_WIDTH // 2 - final_score_text.get_width() // 2, SCREEN_HEIGHT // 2 + 10))
pygame.display.update()

# Wait a few seconds before quitting
pygame.time.wait(3000)

pygame.quit()
sys.exit()