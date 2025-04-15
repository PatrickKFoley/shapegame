from ...screen_elements.holdbutton import HoldButton
from ...screen_elements.text import Text
from pygame.surface import Surface
from pygame.image import load
from pygame.transform import smoothscale
import pygame

class LvlUpButton(HoldButton):
    def __init__(self, center: list[int], fast_off = False):
        super().__init__('up', center, fast_off)

        self.cost = 0
        self.essence = 0

        # self.cost_surface = Surface((230, 70), pygame.SRCALPHA, 32).convert_alpha()
        self.level_text = Text('level up shape?', 30, 115, 20)
        self.cost_text = Text(f'{self.cost}', 30, 123, 37, align='topright')
        
        self.essence_icon = smoothscale(load('assets/icons/essence_icon.png'), [30, 30])
        self.essence_rect = self.essence_icon.get_rect()
        self.essence_rect.center = [145, 50]

        # self.updateCost(0, 0)

    
    def updateCost(self, cost: float, essence: float):
        self.cost = cost
        self.essence = essence

        if self.cost > self.essence:
            pygame.draw.rect(self.text_surface, 'black', [0, 0, 230, 70], border_radius=10)
            pygame.draw.rect(self.text_surface, 'white', [3, 3, 224, 64], border_radius=8)

            self.level_text.updateText('too expensive!', color='black')
            self.cost_text.updateText(f'{self.cost}', color='red')

            self.level_text.draw(self.text_surface)
            self.cost_text.draw(self.text_surface)
            self.text_surface.blit(self.essence_icon, self.essence_rect)

            self.disable()
            return

        self.level_text.updateText('level up shape?', color='black')
        self.cost_text.updateText(f'{self.cost}', color='black')

        pygame.draw.rect(self.text_surface, 'black', [0, 0, 230, 70], border_radius=10)
        pygame.draw.rect(self.text_surface, 'white', [3, 3, 224, 64], border_radius=8)

        self.level_text.draw(self.text_surface)
        self.cost_text.draw(self.text_surface)
        self.text_surface.blit(self.essence_icon, self.essence_rect)
        
        self.enable()

        # self.text_surface.set_alpha(self.text_alpha)

