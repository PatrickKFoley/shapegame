from pygame.locals import *
import pygame.mouse
from pygame.sprite import Group
from pygame.mixer import Sound
from pygame.transform import smoothscale
from pygame.surface import Surface
from pygame.image import load
import pygame, random, math
from typing import Callable

from createdb import User, Shape as ShapeData, Notification, friends, GamePlayed
from ...screen_elements.text import Text
from ...screen_elements.editabletext import EditableText
from ...screen_elements.button import Button
from ...screen_elements.scrollbar import ScrollBar
from ...game.gamedata import color_data
from ..scrollablewindow import ScrollableWindow
from .friendsprite import FriendSprite
from sqlalchemy import func, delete, select, case
from sqlalchemy.orm import Session

class FriendsWindow(ScrollableWindow):
    def __init__(self, user: User, session: Session, addFriend: Callable, startNetwork: Callable):
        super().__init__(user, session, 'left')
        self.addFriend = addFriend
        self.startNetwork = startNetwork

        self.addAssets()
        self.initGroup()

    def addAssets(self):

        self.name_tags = []
        for i in range(4):
            self.name_tags.append(load(f'assets/backgrounds/hello_stickers/{i}.png'))
        self.name_tags.append(load('assets/paper/killfeed_larger.png').convert_alpha())
            
        self.frames_flag_raised = 0
        self.already_following_flag = False
        self.bad_credentials_flag = False
        self.thats_you_flag = False

        self.header = Text('followed players', 40, 250, 115)
        self.already_following = Text('already following!', 30, 250, 202)
        self.bad_credentials = Text('user not found!', 30, 250, 202)
        self.thats_you = Text('thats you, silly :3', 30, 250, 202)
        self.search_editable = EditableText('add player: ', 30, 250, 168)
        
        self.texts.append(self.header)
        self.editables.append(self.search_editable)

    def initGroup(self):

        for friend in reversed(self.user.friends):
            self.addFriendSprite(friend)

    def handleRaisedFlags(self):
        if not any([self.already_following_flag, self.thats_you_flag, self.bad_credentials_flag]): return
        
        self.frames_flag_raised += 1
        
        if self.frames_flag_raised == 180:
            self.frames_flag_raised = 0
            self.already_following_flag, self.bad_credentials_flag, self.thats_you_flag = False, False, False

    def handleInputs(self, mouse_pos, events):
        rel_mouse_pos = [mouse_pos[0] - self.x, mouse_pos[1] - self.y]
        
        super().handleInputs(mouse_pos, events)

        # handle events
        for event in events:
            if event.type == MOUSEBUTTONDOWN and event.button == 1:

                if self.search_editable.rect.collidepoint(rel_mouse_pos):
                    self.search_editable.select()
                else:
                    self.search_editable.deselect()

            elif event.type == KEYDOWN:
                if event.key == K_RETURN and (self.search_editable.selected or self.search_editable.hovered):
                    self.addFriend(self.search_editable.getText())

    def update(self, mouse_pos, events):
        '''update position of the collection window'''
        rel_mouse_pos = [mouse_pos[0] - self.x, mouse_pos[1] - self.y]

        # if the window is fully closed, idle
        if self.fully_closed:
            self.idle(rel_mouse_pos, events)
            return
        
        super().update(mouse_pos, events)
        self.handleRaisedFlags()
        
    def checkFriendsUpdate(self):
        '''check if a friend has been added'''

        if len(self.group) != len(self.user.friends):
            sprite_usernames = [sprite.shown_user.username for sprite in self.group.sprites()]

            for friend in self.user.friends: 
                if friend.username not in sprite_usernames:
                    self.addFriendSprite(friend)
                    break

    def addFriendSprite(self, friend: User):    

        self.addSprite(FriendSprite(
            self.user,
            friend,
            -1,
            self.session,
            self.name_tags,
            self.addFriend,
            self.startNetwork,
            len(self.group),
            True
        ))

    def renderSurface(self):
        super().renderSurface()

        if self.already_following_flag: self.surface.blit(self.already_following.surface, self.already_following.rect)
        if self.bad_credentials_flag: self.surface.blit(self.bad_credentials.surface, self.bad_credentials.rect)
        if self.thats_you_flag: self.surface.blit(self.thats_you.surface, self.thats_you.rect)