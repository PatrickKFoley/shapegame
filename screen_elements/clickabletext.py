import pygame

MAX_GROWTH = 6

class ClickableText:
    def __init__(self, text, size, x, y, alignment = "center"):
        self.y = y
        self.x = x
        self.text = text
        self.alignment = alignment
        self.text_unselected, self.text_selected, self.rect, small = self.createText(text, size)
        self.align()

        self.length = small.get_size()[0]
        self.width = small.get_size()[1]

        self.length_width_multiplier = int(self.length/self.width)
        self.growth_amount = 0

        self.buildSurface()

    def getText(self): return self.text

    @staticmethod
    def createText(text, size):
        font_small = pygame.font.Font("backgrounds/font.ttf", size)
        font_large = pygame.font.Font("backgrounds/font.ttf", size + 10)

        text_small = font_small.render(text, True, "black")
        text_unselected = font_large.render(text, True, "black")
        text_selected = font_large.render(text, True, "darkgray")
        text_rect = text_unselected.get_rect()

        return text_unselected, text_selected, text_rect, text_small
    
    def buildSurface(self, hover = False):
        if hover:
            self.surface = pygame.transform.smoothscale(self.text_selected, (self.length + self.growth_amount*self.length_width_multiplier, self.width + self.growth_amount))
        else:
            self.surface = pygame.transform.smoothscale(self.text_unselected, (self.length + self.growth_amount*self.length_width_multiplier, self.width + self.growth_amount))

        self.rect = self.surface.get_rect()
        self.align()

    def update(self, mouse_pos):
        if self.rect.collidepoint(mouse_pos):
            if self.growth_amount < MAX_GROWTH:
                self.growth_amount += 1
                self.buildSurface(True)

        else:
            if self.growth_amount > 0:
                self.growth_amount -= 1
                self.buildSurface()

    def align(self):
        if self.alignment == "center":
            self.rect.center = [self.x, self.y]
        
        elif self.alignment == "topleft":
            self.rect.topleft = [self.x, self.y]

        elif self.alignment == "topright":
            self.rect.topright = [self.x, self.y]