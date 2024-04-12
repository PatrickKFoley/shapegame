import pygame

class MenuBlackLaser(pygame.sprite.Sprite):
    def __init__(self, shape, directions, image):
        super().__init__()
        self.shape = shape
        self.x = shape.x
        self.y = shape.y
        self.v_x = directions[0]
        self.v_y = directions[1]
        self.image = image
        self.r = image.get_size()[0]/2
        self.damage = 10
        self.shapes_collided_with = []

        self.rect = self.image.get_rect()
        self.rect.center = [self.x, self.y]

    def update(self):
        flag = False
        # ensure laser stays within bounds
        self.x += self.v_x
        self.y += self.v_y

        if self.x + self.r > 1920:
            flag = True

        if self.x - self.r < 0:
            flag = True
        
        if self.y + self.r > 1080:
            flag = True

        if self.y - self.r < 500:
            flag = True

        self.rect.center = [self.x, self.y]

        self.image.set_alpha(255)

        if flag: self.kill()
        # game.screen.blit(self.image, (int(self.x - self.image.get_size()[0]/2), int(self.y - self.image.get_size()[1]/2))) 
