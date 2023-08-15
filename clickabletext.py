import pygame

class ClickableText:
    def __init__(self, text, size, x, y):
        self.text_unselected, self.text_selected, self.rect = self.createText(text, size)
        self.rect.center = [x, y]

        self.surface = self.text_unselected

    def createText(self, text, size):
        font = pygame.font.Font("backgrounds/font.ttf", size)

        text_unselected = font.render(text, True, "white")
        text_selected = font.render(text, True, "lightgray")
        text_rect = text_unselected.get_rect()

        return text_unselected, text_selected, text_rect
    
    def update(self, mouse_pos):
        if self.rect.collidepoint(mouse_pos):
            self.surface = self.text_selected
        else:
            self.surface = self.text_unselected
