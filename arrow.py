import pygame

MAX_GROWTH = 15

class Arrow:
    def __init__(self, x, y, direction = "->", length = 75, width = 50, growth = 15):
        self.center = [x, y]
        self.direction = direction
        self.length = length
        self.width = width
        self.growth = growth
        self.growth_amount = 0

        if direction == "->": self.image = pygame.image.load("backgrounds/arrow_right.png")
        else: self.image = pygame.image.load("backgrounds/arrow_left.png")

        self.buildSurface()

    def update(self, mouse_pos):
        if self.rect.collidepoint(mouse_pos):
            if self.growth_amount < MAX_GROWTH:
                self.growth_amount += 1
                self.buildSurface()

        else:
            if self.growth_amount > 0:
                self.growth_amount -= 1
                self.buildSurface()

    def buildSurface(self):
        self.surface = pygame.transform.smoothscale(self.image, (self.length + self.growth_amount, self.width + self.growth_amount))
        self.rect = self.surface.get_rect()
        self.rect.center = self.center