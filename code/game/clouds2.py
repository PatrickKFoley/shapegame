import pygame
from .shape import Shape
from pygame.surface import Surface

class Clouds(pygame.sprite.Sprite):
    def __init__(self, shape: Shape, images: list[Surface]):
        super().__init__()

        self.x = shape.x
        self.y = shape.y
        self.frames = 0

        self.images = images
        self.index = 0
        self.image = self.images[0]
        self.shape = shape

        self.rect = self.image.get_rect()
        self.rect.center = [self.x, self.y]

    def update(self):
        self.frames += 1

        # animate image
        if self.frames % 10 == 0:
            self.index += 1

            if self.index >= len(self.images): self.kill(); return

            self.image = self.images[self.index]
        
        # follow shape
        self.x = self.shape.x
        self.y = self.shape.y
        
        self.rect.center = [self.x, self.y]