import  pygame, random, math, numpy as np, sys
from pygame.surface import Surface
from ..game.shapestats import ShapeStats
from ..game.gamedata import ColorData
from ..game.powerup2 import Powerup
from createdb import User, Shape as ShapeData
from ..game.circledata import powerup_data
from ..screen_elements.text import Text 

NUM_MENU_SHAPES = 12

class MenuShape(pygame.sprite.Sprite):
    def __init__(self, shape_id, shape_data: ShapeData = 0, color_data: ColorData = 0,  face_images: list[Surface] = 0):
        super().__init__()

        # provided properties
        self.shape_id = shape_id
        self.shape_data = shape_data
        self.color_data = color_data
        self.face_images = face_images

        # shape gameplay attributes
        self.r = random.randint(shape_data.radius_min, shape_data.radius_max)
        self.m = round((3/4) * 3.14 * self.r**3)
        self.hp = shape_data.health
        self.max_hp = shape_data.health
        self.shapes_touching: list[MenuShape] = []
        
        # shape display attributes
        self.alpha_max = 190
        self.alpha = self.alpha_max
        self.shown = True
        self.stuck = False
        self.within_bounds = False

        self.initPos()
        self.initSurface()
        
    # SHAPE INIT HELPERS

    def initPos(self):
        # Calculate position on circle based on shape_id
        circle_radius = 1300
        speed = 6
        total_shapes = NUM_MENU_SHAPES
        screen_center_x = 1920/2
        screen_center_y = 1080/2 

        # Calculate angle for this shape (evenly spaced around circle)
        angle = (2 * math.pi * self.shape_id) / total_shapes
        
        # Position on circle relative to screen center
        self.x = screen_center_x + circle_radius * math.cos(angle)
        self.y = screen_center_y + circle_radius * math.sin(angle)
        
        # Velocity pointing toward screen center
        # Normalize the position vector and multiply by negative speed
        dx = self.x - screen_center_x
        dy = self.y - screen_center_y
        magnitude = math.sqrt(dx**2 + dy**2)
        self.vx = (-speed * dx) / magnitude
        self.vy = (-speed * dy) / magnitude

    def initSurface(self):

        # determine body image
        if self.shape_data.type == 'circle':
            self.body_image = self.color_data.circle_image
        elif self.shape_data.type == 'square':
            self.body_image = self.color_data.square_image
        elif self.shape_data.type == 'triangle':
            self.body_image = self.color_data.triangle_image

        # construct shape images (full sized)
        self.shape_images = []
        for i, face in enumerate(self.face_images):
            body_copy = self.body_image.convert_alpha()
            body_copy.blit(face, [0, 0])

            self.shape_images.append(pygame.transform.smoothscale(body_copy, (self.r*2, self.r*2)))

        # set current shape image
        self.current_shape_image = pygame.transform.smoothscale(self.shape_images[0], (self.r*2, self.r*2))
        self.image = pygame.transform.smoothscale(self.current_shape_image, (self.r*2, self.r*2))
        self.image.set_alpha(self.alpha)
        self.collision_mask = pygame.mask.from_surface(self.current_shape_image)
        self.collision_mask_rect = self.current_shape_image.get_rect()
        self.rect = self.current_shape_image.get_rect()
        self.rect.center = (self.x, self.y)

    # GAME LOOP HELPERS

    def update(self):
        
        self.move()

        if not self.shown and self.alpha > 0:
            self.alpha = max(0, self.alpha - 10)
            self.image.set_alpha(self.alpha)

        elif self.shown and self.alpha < self.alpha_max:
            self.alpha = min(self.alpha_max, self.alpha + 10)
            self.image.set_alpha(self.alpha)

    def move(self):
        # move shape
        if self.stuck: return
        self.x += self.vx
        self.y += self.vy

        # redirect shape back to center if it's too far away
        dist_from_center = math.sqrt((self.x - 960)**2 + (self.y - 540)**2)
        if dist_from_center > 1301:
            # Calculate unit vector pointing to center
            dx = 960 - self.x 
            dy = 540 - self.y
            magnitude = math.sqrt(dx**2 + dy**2)
            
            # Set velocity towards center with speed 10
            self.vx = (10 * dx) / magnitude
            self.vy = (10 * dy) / magnitude
        
        # Set within_bounds when shape is fully inside screen bounds
        if (self.r <= self.x <= 1920 - self.r and self.r <= self.y <= 1080 - self.r):
            self.within_bounds = True

        # ensure shape stays within bounds once it is within bounds
        if self.within_bounds:
            if self.x > 1920 - self.r:
                self.x = 1920 - self.r
                self.vx *= -1

            if self.x < self.r:
                self.x = self.r
                self.vx *= -1

            if self.y > 1080 - self.r:
                self.y = 1080 - self.r
                self.vy *= -1

            if self.y < self.r:
                self.y = self.r
                self.vy *= -1

        # move sprite
        self.rect.center = [round(self.x), round(self.y)]
        self.collision_mask_rect.center = [round(self.x), round(self.y)]

    # COLLISION HELPERS

    def getDamage(self):
        velocity = math.sqrt(self.vx**2 + self.vy**2)

        if velocity == np.nan or str(velocity) == 'nan':
            velocity = 0

        damage = round((velocity * self.m / 500000))
        return damage

    def takeDamage(self, amount):
        self.hp -= amount

        hp_percent = round((self.hp / self.max_hp) * 100)

        if hp_percent >= 75: self.image = self.shape_images[0]
        elif hp_percent < 75 and hp_percent >= 50: self.image = self.shape_images[1]
        elif hp_percent < 50 and hp_percent >= 25: self.image = self.shape_images[2]
        else: self.image = self.shape_images[3]

        self.image.set_alpha(self.alpha)

    def getXY(self):
        return [self.x, self.y]

    def getV(self):
        return [self.vx, self.vy]
    
    def setV(self, vx, vy):
        self.vx = round(vx)
        self.vy = round(vy)

    def getM(self):
        return self.m
    
    # SCREEN ELEMENT HELPERS

    def turnOff(self):
        self.shown = False
        self.stuck = True

    def turnOn(self):
        self.shown = True
        self.stuck = False
