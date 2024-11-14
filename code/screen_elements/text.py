from sharedfunctions import createText
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
        self.max_width = max_width
        self.outline_color = outline_color

        self.on = True
        self.alpha = 255

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
        
        self.position()

    def position(self):
        self.xy = [self.x, self.y]

        if self.align == "center": self.rect.center = self.xy
        elif self.align == "topleft": self.rect.topleft = self.xy
        elif self.align == "topright": self.rect.topright = self.xy

    def update(self):

        if not self.on and self.alpha > 0:
            self.alpha = max(self.alpha - 10, 0)
            self.surface.set_alpha(self.alpha)

        elif self.on and self.alpha < 255:
            self.alpha = min(self.alpha + 10, 255)
            self.surface.set_alpha(self.alpha)

    def draw(self, surface):
        surface.blit(self.surface, self.rect)

    def turnOff(self):
        self.on = False

    def turnOn(self):
        self.on = True

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
        
        self.position()