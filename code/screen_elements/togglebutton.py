from pygame.locals import *
from pygame.transform import smoothscale
from pygame.surface import Surface
from pygame.image import load

class ToggleButton:
    def __init__(self, icon_name: str, size: int, center: list[int]):
    
        self.icon_selected = smoothscale(load(f'assets/icons/{icon_name}_icon_selected.png').convert_alpha(), [size, size])
        self.icon_unselected = smoothscale(load(f'assets/icons/{icon_name}_icon.png').convert_alpha(), [size, size])
        self.surface = self.icon_unselected
        self.rect = self.surface.get_rect()
        self.rect.center = center

        self.x = center[0]
        self.y = center[1]

        self.disabled = False
        self.selected = False

        self.on = True
        self.alpha = 255

    def select(self): self.selected = True
    
    def deselect(self): self.selected = False

    def draw(self, surface: Surface):
        surface.blit(self.surface, self.rect)

    def disable(self):
        self.disabled = True
        self.surface = self.icon_selected

    def enable(self):
        self.disabled = False

    def update(self, mouse_pos = None, events = None):

        if not self.on and self.alpha > 0:
            self.alpha = max(self.alpha - 10, 0)
            self.surface.set_alpha(self.alpha)
        elif self.on and self.alpha < 255:
            self.alpha = min(self.alpha + 10, 255)
            self.surface.set_alpha(self.alpha)

        if self.disabled: return

        self.surface = self.icon_selected if self.selected else self.icon_unselected

        if mouse_pos == None: return

        self.surface = self.icon_selected if self.rect.collidepoint(mouse_pos) or self.selected else self.icon_unselected
        for event in events:
            if event.type == MOUSEBUTTONDOWN and self.rect.collidepoint(mouse_pos):
                self.selected = not self.selected

    def turnOff(self):
        self.on = False
        self.disabled = True

    def turnOn(self):
        self.on = True
        self.disabled = False