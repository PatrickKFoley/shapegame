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

class NotificationSprite(WindowSprite):

    # INIT

    def __init__(self, user: User, notification: Notification, position: int, session: Session, backgrounds: list[Surface], addFriend: Callable, startNetwork: Callable, current_length = None, new = False, shimmer_images: list[Surface] = None):
        self.side = 'right'
        super().__init__(user, notification.sender, session, position, backgrounds, current_length, self.side, new)

        self.user = user
        self.notification = notification
        self.position = position
        self.session = session
        self.backgrounds = backgrounds
        self.addFriend = addFriend
        self.startNetwork = startNetwork
        self.current_length = current_length
        self.shimmer_images = shimmer_images
        self.addAssets()
        self.initSurface()
        
        self.shimmer_index = 0
        self.shimmering = self.notification.new
        self.next_shimmer_frame = random.randint(10, 30)
        self.frames = 0
        self.shimmer_surface = None if not self.shimmering else self.shimmer_images[self.shimmer_index]
        
        

    def addAssets(self):
        blurb = 'followed you!' if self.notification.type == 'FRIEND' else ('wants to fight!' if self.notification.type == 'CHALLENGE' else 'followed you back!')
        icon = 'add_friend' if self.notification.type == 'FRIEND' else 'swords'
        self.blurb = Text(blurb, 25, 140, 90, 'topleft')
        self.accept_button = Button(icon, 35, [225, 125])
        self.buttons.append(self.accept_button)

    def initSurface(self):
        self.image.fill((0, 0, 0, 0))
        
        self.image.blit(self.background, [0, 0])
        self.image.blit(self.username_text.surface, self.username_text.rect)
        self.blurb.draw(self.image)
        self.image.blit(self.shape_image, [20, 46])
        self.image.blit(self.face_image, [20, 46])
        
        self.accept_button.rect.center = [150, 125]     # adjust placement of button
        for button in self.buttons: button.rect.y += 8  # move notification sprite buttons down a few pixels to fit blurb

        [button.draw(self.image) for button in self.buttons]

    # UPDATE STATE
    
    def draw(self, surface):
        surface.blit(self.image, self.rect)
        
        if self.shimmering:
            surface.blit(self.shimmer_surface, self.rect)
        

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
                if self.accept_button.rect.collidepoint(rel_mouse_pos):
                    self.next_x -= 1000

                    if self.notification.type == 'FRIEND':
                        self.addFriend(self.notification.sender.username)
                    else: 
                        print(self.notification.type)
                        self.startNetwork(self.shown_user)
                
                if self.delete_button.rect.collidepoint(rel_mouse_pos):
                    self.next_x += 1000

    def update(self, mouse_pos, events):

        self.handleInputs(mouse_pos, events)
        
        if self.shimmering and self.frames >= self.next_shimmer_frame:
            
            if self.frames % 3 == 0:
            
                self.shimmer_index += 1
                if self.shimmer_index >= len(self.shimmer_images):
                    self.shimmer_index = 0
                    self.next_shimmer_frame = self.frames + 90
                    
                prev_alpha = self.shimmer_surface.get_alpha()
                self.shimmer_surface = Surface(self.shimmer_images[self.shimmer_index].get_size(), pygame.SRCALPHA, 32)
                self.shimmer_surface.blit(self.shimmer_images[self.shimmer_index], [0, 0])
                self.shimmer_surface.set_alpha(prev_alpha)
                    
                    
                if not self.notification.new and self.shimmer_surface.get_alpha() > 0:
                    self.shimmer_surface.set_alpha(max(self.shimmer_surface.get_alpha() - 10, 0))
                
            if self.shimmer_surface.get_alpha() == 0:
                self.shimmering = False
                
            if self.image.get_alpha() != 255:
                self.shimmer_surface.set_alpha(max(self.shimmer_surface.get_alpha() - 10, 0))
                

        return super().update()
    
    