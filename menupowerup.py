import pygame

MAX_SIZE = 120

class MenuPowerup(pygame.sprite.Sprite):
    def __init__(self, name, id):
        super().__init__()
        self.name = name
        self.size = 80
        self.growth_amount = 0
        self.center = [(id * 1920/11) + 1920/11,  300]

        self.image_full = pygame.image.load("powerups/{}.png".format(name))
        self.image = pygame.transform.smoothscale(self.image_full, (self.size, self.size))
        self.rect = self.image.get_rect()
        self.rect.center = self.center

        self.selected = False

    def select(self): self.selected = True

    def deselect(self): self.selected = False

    def getName(self): return self.name

    def update(self):
        if self.selected:

            if self.size + self.growth_amount < MAX_SIZE:
                self.growth_amount += 2
            
            self.image = pygame.transform.smoothscale(self.image_full, (self.size + self.growth_amount, self.size + self.growth_amount))
            self.rect = self.image.get_rect()
            self.rect.center = self.center

        elif self.size + self.growth_amount > self.size:
            self.growth_amount -= 2

            self.image = pygame.transform.smoothscale(self.image_full, (self.size + self.growth_amount, self.size + self.growth_amount))
            self.rect = self.image.get_rect()
            self.rect.center = self.center
