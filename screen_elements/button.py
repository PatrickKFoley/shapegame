from pygame.transform import smoothscale
from pygame.surface import Surface
from pygame.image import load

class Button:
    def __init__(self, icon_name: str, size: int, center: list[int]):
    
        self.icon_selected = smoothscale(load(f'backgrounds/{icon_name}_icon_selected.png').convert_alpha(), [size, size])
        self.icon_unselected = smoothscale(load(f'backgrounds/{icon_name}_icon.png').convert_alpha(), [size, size])
        self.surface = self.icon_unselected
        self.rect = self.surface.get_rect()
        self.rect.center = center

        self.disabled = False

    def disable(self):
        self.disabled = True
        self.surface = self.icon_selected

    def enable(self):
        self.disabled = False

    def update(self, mouse_pos):
        if self.disabled: return

        self.surface = self.icon_selected if self.rect.collidepoint(mouse_pos) else self.icon_unselected