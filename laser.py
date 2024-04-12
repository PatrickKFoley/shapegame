import pygame

class Laser(pygame.sprite.Sprite):
    def __init__(self, circle, g_id, x, y, vx, vy, image, real = True):
        super().__init__()
        self.real = real

        self.g_id = g_id
        self.circle = circle
        self.x = x
        self.y = y
        self.vx = vx *3
        self.vy = vy *3
        self.image = image
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