import pygame
from .screenelement import ScreenElement 
from sharedfunctions import createText

MAX_GROWTH = 6

class ClickableText(ScreenElement):

    def __init__(self, text, size, x, y, alignment = "center", color = [0, 0, 0], outline_color = None):
        super().__init__(x, y)
        self.text = text
        self.alignment = alignment
        self.outline_color = outline_color

        self.text = text
        self.size = size
        self.color = color
        self.outline_color = outline_color

        # Add growth tracking
        self.growth_amount = 0
        self.base_size = size

        self.buildSurface(size)


    def buildSurface(self, size):
        # build surface
        if self.outline_color == None:  
            self.surface, self.rect = createText(self.text, size, self.color)

        else:
            back, back_rect = createText(self.text, size, self.outline_color)
            front, front_rect = createText(self.text, size, self.color)

            diff = max(2, int(size / 38))

            self.surface = pygame.Surface((back.get_size()[0] + diff, back.get_size()[1]), pygame.SRCALPHA, 32).convert_alpha()
            self.rect = self.surface.get_rect()


            self.surface.blit(back, [0, 0])
            self.surface.blit(front, [diff, 0])

        self.align()

    def update(self, events, mouse_pos):

        super().update(events, mouse_pos)

        if self.disabled: return

        self.hovered = self.rect.collidepoint(mouse_pos)

        target_growth = MAX_GROWTH if (self.hovered) else 0
        if self.growth_amount < target_growth:
            self.growth_amount += 1
            self.resize()
        elif self.growth_amount > target_growth:
            self.growth_amount -= 1
            self.resize()


    def getText(self): return self.text

    def resize(self):
        # Update both input visualizers with new font size
        current_size = self.base_size + self.growth_amount
        self.buildSurface(current_size)
        
        # Update surfaces and alignment
        self.rect = self.surface.get_rect()
        self.align()

