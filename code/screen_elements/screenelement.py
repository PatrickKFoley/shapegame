import pygame

class ScreenElement:
    def __init__(self, x, y, fast_off = False):
        self.x = x
        self.y = y

        self.surface = None
        self.rect = None
        self.alignment = 'center'

        self.alpha = 255
        self.shown = True
        self.disabled = False
        self.selected = False
        self.hovered = False

    def isHovAndEnabled(self, mouse_pos):
        return not self.disabled and self.rect.collidepoint(mouse_pos)

    def draw(self, surface):
        if self.alpha == 0: return


        surface.blit(self.surface, self.rect)   

    def fastOff(self):
        self.turnOff()
        self.alpha = 0
        self.surface.set_alpha(0)

    def turnOff(self):
        self.shown = False
        self.disable()

    def turnOn(self):
        self.shown = True
        self.enable()

    def disable(self):
        self.disabled = True

    def enable(self):
        self.disabled = False

    def select(self): self.selected = True
    
    def deselect(self): self.selected = False

    def update(self, events, rel_mouse_pos):
        # fade in or out
        if not self.shown and self.alpha > 0:
            self.alpha = max(self.alpha - 10, 0)
            self.surface.set_alpha(self.alpha)

        elif self.shown and self.alpha < 255:
            self.alpha = min(self.alpha + 10, 255)
            self.surface.set_alpha(self.alpha)

    def align(self):
        if self.alignment == 'center':

            self.rect.center = [self.x, self.y]
        
        elif self.alignment == 'topleft':
            self.rect.topleft = [self.x, self.y]

        elif self.alignment == 'topright':
            self.rect.topright = [self.x, self.y]

    def createText(self, text, size, color):
        font_small = pygame.font.Font('assets/misc/font.ttf', size)
        font_large = pygame.font.Font('assets/misc/font.ttf', size + 10)

        light_color = [max(color[0] - 100, 0), max(color[1] - 100, 0), max(color[2] - 100, 0)]

        text_small = font_small.render(text, True, color)
        text_unselected = font_large.render(text, True, color)
        text_selected = font_large.render(text, True, light_color)
        text_rect = text_unselected.get_rect()

        return text_unselected, text_selected, text_rect, text_small