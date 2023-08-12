import pygame

class Killfeed(pygame.sprite.Sprite):
    def __init__(self, left_circle, right_circle, action_img, x, count, screen):
        super().__init__()
        self.left_circle = left_circle
        self.right_circle = right_circle
        self.action_img = action_img
        self.x = x
        self.y = 260 + (60 * count)
        self.next_y = self.y
        self.screen = screen
        self.surface = pygame.Surface((200, 60), pygame.SRCALPHA, 32)
        self.left_img = pygame.transform.scale(left_circle.circle_image, (50, 50))
        self.right_img = pygame.transform.scale(right_circle.circle_image, (50, 50))
        self.frames = 0

        # self.surface.fill("gray")
        # self.surface.set_colorkey((0, 0, 0))
        self.surface.convert_alpha()
        self.surface.blit(self.left_img, (10, 5))
        self.draw_text(str(self.left_circle.getId()), pygame.font.SysFont("bahnschrift", 20), "black", self.surface, 60, 38)
        self.surface.blit(self.action_img, (80, 15))
        self.surface.blit(self.right_img, (140, 5))
        self.draw_text(str(self.right_circle.getId()), pygame.font.SysFont("bahnschrift", 20), "black", self.surface, 190, 38)

        self.image = self.surface
        self.rect = self.image.get_rect()
        self.rect.topleft = [self.x, self.y]

    def update(self, cycle = False):
        # check if they are now cycled out 
        if cycle:
            self.next_y -= 60

            if self.next_y < 260:
                self.kill()
                return
            
        if self.y != self.next_y:
            self.y -= 2

        self.frames += 1 
        if self.frames > 60 * 13: 
            self.kill()
            return 1
        elif self.frames < 60 * 5:
            self.image.set_alpha(255)
            # self.left_img.set_alpha(255)
            # self.right_img.set_alpha(255)
            # self.action_img.set_alpha(255)
        else:
            alpha = 255 + 30 * 5 - self.frames / 2
            self.image.set_alpha(alpha)
            # self.left_img.set_alpha(alpha)
            # self.right_img.set_alpha(alpha)
            # self.action_img.set_alpha(alpha)

        self.rect.topleft = [self.x, self.y]

        # draw elements
        # self.screen.blit(self.surface, (self.x, self.y))
        # self.screen.blit(self.left_img, (self.x + 10, self.y))
        # self.draw_text(str(self.left_circle.getId()), pygame.font.Font("freesansbold.ttf", 20), "black", self.screen, self.x + 60, self.y + 40)
        # self.screen.blit(self.action_img, (self.x + 80, self.y + 10))
        # self.screen.blit(self.right_img, (self.x + 140, self.y))
        # self.draw_text(str(self.right_circle.getId()), pygame.font.Font("freesansbold.ttf", 20), "black", self.screen, self.x + 190, self.y + 40)

    def draw_text(self, text, font, color, surface, x, y):
        text_obj = font.render(text, 1, color)
        text_rect = text_obj.get_rect()
        text_rect.topleft = (x - font.size(text)[0] / 2, y)
        surface.blit(text_obj, text_rect)