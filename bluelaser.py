import pygame

class BlueLaser(pygame.sprite.Sprite):
    def __init__(self, circle, directions, image):
        super().__init__()
        self.circle = circle
        self.g_id = circle.getG_id()
        self.x = circle.getXY()[0]
        self.y = circle.getXY()[1]
        self.vx = directions[0]
        self.vy = directions[1]
        self.image = image
        self.r = image.get_size()[0]/2
        self.ids_collided_with = []

        self.rect = self.image.get_rect()
        self.rect.center = [self.x, self.y]

    def update(self, game):
        self.x += self.vx
        self.y += self.vy

        self.rect.center = [self.x, self.y]

        flag = False
        # ensure laser stays within bounds
        if self.x > game.screen_w - self.r - game.fortnite_x:
            flag = True

        if self.x < self.r + game.fortnite_x:
            flag = True

        if self.y > game.screen_h - self.r - game.fortnite_y:
            flag = True

        if self.y < self.r + game.fortnite_y:
            flag = True

        if flag == True: self.kill()

        self.image.set_alpha(255)
        # game.screen.blit(self.image, (int(self.x - self.image.get_size()[0]/2), int(self.y - self.image.get_size()[1]/2))) 
