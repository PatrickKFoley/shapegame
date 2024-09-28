import pygame

class Powerup(pygame.sprite.Sprite):
    def __init__(self, name, image, xy):
        super().__init__()

        # attributes from game
        # names are "insta-kill", "resurrect", "star", "muscle", "speed", "health", "bomb", "laser", "buckshot", "mushroom"
        self.name = name
        self.image = image
        self.x = xy[0]
        self.y = xy[1]
        
        # attributes necessary for powerup function
        self.frames = 0
        self.r = 10
        
        # surface handling
        self.rect = self.image.get_rect()
        self.rect.center = [self.x, self.y]

    def update(self):
        self.frames += 1

        if self.frames >= (20 * 144):
            self.kill()