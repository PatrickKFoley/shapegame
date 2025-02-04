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
from ...game.gamedata import color_data
from ..windowsprite import WindowSprite
from sqlalchemy import func, delete, select, case
from sqlalchemy.orm import Session

class FriendSprite(WindowSprite):

    def __init__(self, user: User, friend: User, position: int, session: Session, backgrounds: list[Surface], addFriend: Callable, startNetwork: Callable, current_length = None, new = False):
        self.side = 'left'
        super().__init__(user, friend, session, position, backgrounds, current_length, self.side, new)

        self.user = user
        self.friend = friend
        self.position = position
        self.session = session
        self.backgrounds = backgrounds
        self.addFriend = addFriend
        self.startNetwork = startNetwork
        self.current_length = current_length

        self.addAssets()
        self.initSurface()

    def addAssets(self):
        self.challenge_button = Button('swords', 35, [150, 125])
        self.buttons.append(self.challenge_button)

    def initSurface(self):
        self.image.blit(self.background, [0, 0])
        self.image.blit(self.username_text.surface, self.username_text.rect)
        self.image.blit(self.shape_image, [20, 46])
        self.image.blit(self.face_image, [20, 46])

        [button.draw(self.image) for button in self.buttons]

    # UPDATE STATE

    def handleInputs(self, mouse_pos, events):
        rel_mouse_pos = [mouse_pos[0] - self.x + self.width/2, mouse_pos[1] - self.y + self.height/2]

        [button.update(events, rel_mouse_pos) for button in self.buttons]
        
        # check hover
        if any(button.rect.collidepoint(rel_mouse_pos) for button in self.buttons) and not self.rerender_icons:
            self.rerender_icons = True
        elif self.rerender_icons: self.rerender_icons = False
        else:
            self.rerender_icons = True

        # check info hover
        if self.info_button.rect.collidepoint(rel_mouse_pos):
            self.info_hovered = True
            self.info_alpha = min(self.info_alpha + 15, 255)
            self.info_surface.set_alpha(self.info_alpha)
        elif self.info_alpha > 0:
            self.info_alpha = max(self.info_alpha - 15, 0)
            self.info_surface.set_alpha(self.info_alpha)
        else: 
            self.info_hovered = False
        
        for event in events:
            if event.type == MOUSEBUTTONDOWN:
                if self.challenge_button.rect.collidepoint(rel_mouse_pos):
                    self.startNetwork(self.friend, True)
                
                elif self.delete_button.rect.collidepoint(rel_mouse_pos):
                    self.next_x -= 1000

    def update(self, mouse_pos, events):

        self.handleInputs(mouse_pos, events)

        return super().update()
    