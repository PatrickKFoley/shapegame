import pygame, math

class Laser(pygame.sprite.Sprite):
    def __init__(self, shape, image, real = True):
        super().__init__()
        self.shape = shape
        self.image = image
        self.real = real

        desired_speed = 8
        current_speed = math.sqrt(shape.v_x**2 + shape.v_y**2)
        multiplier = desired_speed / current_speed

        self.g_id = shape.g_id
        self.x = shape.x
        self.y = shape.y
        self.vx = shape.v_x * multiplier * 3
        self.vy = shape.v_y * multiplier * 3
        
        self.r = 20
        self.frames = 0
        self.ids_collided_with = []

        if not self.real: return

        self.rect = self.image.get_rect()
        self.rect.center = [self.x, self.y]

    def update(self, game):
        self.x += self.vx
        self.y += self.vy

        # ensure laser stays within bounds
        if self.x > game.screen_w - self.r - game.fortnite_x:
            self.x = game.screen_w - self.r - game.fortnite_x
            self.vx = -1 * self.vx

        if self.x < self.r + game.fortnite_x:
            self.x = self.r + game.fortnite_x
            self.vx = -1 * self.vx

        if self.y > game.screen_h - self.r - game.fortnite_y:
            self.y = game.screen_h - self.r - game.fortnite_y
            self.vy = -1 * self.vy

        if self.y < self.r + game.fortnite_y:
            self.y = self.r + game.fortnite_y
            self.vy = -1 * self.vy

        if self.real:
            self.image.set_alpha(255)
            self.rect.center = [self.x, self.y]

        self.frames += 1
        if self.frames >= game.fps * 5:
            self.kill()