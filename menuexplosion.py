import pygame

class MenuExplosion(pygame.sprite.Sprite):
    def __init__(self, x, y, images):
        super().__init__()
        self.x = x
        self.y = y
        self.frames = 0
        self.images = images
        self.image = self.images[0]
        self.damage = 400

        self.rect = self.image.get_rect()
        self.rect.center = [self.x, self.y]

    def update(self):
        # explosion animation
        self.frames += 2
        if self.frames <= 70:
            if self.frames <= 10:
                self.image = self.images[0]
            elif self.frames <= 20:
                self.image = self.images[1]
            elif self.frames <= 30:
                self.image = self.images[2]
            elif self.frames <= 40:
                self.image = self.images[3]
            elif self.frames <= 50:
                self.image = self.images[4]
            elif self.frames <= 60:
                self.image = self.images[5]
            elif self.frames <= 70:
                self.image = self.images[6]
        else:
            self.kill()

        self.rect = self.image.get_rect()
        self.rect.center = [self.x, self.y]