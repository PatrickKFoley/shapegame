from sharedfunctions import createText
from pygame.surface import Surface
import pygame
from .screenelement import ScreenElement

class Text(ScreenElement):
    def __init__(self, text, size, x, y, align = "center", color = "black", max_width = None, outline_color = None, fast_off = False):
        super().__init__(x, y)

        self.text = text
        self.size = size
        self.y_init = y
        self.alignment = align
        self.color = color
        self.xy = [self.x, self.y]
        self.y_scroll = 0
        self.max_width = max_width
        self.outline_color = outline_color

        if outline_color == None:
            self.surface, self.rect = createText(self.text, self.size, self.color)
        else:
            back, back_rect = createText(self.text, self.size, outline_color)
            front, front_rect = createText(self.text, self.size, self.color)
            self.surface = Surface((back.get_size()[0] + 4, back.get_size()[1]), pygame.SRCALPHA, 32)
            self.rect = self.surface.get_rect()

            self.surface.blit(back, [0, 0])
            self.surface.blit(front, [4, 0])
            

        if max_width != None:
            while self.surface.get_size()[0] > max_width:
                self.size -= 1
                self.y += 0.5
                self.surface, self.rect = createText(self.text, self.size, self.color)
        
        self.align()
        if fast_off: self.fastOff()

    def updateText(self, text: str):
        self.text = text

        if self.outline_color == None:
            self.surface, self.rect = createText(self.text, self.size, self.color)
        else:
            back, back_rect = createText(self.text, self.size, self.outline_color)
            front, front_rect = createText(self.text, self.size, self.color)
            self.surface = Surface((back.get_size()[0] + 4, back.get_size()[1]), pygame.SRCALPHA, 32)
            self.rect = self.surface.get_rect()

            self.surface.blit(back, [0, 0])
            self.surface.blit(front, [4, 0])
            

        if self.max_width != None:
            while self.surface.get_size()[0] > self.max_width:
                self.size -= 1
                self.y += 0.5
                self.surface, self.rect = createText(self.text, self.size, self.color)
        
        self.align()