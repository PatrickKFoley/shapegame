from pygame.locals import *
import pygame.mouse
from pygame.sprite import Group
from pygame.mixer import Sound
import pygame.sprite
from pygame.transform import smoothscale
from pygame.surface import Surface
from pygame.image import load
from typing import Union
import pygame, random, math, itertools
from typing import Callable

from code.screen_elements.screenelement import ScreenElement
from createdb import User, Shape as ShapeData, Notification, friends, GamePlayed
from ..screen_elements.text import Text
from ..screen_elements.editabletext import EditableText
from ..screen_elements.button import Button
from ..screen_elements.scrollbar import ScrollBar
from ..game.gamedata import color_data
from .friends_window.friendsprite import FriendSprite
from .notifications_window.notificationsprite import NotificationSprite
from sqlalchemy import func, delete, select, case
from sqlalchemy.orm import Session, exc
from sharedfunctions import clearSurfaceBeneath

class ScrollableWindow:
    def __init__(self, user: User, session: Session, side = 'left'):
        self.user = user
        self.session = session
        self.side = side

        self.closed_x = -500 if self.side == 'left' else 1920 - 50
        self.opened_x = 0 if self.side == 'left' else 1920 - 550
        self.x = self.closed_x
        self.next_x = self.x
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
        
        self.current_opp_id = -1
        
        self.initAssets()
        self.initSurface()

    def initAssets(self):
        self.notebook_color = 'green' if self.side == 'left' else 'blue'
        self.icon_name = 'friends' if self.side == 'left' else 'mail'

        self.background = load(f'assets/backgrounds/{self.notebook_color}_notebook.png').convert_alpha()
        self.background_extension = load(f'assets/backgrounds/{self.notebook_color}_notebook_extension.png').convert_alpha()
        self.background_rect = self.background.get_rect()
        self.background_rect.topleft = [0, 0]

        self.woosh_sound = Sound('assets/sounds/woosh.wav')

        self.button = Button(self.icon_name, 45, [25, 25] if self.side == 'right' else [525, 25], fast_off=True)
        self.screen_elements: list[ScreenElement] = [
            self.button
        ]

        self.group = Group()
        self.dead_group = Group()
        
        self.sprite_count_text = None
        '''text to display the number of sprites in the window
            currently only used for notifications window
        '''

    def initSurface(self):
        self.surface_l = 2160
        self.len_x = 1
        if self.y_min <= -1080:
            self.len_x += self.y_min // -1080

        self.surface = Surface([550, self.surface_l * self.len_x], pygame.SRCALPHA, 32)
        self.rect = self.surface.get_rect()
        self.rect.topleft = [self.x, 0]

        scrollbar_hooks = {key: getattr(self, key) for key in ['x', 'next_x', 'y', 'y_min', 'next_y_min']}
        self.scrollbar = ScrollBar(scrollbar_hooks, self.side)

    def draw(self, surface):
        surface.blit(self.surface, self.rect)

    def addSprite(self, sprite: Union[FriendSprite, NotificationSprite], play_sound = True):
        
        # if type(sprite) == FriendSprite:
        sprites_copy = self.group.sprites()
        self.group.empty()
        self.group.add(sprite)
        self.group.add(sprites_copy)
        # else:
        self.group.add(sprite)
        

        # check if the surface needs to be extended
        len_x = 1
        if self.next_y_min <= -1080:
            len_x += self.next_y_min // -1080

        if len_x != self.len_x:
            self.len_x = len_x
            cur_pos = self.rect.topleft
            
            self.surface = Surface([550, 2160 * self.len_x], pygame.SRCALPHA, 32)
            self.rect = self.surface.get_rect()
            self.rect.topleft = cur_pos
            
        self.y_min = min(-(450 + len(self.group.sprites()) * 175 - 1080), 0)
        self.next_y_min = self.y_min

        if sprite.new:
            [sprite.moveDown() for sprite in self.group.sprites()]
            
        if play_sound:    
            self.woosh_sound.play()

    def removeSprite(self, sprite: Union[FriendSprite, NotificationSprite]):

        self.group.remove(sprite)
        self.dead_group.add(sprite)

        self.woosh_sound.play()
        self.next_y_min = min(-(650 + (len(self.group.sprites())-1) * 175 - 1080), 0)
        
        if type(sprite) == FriendSprite:

            try:
                self.session.execute(delete(friends).where((friends.c.user_id == self.user.id) & (friends.c.friend_id == sprite.friend.id)))
                self.session.commit()
            except Exception as e:
                self.session.rollback()
                print(f'error deleting friend: {e}')
            
        if type(sprite) == NotificationSprite:

            try:
                self.session.execute(delete(Notification).where((Notification.id == sprite.notification.id)))
                self.session.commit()
            except Exception as e:
                self.session.rollback()

                # ignore object deleted errors, happens when notification is replaced by a new identical one
                if type(e) != exc.ObjectDeletedError:
                    print(f'error deleting notification: {e}')

    def updateScrollBar(self):
        scrollbar_hooks = {key: getattr(self, key) for key in ['x', 'next_x', 'y', 'y_min', 'next_y_min']}
        self.scrollbar.update(scrollbar_hooks)

    def toggle(self):
        self.opened = not self.opened

        if self.opened: 
            self.fully_closed = False
            self.next_x = self.opened_x
        else: self.next_x = self.closed_x

    def idle(self, mouse_pos, events):
    
        ''' replaces update() when window is fully closed
            only accepts inputs to and draws toggle button
        '''
        
        if self.sprite_count_text != None and self.sprite_count_text.text != '0':
            
            self.button.update(events, mouse_pos)
            self.sprite_count_text.update(events, mouse_pos)
            
            clearSurfaceBeneath(self.surface, self.button.rect)
            clearSurfaceBeneath(self.surface, self.sprite_count_text.rect)
            
            self.button.draw(self.surface)
            self.sprite_count_text.draw(self.surface)
            
        else:
            self.button.update(events, mouse_pos)
            clearSurfaceBeneath(self.surface, self.button.rect)
            self.button.draw(self.surface)

        for event in events: 
            
            if event.type == MOUSEBUTTONDOWN and event.button == 1 and self.button.rect.collidepoint(mouse_pos) and not self.button.disabled:
                self.toggle()

    def close(self):
        self.opened = False
        self.next_x = self.closed_x

    def updateGroup(self, rel_mouse_pos, events):

        self.dead_group.update(rel_mouse_pos, events)

        sprite_died = False
        for sprite in self.group.sprites():
            if sprite_died: 
                sprite.moveUp()

            if sprite.update(rel_mouse_pos, events): 
                sprite_died = True

                self.removeSprite(sprite)

    def handleInputs(self, mouse_pos, events):
        rel_mouse_pos = [mouse_pos[0] - self.x, mouse_pos[1] - self.y]
        
        # handle events
        for event in events:
            if event.type == MOUSEBUTTONDOWN: 

                if self.button.isHovAndEnabled(rel_mouse_pos):
                    self.toggle()

                if self.rect.collidepoint(mouse_pos):
                    self.is_held = True
                    self.y_on_click = int(self.y)
                    self.mouse_y_on_click = mouse_pos[1]

            elif event.type == MOUSEBUTTONUP:
                if self.rect.collidepoint(mouse_pos):
                    self.is_held = False

    def update(self, mouse_pos, events):
        '''update position of the collection window'''
        rel_mouse_pos = [mouse_pos[0] - self.x, mouse_pos[1] - self.y]

        clearSurfaceBeneath(self.surface, self.button.rect)

        # if the window is fully closed, idle
        if self.fully_closed:
            self.idle(rel_mouse_pos, events)
            return
        
        self.handleInputs(mouse_pos, events)
        
        self.updateGroup(rel_mouse_pos, events)
        self.updateScrollBar()
        # [editable.update(events, rel_mouse_pos) for editable in self.editables]
        # [clickable.update(events, rel_mouse_pos) for clickable in self.clickables]
        [element.update(events, rel_mouse_pos) for element in self.screen_elements if element != None]


        # inputs
        # raised flags

        self.positionWindow(mouse_pos)
        self.renderSurface()

    def positionWindow(self, mouse_pos):
        # update window positions
        if self.y_min != self.next_y_min:

            if self.y_min < self.next_y_min:
                self.y_min = min(self.y_min + 20, self.next_y_min)

            else: self.y_min = max(self.y_min - 20, self.next_y_min)

        if self.y < self.y_min:
            self.y = min(self.y + 20, self.next_y_min)
            self.rect.topleft = [self.x, self.y]

            self.updateScrollBar()
            self.button.rect.center = [self.button.x, self.button.y - self.y]

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

            self.rect.topleft = [self.x, self.y]

            # determine closed status
            if self.x == self.closed_x:
                self.fully_closed = True

        if self.is_held:
            self.y = max(self.y_min, min(mouse_pos[1] - self.mouse_y_on_click + self.y_on_click, 0))
            
            self.updateScrollBar()
            self.button.rect.center = [self.button.x, self.button.y - self.y]

            self.rect.topleft = [self.x, self.y]
    
    def renderSurface(self):
        self.surface.fill((0, 0, 0, 0))
        self.scrollbar.draw(self.surface)
        self.surface.blit(self.background, [50, 0] if self.side == 'right' else [0, 0])

        # if the surface is longer than 1 image, repeat it
        if self.len_x > 1:
            for i in range(1, self.len_x):
                self.surface.blit(self.background_extension, [0 if self.side == 'left' else 50, self.surface_l * (i)])

        # [clickable.draw(self.surface) for clickable in self.clickables]
        # [editable.draw(self.surface) for editable in self.editables]
        # [text.draw(self.surface) for text in self.texts]
        [screen_element.draw(self.surface) for screen_element in self.screen_elements if screen_element != None]
        
        # self.group.draw(self.surface)
        # self.dead_group.draw(self.surface)
        [sprite.draw(self.surface) for sprite in itertools.chain(self.group.sprites(), self.dead_group.sprites())]
        

        [self.surface.blit(sprite.info_surface, sprite.info_rect) for sprite in self.group.sprites() if sprite.info_hovered]

    def isButtonHovered(self, mouse_pos):
        rel_mouse_pos = [mouse_pos[0] - self.x, mouse_pos[1] - self.y]

        return self.button.rect.collidepoint(rel_mouse_pos)