import pygame

MAX_GROWTH = 6

class ClickableText:
    def __init__(self, text, size, x, y, alignment = "center", color = [0, 0, 0]):
        self.y = y
        self.x = x
        self.text = text
        self.alignment = alignment
        self.text_unselected, self.text_selected, self.rect, small = self.createText(text, size, color)
        self.align()

        self.disabled = False
        self.on = True
        self.alpha = 255

        self.length = small.get_size()[0]
        self.width = small.get_size()[1]

        self.length_width_multiplier = int(self.length/self.width)
        self.growth_amount = 0

        self.buildSurface()

    def getText(self): return self.text

    @staticmethod
    def createText(text, size, color):
        font_small = pygame.font.Font("assets/misc/font.ttf", size)
        font_large = pygame.font.Font("assets/misc/font.ttf", size + 10)

        light_color = [max(color[0] - 100, 0), max(color[1] - 100, 0), max(color[2] - 100, 0)]

        text_small = font_small.render(text, True, color)
        text_unselected = font_large.render(text, True, color)
        text_selected = font_large.render(text, True, light_color)
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

        if not self.on and self.alpha > 0:
            self.alpha = max(self.alpha - 10, 0)
            self.surface.set_alpha(self.alpha)

        elif self.on and self.alpha < 255:
            self.alpha = min(self.alpha + 10, 255)
            self.surface.set_alpha(self.alpha)

        if self.disabled: return

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

    def draw(self, surface):
        surface.blit(self.surface, self.rect)

    def turnOff(self):
        self.on = False
        self.disabled = True

    def turnOn(self):
        self.on = True
        self.disabled = False