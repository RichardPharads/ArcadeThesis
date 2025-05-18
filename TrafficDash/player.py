import pygame, sys
from os import walk
from utils import get_asset_path

class Player(pygame.sprite.Sprite):
	def __init__(self, pos, groups, collision_sprites):
		super().__init__(groups)

		# image
		self.import_assets()
		self.frame_index = 0
		self.status = 'down'
		self.image = self.animations[self.status][self.frame_index]
		self.rect = self.image.get_rect(center = pos)
		self.mask = pygame.mask.from_surface(self.image)  # Create mask from initial image

		# float based movement
		self.pos = pygame.math.Vector2(self.rect.center)
		self.direction = pygame.math.Vector2(0,0)
		self.speed = 200

		# collisions
		self.collision_sprites = collision_sprites
		self.hitbox = self.rect.inflate(0,-self.rect.height / 2)

		# controller setup
		pygame.joystick.init()
		self.joysticks = []
		try:
			for i in range(pygame.joystick.get_count()):
				joystick = pygame.joystick.Joystick(i)
				joystick.init()
				self.joysticks.append(joystick)
		except pygame.error:
			pass  # No joysticks connected

		# deadzone for analog stick
		self.deadzone = 0.2

	def collision(self, direction):
		if direction == 'horizontal':
			for sprite in self.collision_sprites.sprites():
				if sprite.hitbox.colliderect(self.hitbox):
					if hasattr(sprite, 'name') and sprite.name == 'car':
						pygame.quit()
						sys.exit()
					if self.direction.x > 0: # moving right
						self.hitbox.right = sprite.hitbox.left
						self.rect.centerx = self.hitbox.centerx
						self.pos.x = self.hitbox.centerx
					if self.direction.x < 0: # moving left
						self.hitbox.left = sprite.hitbox.right
						self.rect.centerx = self.hitbox.centerx
						self.pos.x = self.hitbox.centerx	
		else:
			for sprite in self.collision_sprites.sprites():
				if sprite.hitbox.colliderect(self.hitbox):
					if hasattr(sprite, 'name') and sprite.name == 'car':
						pygame.quit()
						sys.exit()
					if self.direction.y > 0: # moving down
						self.hitbox.bottom = sprite.hitbox.top
						self.rect.centery = self.hitbox.centery
						self.pos.y = self.hitbox.centery
					if self.direction.y < 0: # moving up
						self.hitbox.top = sprite.hitbox.bottom
						self.rect.centery = self.hitbox.centery
						self.pos.y = self.hitbox.centery

	def import_assets(self):
		self.animations = {}
		player_path = get_asset_path('TrafficDash', 'graphics', 'player')
		
		# Get all animation folders
		for _, folders, _ in walk(player_path):
			for folder in folders:
				self.animations[folder] = []
				
				# Get all images in the animation folder
				folder_path = get_asset_path('TrafficDash', 'graphics', 'player', folder)
				for _, _, files in walk(folder_path):
					for file in sorted(files):  # Sort files to ensure consistent order
						if file.endswith('.png'):
							image_path = get_asset_path('TrafficDash', 'graphics', 'player', folder, file)
							surf = pygame.image.load(image_path).convert_alpha()
							self.animations[folder].append(surf)

	def move(self, dt):

		# to normalized a vector
		if self.direction.magnitude() != 0:
			self.direction = self.direction.normalize()

		# horizontal movement + collisions
		self.pos.x += self.direction.x * self.speed * dt
		self.hitbox.centerx = round(self.pos.x)
		self.rect.centerx = self.hitbox.centerx
		self.collision('horizontal')

		# vertical movement + collisions
		self.pos.y += self.direction.y * self.speed * dt
		self.hitbox.centery = round(self.pos.y)
		self.rect.centery = self.hitbox.centery
		self.collision('vertical')

	def input(self):
		keys = pygame.key.get_pressed()
		
		# Initialize movement to 0
		self.direction.x = 0
		self.direction.y = 0
		
		# Keyboard input
		if keys[pygame.K_RIGHT]:
			self.direction.x = 1
			self.status = 'right'
		elif keys[pygame.K_LEFT]:
			self.direction.x = -1
			self.status = 'left'
			
		if keys[pygame.K_UP]:
			self.direction.y = -1
			self.status = 'up'
		elif keys[pygame.K_DOWN]:
			self.direction.y = 1
			self.status = 'down'

		# Controller input - only process if joysticks are available
		if self.joysticks:  # Only process joystick input if we have joysticks
			for joystick in self.joysticks:
				try:
					# Left analog stick
					x_axis = joystick.get_axis(0)
					y_axis = joystick.get_axis(1)
					
					# Apply deadzone
					if abs(x_axis) > self.deadzone:
						self.direction.x = x_axis
						self.status = 'right' if x_axis > 0 else 'left'
					
					if abs(y_axis) > self.deadzone:
						self.direction.y = y_axis
						self.status = 'down' if y_axis > 0 else 'up'

					# D-pad support
					hat = joystick.get_hat(0)
					if hat[0] > 0:
						self.direction.x = 1
						self.status = 'right'
					elif hat[0] < 0:
						self.direction.x = -1
						self.status = 'left'
						
					if hat[1] > 0:
						self.direction.y = 1
						self.status = 'up'
					elif hat[1] < 0:
						self.direction.y = -1
						self.status = 'down'
				except pygame.error:
					continue  # Skip this joystick if there's an error

	def animate(self, dt):
		current_animations = self.animations[self.status]

		if self.direction.magnitude() != 0:
			self.frame_index += 10 * dt
			if self.frame_index >= len(current_animations):
				self.frame_index = 0
		else:
			self.frame_index = 0	
		
		self.image = current_animations[int(self.frame_index)]
		self.mask = pygame.mask.from_surface(self.image)  # Update mask when image changes

	def restrict(self):
		if self.rect.left < 640:
			self.pos.x = 640 + self.rect.width / 2
			self.hitbox.left = 640
			self.rect.left = 640
		if self.rect.right > 2560:
			self.pos.x = 2560 - self.rect.width / 2
			self.hitbox.right = 2560
			self.rect.right = 2560
		if self.rect.bottom > 3500:
			self.pos.y = 3500 - self.rect.height / 2
			self.rect.bottom = 3500
			self.hitbox.centery = self.rect.centery
		# Prevent moving up when below y=1180
		if self.pos.y > 1180 and self.direction.y < 0:
			self.direction.y = 0
			self.pos.y = max(self.pos.y, 1180 + self.rect.height / 2)

	def update(self, dt):
		self.input()
		self.move(dt)
		self.animate(dt)
		self.restrict()

