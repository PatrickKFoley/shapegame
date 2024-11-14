import pygame
from createdb import User
from pygame.surface import Surface
from .text import Text
from .togglebutton import ToggleButton
from ..game.gamedata import color_data

class NetworkNameplate:
    def __init__(self, user: User):
        self.user = user
        
        self.w = 1020
        self.h = 60
        self.alpha = 0
        self.on = False
        self.button_hovered = False

        self.surface = Surface([self.w, self.h], pygame.SRCALPHA, 32)
        self.background = Surface([self.w, self.h], pygame.SRCALPHA, 32)
        self.rect = self.surface.get_rect()
        self.rect.center = [1370, 100]
        
        pygame.draw.rect(self.background, 'black', [0, 0, self.w, self.h], border_radius=10)
        pygame.draw.rect(self.background, 'white', [3, 3, self.w-6, self.h-6], border_radius=10)

        color = None
        for shape_data in self.user.shapes:
            if shape_data.id == self.user.favorite_id:
                color = color_data[shape_data.color_id].text_color
                break
        
        self.locked = ToggleButton('radio', 35, [490, self.h/2])
        self.keeps = ToggleButton('radio', 35, [775, self.h/2])
        self.ready = ToggleButton('radio', 35, [950, self.h/2])

        self.buttons = [
            self.locked,
            self.keeps,
            self.ready,
        ]

        self.elements = [
            self.locked,
            self.keeps,
            self.ready,
            Text(f'{self.user.username}', 60, 50, 0, 'topleft', color, 200, 'black'), 
            Text('confirm selection', 30, 350, 30),
            Text('play for keeps', 30, 650, 30),
            Text('ready', 30, 880, 30),
        ]

        self.renderSurface()

    def renderSurface(self):
        self.surface.fill((0, 0, 0, 0))
        
        self.surface.blit(self.background, [0, 0])
        [element.draw(self.surface) for element in self.elements]

        self.surface.set_alpha(self.alpha)

    def update(self, mouse_pos = None, events = None):

        if self.on and self.alpha < 255:
            self.alpha = min(self.alpha + 10, 255)
            self.surface.set_alpha(self.alpha)
        elif not self.on and self.alpha > 0:
            self.alpha = max(self.alpha - 15, 0)
            self.surface.set_alpha(self.alpha)
        
        if not self.on or mouse_pos == None: return

        rel_mouse_pos = [mouse_pos[0] - self.rect.x, mouse_pos[1] - self.rect.y]

        # [button.update(rel_mouse_pos, events) for button in self.buttons]
        self.locked.update(rel_mouse_pos, events)
        self.keeps.update(rel_mouse_pos, events)
        if self.locked.selected: self.ready.update(rel_mouse_pos, events)

        if any(button.rect.collidepoint(rel_mouse_pos) for button in self.buttons): 
            self.renderSurface()
            self.button_hovered = True
        elif self.button_hovered:
            self.button_hovered = False
            self.renderSurface()
        

    def draw(self, surface):
        surface.blit(self.surface, self.rect)

    def turnOn(self):
        self.on = True

    def turnOff(self):
        self.on = False

