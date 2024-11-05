from pygame.locals import *
import pygame.mouse
from pygame.sprite import Group
from pygame.mixer import Sound
from pygame.transform import smoothscale
from pygame.surface import Surface
from pygame.image import load
import pygame, random, math

WIN_HEIGHT = 1080
WIDTH = 18
HEIGHT = 250
F_WIDTH = 14
Y_TOP = 1080 - 10 - HEIGHT

CLOSED_X_L = 450
OPENED_X_L = 525
CLOSED_X_R = 525
OPENED_X_R = 450

class ScrollBar:
    def __init__(self, hooks, direction = 'left'):
        
        self.window_x = hooks['x']
        self.window_next_x = hooks['next_x']
        self.window_y = hooks['y']
        self.y_min = hooks['y_min']
        self.next_y_min = hooks['next_y_min']

        self.opened_x = OPENED_X_L if direction == 'left' else OPENED_X_R
        self.closed_x = CLOSED_X_L if direction == 'left' else CLOSED_X_R
        self.x = self.closed_x
        self.next_x = self.x
        self.disabled = self.y_min == 0
        self.alpha = 0

        # create background surface
        self.surface = Surface((WIDTH, HEIGHT), pygame.SRCALPHA, 32)
        self.rect = self.surface.get_rect()
        self.rect.topleft = self.x - WIDTH/2, Y_TOP - self.window_y
        pygame.draw.rect(self.surface, (0, 0, 0, 150), [0, 0, self.rect.w, self.rect.h], border_radius=10)

        # manually trigger front surface creation
        self.updateLength(-1)

    def draw(self, surface: Surface):

        surface.blit(self.surface, self.rect)
        surface.blit(self.front_surface, self.front_rect)

    def updatePosition(self, prev_window_y):

        # toggle scrollbar position if window moved
        if self.window_x != self.window_next_x:
            if self.window_next_x < 0: self.next_x = self.closed_x
            else: self.next_x = self.opened_x

        # move horizontally if needed
        if self.x != self.next_x:
            if self.x < self.next_x: self.x = min(self.x + 5, self.next_x)
            else: self.x = max(self.x - 2, self.next_x)

        # handle scrolling window
        if self.window_y != prev_window_y:
            percent_above = ((self.window_y * -1) / ((self.y_min * -1) + 1080))
            self.front_y = min(max(int((percent_above * (HEIGHT))-5), 5), HEIGHT+10-self.front_h)

    def updateLength(self, prev_y_min):
        if self.y_min == prev_y_min: return

        # turn scrollbar off if window can't scroll
        self.disabled = self.y_min == 0
        
        # determine length and position of white bar
        self.front_h = min(int((1080 / ((self.y_min * -1) + 1080)) * HEIGHT), HEIGHT-10)
        percent_above = ((self.window_y * -1) / ((self.y_min * -1) + 1080))
        self.front_y = min(max(int((percent_above * (HEIGHT))-5), 5), HEIGHT+10-self.front_h)
        
        # recreate from bar surface
        self.front_surface = Surface((F_WIDTH, self.front_h), pygame.SRCALPHA, 32)
        self.front_rect = self.front_surface.get_rect()
        self.front_rect.topleft = self.x - F_WIDTH/2, Y_TOP - self.window_y + self.front_y
        pygame.draw.rect(self.front_surface, (255, 255, 255, 200), [0, 0, self.front_rect.w, self.front_rect.h], border_radius=10)

    def updateTransparency(self):

        # fade surface in and out
        if not self.disabled and self.alpha <= 255:
            self.alpha = min(self.alpha + 10, 255)
            self.surface.set_alpha(self.alpha)
            self.front_surface.set_alpha(self.alpha)

        elif self.disabled and self.alpha >= 0:
            self.alpha = max(self.alpha - 10, 0)
            self.surface.set_alpha(self.alpha)
            self.front_surface.set_alpha(self.alpha)

    def update(self, hooks):
        prev_y_min = self.y_min
        prev_window_y = self.window_y

        self.window_x = hooks['x']
        self.window_next_x = hooks['next_x']
        self.window_y = hooks['y']
        self.y_min = hooks['y_min']
        self.next_y_min = hooks['next_y_min']

        self.updatePosition(prev_window_y)
        self.updateLength(prev_y_min)
        self.updateTransparency()

        self.rect.topleft = self.x - WIDTH/2, Y_TOP - self.window_y
        self.front_rect.topleft = self.x - F_WIDTH/2, Y_TOP - self.window_y + self.front_y
    


