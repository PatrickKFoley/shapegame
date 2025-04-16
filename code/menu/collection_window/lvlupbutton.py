from ...screen_elements.holdbutton import HoldButton
from ...screen_elements.text import Text
from pygame.image import load
from pygame.transform import smoothscale
import pygame
from typing import Callable

class  LvlUpButton(HoldButton):
    def __init__(self, center: list[int], callback: Callable, fast_off = False):
        super().__init__('up', center, callback, fast_off)

        self.cost = 0       # cost of the next level for the currently selected shape
        self.essence = 0    # essence amount of the logged in user

        # text elements for info surface
        self.level_text = Text('level up shape?', 30, 115, 20)
        self.cost_text = Text(f'{self.cost}', 30, 123, 37, align='topright')
        
        # essence icon for cost unit
        self.essence_icon = smoothscale(load('assets/icons/essence_icon.png'), [30, 30])
        self.essence_rect = self.essence_icon.get_rect()
        self.essence_rect.center = [145, 50]
    
    def updateCost(self, cost: float, essence: float):
        '''update the info surface with the new cost '''

        self.cost = cost
        self.essence = essence

        # if cost is too high, update info surface with warning
        if self.cost > self.essence:

            pygame.draw.rect(self.text_surface, 'black', [0, 0, 230, 70], border_radius=10)
            pygame.draw.rect(self.text_surface, 'white', [3, 3, 224, 64], border_radius=8)

            self.level_text.updateText('too expensive!', color='black')
            self.cost_text.updateText(f'{self.cost}', color='red')

            self.level_text.draw(self.text_surface)
            self.cost_text.draw(self.text_surface)
            self.text_surface.blit(self.essence_icon, self.essence_rect)

            self.disable() # don't allow the user to activate the button
            return

        # else, update info surface with normal text
        pygame.draw.rect(self.text_surface, 'black', [0, 0, 230, 70], border_radius=10)
        pygame.draw.rect(self.text_surface, 'white', [3, 3, 224, 64], border_radius=8)

        self.level_text.updateText('level up shape?', color='black')
        self.cost_text.updateText(f'{self.cost}', color='black')

        self.level_text.draw(self.text_surface)
        self.cost_text.draw(self.text_surface)
        self.text_surface.blit(self.essence_icon, self.essence_rect)
        
        self.enable() # allow the user to activate the button