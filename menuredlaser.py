import pygame

class MenuRedLaser(pygame.sprite.Sprite):
    def __init__(self, shape, image):
        super().__init__()
        self.shape = shape
        self.x = shape.x
        self.y = shape.y
        self.v_x = shape.v_x *3
        self.v_y = shape.v_y *3
        self.image = image
        self.r = image.get_size()[0]/2
        self.frames = 0
        self.damage = 25
        self.shapes_collided_with = []

        self.rect = self.image.get_rect()
        self.rect.center = [self.x, self.y]

    def update(self):
        self.x += self.v_x
        self.y += self.v_y

        if self.x + self.r > 1920:
            self.x = 1920 - self.r
            self.v_x = -1 * self.v_x

        if self.x - self.r < 0:
            self.x = 0 + self.r
            self.v_x = -1 * self.v_x
        
        if self.y + self.r > 1080:
            self.y = 1080 - self.r
            self.v_y = -1 * self.v_y

        if self.y - self.r < 500:
            self.y = 500 + self.r
            self.v_y = -1 * self.v_y

        self.image.set_alpha(255)

        self.rect.center = [self.x, self.y]

        self.frames += 1
        if self.frames >= 60 * 5:
            self.kill()