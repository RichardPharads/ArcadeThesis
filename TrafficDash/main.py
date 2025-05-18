import pygame, sys, time
from settings import *
from player import Player
from car import Car
from waterbottle import WaterBottle
from random import choice, randint
from sprite import SimpleSprite, LongSprite
from utils import get_asset_path

class AllSprites(pygame.sprite.Group):
	def __init__(self):
		super().__init__()
		self.offset = pygame.math.Vector2()
		self.bg = pygame.image.load(get_asset_path("TrafficDash", "graphics", "main", "map.png")).convert()
		self.fg = pygame.image.load(get_asset_path("TrafficDash", "graphics", "main", "overlay.png")).convert_alpha()

	def customize_draw(self):
		# change the offset vector
		self.offset.x = player.rect.centerx - WINDOW_WIDTH / 2
		self.offset.y = player.rect.centery - WINDOW_HEIGHT / 2

		# blit the background
		display_surface.blit(self.bg,-self.offset)

		for sprite in sorted(self.sprites(),key = lambda sprite: sprite.rect.centery):
			offset_pos = sprite.rect.topleft - self.offset
			display_surface.blit(sprite.image, offset_pos)

		display_surface.blit(self.fg,-self.offset)	

def quit_game():
	pygame.quit()
	sys.exit()

# basic setup
pygame.init()
display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption('Water Bottle Collector')
clock = pygame.time.Clock()

# groups
all_sprites = AllSprites()
obstacle_sprites = pygame.sprite.Group()
collectible_sprites = pygame.sprite.Group()

# sprites
player = Player((2062,3274), all_sprites, obstacle_sprites)

# timer
car_timer = pygame.event.custom_type()
bottle_timer = pygame.event.custom_type()
pygame.time.set_timer(car_timer, 120)
pygame.time.set_timer(bottle_timer, 3000)  # Spawn water bottle every 3 seconds
pos_list = []

# score
score = 0
font = pygame.font.Font(None, 50)
collect_sound = pygame.mixer.Sound(get_asset_path("TrafficDash", "audio", "collected.wav"))

# music
music = pygame.mixer.Sound(get_asset_path("TrafficDash", "audio", "music.mp3"))
music.play(loops = -1)

def spawn_water_bottle():
	# Only spawn if we have less than 20 bottles
	if len(collectible_sprites) >= 20:
		return None
		
	# Spawn within player's restricted area
	x = randint(640, 2560)  # Player's x boundaries
	y = randint(1180, 3500)  # Player's y boundaries
	
	# Check if position is too close to other bottles (minimum distance of 100 pixels)
	for bottle in collectible_sprites:
		if abs(bottle.rect.centerx - x) < 100 and abs(bottle.rect.centery - y) < 100:
			return None
			
	return WaterBottle((x, y), [all_sprites, collectible_sprites])

def display_score():
	score_text = f'Water Bottles: {score}'
	score_surf = font.render(score_text, True, "white")
	score_rect = score_surf.get_rect(topleft=(10, 10))
	
	# Create background rectangle with padding
	bg_rect = score_rect.inflate(20, 20)
	bg_rect.topleft = (5, 5)
	
	# Draw background with alpha
	bg_surf = pygame.Surface(bg_rect.size)
	bg_surf.fill('black')
	bg_surf.set_alpha(128)  # Semi-transparent background
	
	# Draw background and text
	display_surface.blit(bg_surf, bg_rect)
	display_surface.blit(score_surf, score_rect)

def check_bottle_collision(player, bottle):
	# First do a quick check with rects
	if player.rect.colliderect(bottle.rect):
		# If rects collide, do precise mask collision
		offset_x = bottle.rect.x - player.rect.x
		offset_y = bottle.rect.y - player.rect.y
		if player.mask.overlap(bottle.mask, (offset_x, offset_y)):
			return True
	return False

# sprite setup 
# simple
for file_name, pos_list in SIMPLE_OBJECTS.items():
	path = get_asset_path("TrafficDash", "graphics", "objects", "simple", f"{file_name}.png")
	surf = pygame.image.load(path).convert_alpha()
	for pos in pos_list:
		SimpleSprite(surf, pos, [all_sprites,obstacle_sprites])
# long
for file_name, pos_list in LONG_OBJECTS.items():
	path = get_asset_path("TrafficDash", "graphics", "objects", "long", f"{file_name}.png")
	surf = pygame.image.load(path).convert_alpha()
	for pos in pos_list:
		LongSprite(surf, pos, [all_sprites,obstacle_sprites])

# Spawn initial water bottles (up to 20)
for _ in range(20):
	spawn_water_bottle()

try:
	# game loop
	while True:
		# event loop
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				quit_game()
			if event.type == car_timer:
				random_pos = choice(CAR_START_POSITIONS)
				if random_pos not in pos_list:
					pos_list.append(random_pos)
					pos = (random_pos[0],random_pos[1] + randint(-8,8))
					Car(pos,[all_sprites,obstacle_sprites])
				if len(pos_list) > 5:
					del pos_list[0]
			if event.type == bottle_timer and len(collectible_sprites) < 20:
				spawn_water_bottle()

		# delta time
		dt = clock.tick() / 1000

		# draw background
		display_surface.fill('black')

		# Check for collisions with water bottles
		for bottle in collectible_sprites:
			if check_bottle_collision(player, bottle):
				bottle.kill()
				score += 1
				collect_sound.play()
				# Spawn a new bottle to maintain the number of bottles
				spawn_water_bottle()

		# update and draw game
		all_sprites.update(dt)
		all_sprites.customize_draw()
		display_score()

		# draw the frame
		pygame.display.update()

except Exception as e:
	print(f"Game crashed: {e}")
finally:
	quit_game()
	
