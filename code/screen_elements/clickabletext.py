import pygame
from .screenelement import ScreenElement 

MAX_GROWTH = 6

class ClickableText(ScreenElement):

    def __init__(self, text, size, x, y, alignment = "center", color = [0, 0, 0]):
        super().__init__(x, y)
        self.text = text
        self.alignment = alignment
        self.text_unselected, self.text_selected, self.rect, small = self.createText(text, size, color)
        self.align()

        self.length = small.get_size()[0]
        self.width = small.get_size()[1]

        self.length_width_multiplier = int(self.length/self.width)
        self.growth_amount = 0

        self.buildSurface()

    def buildSurface(self, hover = False):
        if hover:
            self.surface = pygame.transform.smoothscale(self.text_selected, (self.length + self.growth_amount*self.length_width_multiplier, self.width + self.growth_amount))
        else:
            self.surface = pygame.transform.smoothscale(self.text_unselected, (self.length + self.growth_amount*self.length_width_multiplier, self.width + self.growth_amount))

        self.rect = self.surface.get_rect()
        self.align()

    def update(self, events, mouse_pos):

        super().update(events, mouse_pos)

        if self.disabled: return

        if self.rect.collidepoint(mouse_pos):
            if self.growth_amount < MAX_GROWTH:
                self.growth_amount += 1
                self.buildSurface(True)

        else:
            if self.growth_amount > 0:
                self.growth_amount -= 1
                self.buildSurface()

    def getText(self): return self.text

