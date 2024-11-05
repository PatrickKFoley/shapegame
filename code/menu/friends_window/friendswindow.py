from pygame.locals import *
import pygame.mouse
from pygame.sprite import Group
from pygame.mixer import Sound
from pygame.transform import smoothscale
from pygame.surface import Surface
from pygame.image import load
import pygame, random, math

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
    def __init__(self, user: User, session: Session):
        super().__init__(user, session, 'left')

        self.addAssets()
        self.initGroup()

    def addAssets(self):

        self.name_tags = []
        for i in range(4):
            self.name_tags.append(load(f'assets/backgrounds/hello_stickers/{i}.png'))
            
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

        for friend in self.user.friends:
            sprite = FriendSprite(self.user, friend, len(self.group.sprites()), self.session, self.name_tags)
            self.addSprite(sprite)

    def addFriend(self):
        # try to add the user as a friend
        username = self.search_editable.getText()

        # lower flags
        self.already_friends_flag = False
        self.bad_credentials_flag = False
        self.thats_you_flag = False

        # query db for user
        try:
            searched_user = self.session.query(User).filter(User.username == username).one()
        except Exception as e:
            self.bad_credentials_flag = True
            print(f"Could not add friend, none found: {e}")
            return

        # raise flags
        self.already_friends_flag = any(friend.username == username for friend in self.user.friends)
        self.thats_you_flag = searched_user.username == self.user.username
        if self.already_friends_flag or self.thats_you_flag: return

        # create friend sprite
        sprite = FriendSprite(self.user, searched_user, -1, self.session, self.name_tags, len(self.group))
        sprites_copy = self.group.sprites()
        self.group.empty()
        self.group.add(sprite)
        self.group.add(sprites_copy)

        [sprite.moveDown() for sprite in self.group.sprites()]

        self.woosh_sound.play()

        self.next_y_min = min(-(450 + len(self.group.sprites()) * 175 - 1080), 0) 

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

        # add searched user to user following
        try:
            searched_user = self.session.query(User).filter(User.username == username).one()
            self.session.add(Notification(searched_user.id, searched_user, f'{self.user.username} now follows you', "FOLLOWER", self.user.username))
            self.user.friends.append(searched_user)
            self.session.commit()

        except Exception as e:
            self.session.rollback()
            print(f'Error creating notification: {e}')
            return

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
                    self.addFriend()

    def update(self, mouse_pos, events):
        '''update position of the collection window'''
        rel_mouse_pos = [mouse_pos[0] - self.x, mouse_pos[1] - self.y]

        # if the window is fully closed, idle
        if self.fully_closed:
            self.idle(rel_mouse_pos, events)
            return
        
        super().update(mouse_pos, events)
        self.handleRaisedFlags()
        

    def renderSurface(self):
        super().renderSurface()

        if self.already_following_flag: self.surface.blit(self.already_following.surface, self.already_following.rect)
        if self.bad_credentials_flag: self.surface.blit(self.bad_credentials.surface, self.bad_credentials.rect)
        if self.thats_you_flag: self.surface.blit(self.thats_you.surface, self.thats_you.rect)

        [self.surface.blit(sprite.info_surface, sprite.info_rect) for sprite in self.group.sprites() if sprite.info_hovered]