import pygame, numpy as np
from pygame.surface import Surface
from .shape import Shape

class Buckshot(pygame.sprite.Sprite):
    def __init__(self, shape: Shape, direction: list[int], images: list[Surface], real = True):
        super().__init__()
        self.real = real
        self.type = 'buckshot'

        self.damage = 10

        # range of motion
        self.screen_w = 1920-460
        self.screen_h = 1080

        self.shape = shape
        self.team_id = shape.team_id
        self.x = shape.x
        self.y = shape.y
        self.vx = direction[0]
        self.vy = direction[1]
        self.r = 20
        self.ids_collided_with = []
        self.fading = False

        self.frames = 0
        self.image_index = 0
        self.images = images
        self.image = self.images[self.image_index]
        self.mask = pygame.mask.from_surface(self.image)
        self.alpha = 255

        if not self.real: return

        self.rect = self.image.get_rect()
        self.collision_mask = pygame.mask.from_surface(self.image)
        self.rect.center = [self.x, self.y]

    def setV(self, vx, vy):
        self.vx = round(vx)
        self.vy = round(vy)

    def checkCircleCollision(self, circle_r: int):
        x = self.x + self.vx
        y = self.y + self.vy

        dist = np.sqrt((x - 730) ** 2 + (y - 540) ** 2)

        if dist >= (circle_r - self.r):
            nv = np.array([x - 730, y - 540]) / dist  
            dp = np.dot([self.vx, self.vy], nv)
            vf = np.array([self.vx, self.vy]) - 2 * dp * nv
            
            self.setV(vf[0], vf[1])

            offset = (circle_r - self.r) - dist
            self.x += nv[0] * offset
            self.y += nv[1] * offset

            self.fading = True

    def update(self, circle_r: int):
        # determine if you are touching the oval
        self.checkCircleCollision(circle_r)

        self.x += self.vx
        self.y += self.vy

        # ensure laser stays within bounds
        if self.x > self.screen_w - self.r:
            self.x = self.screen_w - self.r
            self.vx *= -1

            self.fading = True

        if self.x < self.r:
            self.x = self.r
            self.vx *= -1

            self.fading = True

        if self.y > self.screen_h - self.r:
            self.y = self.screen_h - self.r
            self.vy *= -1

            self.fading = True

        if self.y < self.r:
            self.y = self.r
            self.vy *= -1

            self.fading = True

        if not self.real: return

        self.rect.center = [self.x, self.y]

        # animate image
        self.frames += 1
        if self.frames % 10 == 0:
            self.image_index += 1

            if self.image_index >= len(self.images): self.image_index = 0
            
            self.image = self.images[self.image_index]

        # fade out
        if self.fading:
            self.alpha -= 8

            if self.alpha <= 0: self.kill()
            
            self.image.set_alpha(self.alpha)
        else: self.image.set_alpha(255)
