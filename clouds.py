import pygame

class Clouds(pygame.sprite.Sprite):
    def __init__(self, x, y, images, screen):
        super().__init__()
        self.x = x
        self.y = y
        self.frames = 0
        self.images = images
        self.image = self.images[0]
        self.screen = screen

        self.rect = self.image.get_rect()
        self.rect.center = [self.x, self.y]

    def update(self):
        # puff of smoke animation
        self.frames += 2
        if self.frames <= 50:
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
        else:
            self.kill()
        
        self.rect = self.image.get_rect()
        self.rect.center = [self.x, self.y]