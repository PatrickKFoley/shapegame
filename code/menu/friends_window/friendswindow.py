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
from .friendsprite import FriendSprite
from sqlalchemy import func, delete, select, case
from sqlalchemy.orm import Session

class FriendsWindow:
    def __init__(self, user: User, session: Session):
        self.user = user
        self.session = session

        self.x = -500
        self.next_x = -500
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
        self.initGroup()
        self.initSurface()

    def initAssets(self):

        self.name_tags = []
        for i in range(4):
            self.name_tags.append(load(f'assets/backgrounds/hello_stickers/{i}.png'))

        self.background = load('assets/backgrounds/green_notebook.png').convert_alpha()
        self.background_extension = load('assets/backgrounds/green_notebook_extension.png').convert_alpha()

        self.background_rect = self.background.get_rect()
        self.background_rect.topleft = [0, 0]

        self.woosh_sound = Sound('assets/sounds/woosh.wav')

    def initGroup(self):
        self.friends_group = Group()
    
        for friend in self.user.friends:
            self.friends_group.add(FriendSprite(self.user, friend, len(self.friends_group.sprites()), self.session, self.name_tags))

        self.y_min = min(-(450 + len(self.friends_group.sprites()) * 175 - 1080), 0)
        self.next_y_min = self.y_min

    def initSurface(self):

        self.surface_l = 2160
        self.len_x = 1
        if self.y_min <= -1080:
            self.len_x += self.y_min // -1080

        self.surface = Surface([550, self.surface_l * self.len_x], pygame.SRCALPHA, 32)
        self.rect = self.surface.get_rect()
        self.rect.topleft = [-500, 0]

        self.frames_flag_raised = 0
        self.already_following_flag = False
        self.bad_credentials_flag = False
        self.thats_you_flag = False

        self.header = Text('followed players', 40, 250, 115)
        self.already_following = Text('already following!', 30, 250, 202)
        self.bad_credentials = Text('user not found!', 30, 250, 202)
        self.thats_you = Text('thats you, silly :3', 30, 250, 202)
        self.search_editable = EditableText('add player: ', 30, 250, 168)

        self.texts = [
            self.header
        ]

        self.button = Button('friends', 45, [525, 25])
        self.clickables = [
            self.button,
        ]

        scrollbar_hooks = {key: getattr(self, key) for key in ['x', 'next_x', 'y', 'y_min', 'next_y_min']}
        self.scrollbar = ScrollBar(scrollbar_hooks)

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
        sprite = FriendSprite(self.user, searched_user, -1, self.session, self.name_tags, len(self.friends_group))
        sprites_copy = self.friends_group.sprites()
        self.friends_group.empty()
        self.friends_group.add(sprite)
        self.friends_group.add(sprites_copy)

        [sprite.moveDown() for sprite in self.friends_group.sprites()]

        self.woosh_sound.play()

        self.next_y_min = min(-(450 + len(self.friends_group.sprites()) * 175 - 1080), 0) 

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

    def removeFriend(self, sprite: FriendSprite):
        self.woosh_sound.play()
        self.next_y_min = min(-(450 + (len(self.friends_group.sprites())-1) * 175 - 1080), 0) 
        
        self.session.execute(delete(friends).where((friends.c.user_id == self.user.id) & (friends.c.friend_id == sprite.friend.id)))
        self.session.commit()

    def updateScreenElements(self, rel_mouse_pos, events):

        # update sprite group
        sprite_died = False
        for sprite in self.friends_group.sprites():
            if sprite_died: sprite.moveUp()

            if sprite.update(rel_mouse_pos, events): 
                sprite_died = True

                self.removeFriend(sprite)

        self.button.update(rel_mouse_pos)
        self.search_editable.update(events)
        self.search_editable.hovered = self.search_editable.rect.collidepoint(rel_mouse_pos)

        self.updateScrollBar()

    def updateScrollBar(self):
        scrollbar_hooks = {key: getattr(self, key) for key in ['x', 'next_x', 'y', 'y_min', 'next_y_min']}
        self.scrollbar.update(scrollbar_hooks)

    def handleRaisedFlags(self):
        if not any([self.already_following_flag, self.thats_you_flag, self.bad_credentials_flag]): return
        
        self.frames_flag_raised += 1
        
        if self.frames_flag_raised == 180:
            self.frames_flag_raised = 0
            self.already_following_flag, self.bad_credentials_flag, self.thats_you_flag = False, False, False

    def handleInputs(self, mouse_pos, events):
        rel_mouse_pos = [mouse_pos[0] - self.x, mouse_pos[1] - self.y]

        # handle events
        for event in events:
            if event.type == MOUSEBUTTONDOWN and event.button == 1:

                if self.button.rect.collidepoint(rel_mouse_pos):
                    self.toggle()

                if self.rect.collidepoint(mouse_pos):
                    self.is_held = True
                    self.y_on_click = int(self.y)
                    self.mouse_y_on_click = mouse_pos[1]

                if self.search_editable.rect.collidepoint(rel_mouse_pos):
                    self.search_editable.select()
                else:
                    self.search_editable.deselect()

            elif event.type == MOUSEBUTTONUP:
                if self.rect.collidepoint(mouse_pos):
                    self.is_held = False

            elif event.type == KEYDOWN:
                if event.key == K_RETURN and (self.search_editable.selected or self.search_editable.hovered):
                    self.addFriend()

    def toggle(self):
        self.opened = not self.opened

        if self.opened:
            self.fully_closed = False
            self.next_x = 0
        else: self.next_x = -500

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

        self.handleRaisedFlags()

        self.handleInputs(mouse_pos, events)
        
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
            if self.x == -500:
                self.fully_closed = True

        if self.is_held:
            self.y = max(self.y_min, min(mouse_pos[1] - self.mouse_y_on_click + self.y_on_click, 0))
            scrollbar_hooks = {key: getattr(self, key) for key in ['x', 'next_x', 'y', 'y_min', 'next_y_min']}
            self.scrollbar.update(scrollbar_hooks)
            self.button.rect.center = [self.button.x, self.button.y - self.y]

            self.rect.topleft = [self.x, self.y]

    def renderSurface(self):
        self.surface.fill((0, 0, 0, 0))
        self.scrollbar.draw(self.surface)
        self.surface.blit(self.background, [0, 0])

        # if the surface is longer than 1 image, repeat it
        if self.len_x > 1:
            for i in range(1, self.len_x):
                self.surface.blit(self.background_extension, [0, self.surface_l * (i)])

        [self.surface.blit(clickable.surface, clickable.rect) for clickable in self.clickables]
        [self.surface.blit(text.surface, text.rect) for text in self.texts]

        self.surface.blit(self.search_editable.surface, self.search_editable.rect)

        if self.already_following_flag: self.surface.blit(self.already_following.surface, self.already_following.rect)
        if self.bad_credentials_flag: self.surface.blit(self.bad_credentials.surface, self.bad_credentials.rect)
        if self.thats_you_flag: self.surface.blit(self.thats_you.surface, self.thats_you.rect)

        self.friends_group.draw(self.surface)
        [self.surface.blit(sprite.info_surface, sprite.info_rect) for sprite in self.friends_group.sprites() if sprite.info_hovered]

    def isButtonHovered(self, mouse_pos):
        rel_mouse_pos = [mouse_pos[0] - self.x, mouse_pos[1] - self.y]

        return self.button.rect.collidepoint(rel_mouse_pos)