from pygame.transform import smoothscale
from pygame.surface import Surface
from .screenelement import ScreenElement 
from pygame.image import load

class Button(ScreenElement):
    def __init__(self, icon_name: str, size: int, center: list[int], fast_off = False):
    
        super().__init__(center[0], center[1])

        self.icon_selected = smoothscale(load(f'assets/icons/{icon_name}_icon_selected.png').convert_alpha(), [size, size])
        self.icon_unselected = smoothscale(load(f'assets/icons/{icon_name}_icon.png').convert_alpha(), [size, size])
        self.surface = self.icon_unselected
        self.rect = self.surface.get_rect()
        self.rect.center = center

        if fast_off: self.fastOff()

    def disable(self):
        super().disable()
        self.surface = self.icon_selected

    def update(self, events, mouse_pos):
        # fade in or out
        if not self.shown and self.alpha > 0:
            self.alpha = max(self.alpha - 10, 0)
            self.icon_selected.set_alpha(self.alpha)
            self.icon_unselected.set_alpha(self.alpha)

        elif self.shown and self.alpha < 255:
            self.alpha = min(self.alpha + 10, 255)
            self.icon_selected.set_alpha(self.alpha)
            self.icon_unselected.set_alpha(self.alpha)

        if self.disabled: return

        self.surface = self.icon_selected if (self.rect.collidepoint(mouse_pos) or self.selected) else self.icon_unselected

