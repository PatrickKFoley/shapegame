import pygame
from circledata import *

class PostGameShape(pygame.sprite.Sprite):
    def __init__(self, shape, yours = True):
        super().__init__()
        self.shape = shape
        self.y = 1080/2
        self.image_full =  pygame.image.load("circles/{}/{}/0.png".format(shape.face_id, colors[shape.color_id][0]))
        self.image = pygame.transform.smoothscale(self.image_full, (300, 300))

        if yours: self.x = 250
        else: self.x = 1920 - 250

        self.next_x = self.x
        self.rect = self.image.get_rect()
        self.rect.center = [self.x, self.y]

    def moveTo(self, x):
        self.next_x = x

    def update(self):
        if self.next_x != self.x:

            if self.x < self.next_x:
                self.x += 5

                if self.x > self.next_x: self.x = self.next_x

            if self.x > self.next_x:
                self.x -= 5

                if self.x < self.next_x: self.x = self.next_x

            self.rect.center = [self.x, self.y]