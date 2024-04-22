import pygame


class PowerupDisplayPowerup(pygame.sprite.Sprite):
    def __init__(self, name, id, xy):
        super().__init__()
        self.name = name
        self.id = id
        self.x = xy[0]
        self.y = xy[1]

        self.image_full = pygame.image.load("powerups/{}.png".format(name))
        self.image = pygame.transform.smoothscale(self.image_full, (40, 40))
        self.rect = self.image.get_rect()
        self.rect.center = xy

    def select(self): self.selected = True

    def deselect(self): self.selected = False

    def getName(self): return self.name

    def update(self):
        pass
