import pygame
from os import walk
from random import choice
from utils import get_asset_path

class Car(pygame.sprite.Sprite):
	def __init__(self,pos,groups):
		super().__init__(groups)
		self.name = 'car'

		# Get list of available car images
		cars_path = get_asset_path('TrafficDash', 'graphics', 'cars')
		car_images = []
		for _, _, files in walk(cars_path):
			car_images = [f for f in files if f.endswith('.png')]
		
		# Choose a random car image
		car_name = choice(car_images)
		car_image_path = get_asset_path('TrafficDash', 'graphics', 'cars', car_name)
		self.image = pygame.image.load(car_image_path).convert_alpha()
		self.rect = self.image.get_rect(center = pos)

		# float based movement
		self.pos = pygame.math.Vector2(self.rect.center)

		if pos[0] < 200:
			self.direction = pygame.math.Vector2(1,0)
		else:
			self.direction = pygame.math.Vector2(-1,0)
			self.image = pygame.transform.flip(self.image, True, False)
	
		self.speed = 300

		# collision
		self.hitbox = self.rect.inflate(0,-self.rect.height / 2)
		
	def update(self,dt):
		self.pos += self.direction * self.speed * dt
		self.hitbox.center = (round(self.pos.x), round(self.pos.y))
		self.rect.center = self.hitbox.center

		if not -200 < self.rect.x < 3400:
			self.kill()
