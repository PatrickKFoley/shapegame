from pygame.locals import *
import pygame.mouse
from pygame.sprite import Group
from pygame.mixer import Sound
from pygame.transform import smoothscale
from pygame.surface import Surface
from pygame.image import load
import pygame

from createdb import User
from ..screen_elements.button import Button
from sqlalchemy import create_engine, func, delete, select, case
from sqlalchemy.orm import Session

class NotificationsWindow:
    def __init__(self, user: User, session: Session):
        self.user = user
        self.session = session

        self.x = 1920 - 50
        self.next_x = 1920 - 50
        self.v = 0
        self.a = 1.5
        self.opened = False
        self.fully_closed = True

        self.y = 0
        self.y_min = self.y
        self.next_y_min = self.y_min
        self.y_on_click = 0
        self.mouse_y_on_click = 0
        self.is_held = False

        self.initAssets()
        # self.initGroup()
        self.initSurface()

    def initAssets(self):
        self.background = load('assets/backgrounds/green_notebook.png').convert_alpha()
        self.background_rect = self.background.get_rect()
        self.background_rect.topleft = [0, 0]

        self.woosh_sound = Sound('assets/sounds/woosh.wav')

    def initSurface(self):
        self.surface = Surface([550, 2160], pygame.SRCALPHA, 32)
        self.rect = self.surface.get_rect()
        self.rect.topleft = [1920-50, 0]

        self.button = Button('mail', 45, [25, 25])

        self.clickables = [
            self.button,
        ]

    def updateScreenElements(self, rel_mouse_pos, events):
        for clickable in self.clickables:
            clickable.update(rel_mouse_pos)

    def handleInputs(self, mouse_pos, events):
        rel_mouse_pos = [mouse_pos[0] - self.x, mouse_pos[1] - self.y]

        # handle events
        for event in events:
            if event.type == MOUSEBUTTONDOWN: 

                if self.button.rect.collidepoint(rel_mouse_pos):
                    self.toggle()

                if self.rect.collidepoint(mouse_pos):
                    self.is_held = True
                    self.y_on_click = int(self.y)
                    self.mouse_y_on_click = mouse_pos[1]

            elif event.type == MOUSEBUTTONUP:
                if self.rect.collidepoint(mouse_pos):
                    self.is_held = False

    def toggle(self):
        self.opened = not self.opened

        if self.opened: 
            self.fully_closed = False
            self.next_x = 1920 - 550
        else: self.next_x = 1920 - 50

    def idle(self, mouse_pos, events):
        ''' replaces update() when window is fully closed
            only accepts inputs to and draws toggle button
        '''

        self.button.update(mouse_pos)
        self.surface.blit(self.button.surface, self.button.rect)

        for event in events: 
            if event.type == MOUSEBUTTONDOWN and event.button == 1 and self.button.rect.collidepoint(mouse_pos):
                self.toggle()


    def update(self, mouse_pos, events):
        '''update position of the collection window'''
        rel_mouse_pos = [mouse_pos[0] - self.x, mouse_pos[1] - self.y]

        # if the window is fully closed, idle
        if self.fully_closed:
            self.idle(rel_mouse_pos, events)
            return

        
        self.updateScreenElements(rel_mouse_pos, events)

        self.handleInputs(mouse_pos, events)

        # self.handleRaisedFlags()

        self.positionWindow(mouse_pos)

        self.renderSurface()

    def positionWindow(self, mouse_pos):
        # update window positions
        if self.y_min != self.next_y_min:

            if self.y_min < self.next_y_min:
                self.y_min = min(self.y_min + 20, self.next_y_min)

            else: self.y_min = self.next_y_min

        if self.y < self.y_min:
            self.y = min(self.y + 20, self.next_y_min)
            self.rect.topleft = [self.x, self.y]

        if self.x != self.next_x:
        
            # calculate the remaining distance to the target
            distance = abs(self.x - self.next_x)

            # apply acceleration while far from the target, decelerate when close
            if distance > 50:
                self.v += self.a
            else:
                self.v = max(1, distance * 0.2)

            # move the window towards the target position, snap in place if position is exceeded
            if self.x > self.next_x:

                self.x = max(self.x - self.v, self.next_x)

            elif self.x < self.next_x:

                self.x = min(self.x + self.v, self.next_x)

            # reset the velocity when the window reaches its target
            if self.x == self.next_x:
                self.v = 0

        if self.is_held:
            self.y = max(self.y_min, min(mouse_pos[1] - self.mouse_y_on_click + self.y_on_click, 0))
            self.button.rect.center = [self.button.x, self.button.y - self.y]

        self.rect.topleft = [self.x, self.y]

    def renderSurface(self):
        self.surface.fill((0, 0, 0, 0))
        self.surface.blit(self.background, [50, 0])

        [self.surface.blit(clickable.surface, clickable.rect) for clickable in self.clickables]

