from ...screen_elements.holdbutton import HoldButton
from ...screen_elements.text import Text
from typing import Callable
import pygame

class DeleteButton(HoldButton):
    def __init__(self, center: list[int], callback: Callable, fast_off = False):
        super().__init__('trash', center, callback, fast_off)

        self.delete_phrase = ['delete shape?', '(irreversible)']
        self.disabled_phrase = ['not able to', 'delete shape!']

        self.delete_text = Text(self.delete_phrase, 30, 115, 20)
        self.delete_text.draw(self.text_surface)

    def update(self, events, mouse_pos):
        '''renrender the info surface if the button is freshly disabled or enabled'''
        
        rerender = False
        if self.disabled and self.delete_text.text == self.delete_phrase:

            # text indicates button is enabled, is now disabled
            self.delete_text.updateText(self.disabled_phrase, color='red')
            rerender = True
        
        elif not self.disabled and self.delete_text.text == self.disabled_phrase:

            # text indicates button is disabled, is now enabled
            self.delete_text.updateText(self.delete_phrase, color='black')
            rerender = True

        # rerender the info surface if needed
        if rerender:
            pygame.draw.rect(self.text_surface, 'black', [0, 0, 230, 70], border_radius=10)
            pygame.draw.rect(self.text_surface, 'white', [3, 3, 224, 64], border_radius=8)
            self.delete_text.draw(self.text_surface)

        super().update(events, mouse_pos)