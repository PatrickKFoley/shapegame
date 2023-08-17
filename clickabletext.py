import pygame


class ClickableText:
    def __init__(self, text, size, x, y):
        self.y = y
        self.x = x
        self.text_unselected, self.text_selected, self.rect = self.createText(text, size)
        self.rect.center = [x, y]

        self.surface = self.text_unselected

    @staticmethod
    def createText(text, size):
        font_small = pygame.font.Font("backgrounds/font.ttf", size)
        font_large = pygame.font.Font("backgrounds/font.ttf", size + 10)

        text_unselected = font_small.render(text, True, "white")
        text_selected = font_large.render(text, True, "lightgray")
        text_rect = text_unselected.get_rect()

        return text_unselected, text_selected, text_rect

    def update(self, mouse_pos):
        if self.rect.collidepoint(mouse_pos):
            self.surface = self.text_selected
            self.rect = self.surface.get_rect()
            self.rect.center = [self.x, self.y]

        else:
            self.surface = self.text_unselected
            self.rect = self.surface.get_rect()
            self.rect.center = [self.x, self.y]
