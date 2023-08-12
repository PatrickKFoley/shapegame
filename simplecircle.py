import pygame, random
from pygame.locals import *
from circledata import *

class SimpleCircle(pygame.sprite.Sprite):
    def __init__(self, xy, image):
        super().__init__()
        self.x = xy[0]
        self.y = xy[1]
        self.vx = random.randint(-4, 4)
        self.vy = random.randint(-3, 3)
        self.r = random.randint(50, 60)
        self.m = random.randint(10, 15)
        self.frames = 0

        self.face_id = random.randint(0, 2)
        self.color_string = colors[random.randint(0, len(colors)-1)][0]
        self.image = pygame.transform.scale(image, (self.r * 2, self.r * 2))

        self.rect = self.image.get_rect()
        self.rect.center = [self.x, self.y]

    def update(self):
         # ensure circle stays within bounds
        if self.x > 1920 - self.r:
            self.x = 1920 - self.r
            self.vx = -1 * self.vx

        if self.x < self.r:
            self.x = self.r
            self.vx = -1 * self.vx

        if self.y > 400 - self.r:
            self.y = 400 - self.r
            self.vy = -1 * self.vy

        if self.y < self.r:
            self.y = self.r
            self.vy = -1 * self.vy

        # update position
        self.rect.center = [self.x, self.y]
        
        self.x += self.vx
        self.y += self.vy
        self.frames += 1
        self.rect.center = [self.x, self.y]

    def setVel(self, vel):
        self.vx = vel[0]
        self.vy = vel[1]