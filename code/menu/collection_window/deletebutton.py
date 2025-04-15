from ...screen_elements.holdbutton import HoldButton
from ...screen_elements.text import Text
from pygame.surface import Surface
from pygame.image import load
from pygame.transform import smoothscale
import pygame

class DeleteButton(HoldButton):
    def __init__(self, center: list[int], fast_off = False):
        super().__init__('trash', center, fast_off)

        self.delete_phrase = ['delete shape?', '(irreversible)']
        self.disabled_phrase = ['not able to', 'delete shape!']

        self.delete_text = Text(self.delete_phrase, 30, 115, 20)
        self.delete_text.draw(self.text_surface)

    def update(self, events, mouse_pos):
        
        rerender = False
        if self.disabled and self.delete_text.text == self.delete_phrase:
            self.delete_text.updateText(self.disabled_phrase, color='red')
            rerender = True
        
        elif not self.disabled and self.delete_text.text == self.disabled_phrase:
            self.delete_text.updateText(self.delete_phrase, color='black')
            rerender = True

        if rerender:
            pygame.draw.rect(self.text_surface, 'black', [0, 0, 230, 70], border_radius=10)
            pygame.draw.rect(self.text_surface, 'white', [3, 3, 224, 64], border_radius=8)
            self.delete_text.draw(self.text_surface)

        super().update(events, mouse_pos)