from pygame.locals import *
from pygame.transform import smoothscale
from pygame.surface import Surface
from pygame.image import load
from .screenelement import ScreenElement
import pygame

class ToggleButton(ScreenElement):
    def __init__(self, icon_name: str, size: int, center: list[int], invert = False):
        super().__init__(center[0], center[1])
    
        self.icon_selected = smoothscale(load(f'assets/icons/{icon_name}_icon_selected{"_inverted" if invert else ""}.png').convert_alpha(), [size, size])
        self.icon_unselected = smoothscale(load(f'assets/icons/{icon_name}_icon{"_inverted" if invert else ""}.png').convert_alpha(), [size, size])

        self.surface = self.icon_unselected
        self.rect = self.surface.get_rect()
        self.rect.center = center
    
    def update(self, events = None, mouse_pos = None):

        super().update(events, mouse_pos)

        if self.disabled: return

        self.surface = self.icon_selected if self.selected else self.icon_unselected

        if mouse_pos == None: return

        self.surface = self.icon_selected if self.rect.collidepoint(mouse_pos) or self.selected else self.icon_unselected
        for event in events:
            if event.type == MOUSEBUTTONDOWN and self.rect.collidepoint(mouse_pos):
                self.selected = not self.selected
