from shared_functions import createText
from pygame.surface import Surface
import pygame

class Text:
    def __init__(self, text, size, x, y, align = "center", color = "black", max_width = None, outline_color = None):
        self.text = text
        self.size = size
        self.x = x
        self.y = y
        self.y_init = y
        self.align = align
        self.color = color
        self.xy = [self.x, self.y]
        self.y_scroll = 0
        self.align = align

        if outline_color == None:
            self.surface, self.rect = createText(self.text, self.size, self.color)
        else:
            back, back_rect = createText(self.text, self.size, outline_color)
            front, front_rect = createText(self.text, self.size, self.color)
            self.surface = Surface((back.get_size()[0] + 4, back.get_size()[1]), pygame.SRCALPHA, 32)
            self.rect = self.surface.get_rect()
            # front_rect.center = self.surface.get_size()[0]/2, self.surface.get_size()[1]/2 

            self.surface.blit(back, [0, 0])
            self.surface.blit(front, [4, 0])
            

        if max_width != None:
            while self.surface.get_size()[0] > max_width:
                self.size -= 1
                self.y += 0.5
                self.surface, self.rect = createText(self.text, self.size, self.color)
        
        self.position()

    def position(self):
        self.xy = [self.x, self.y]

        if self.align == "center": self.rect.center = self.xy
        elif self.align == "topleft": self.rect.topleft = self.xy
        elif self.align == "topright": self.rect.topright = self.xy

    def scroll(self, amount):
        self.y_scroll += amount

        self.y = self.y_scroll + self.y_init
        self.position()

    def draw(self, surface):
        surface.blit(self.surface, self.rect)

