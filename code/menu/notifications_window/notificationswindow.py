from pygame.locals import *
import pygame.mouse
from pygame.sprite import Group
from pygame.mixer import Sound
from pygame.transform import smoothscale
from pygame.surface import Surface
from pygame.image import load
import pygame
from typing import Callable
import sqlalchemy
from sqlalchemy.orm import exc


from createdb import User, Notification
from ...screen_elements.scrollbar import ScrollBar
from ...screen_elements.button import Button
from ...screen_elements.text import Text
from ...screen_elements.clickabletext import ClickableText
from ..scrollablewindow import ScrollableWindow
from .notificationsprite import NotificationSprite
from sqlalchemy import create_engine, func, delete, select, case
from sqlalchemy.orm import Session

class NotificationsWindow(ScrollableWindow):
    def __init__(self, user: User, session: Session, addFriend: Callable, startNetwork: Callable, notifyMenu: Callable):
        super().__init__(user, session, 'right')
        self.addFriend = addFriend
        self.startNetwork = startNetwork
        self.notifyMenu = notifyMenu
        self.addAssets()
        self.initGroup()

    def addAssets(self):

        # load images

        self.name_tags = []
        for i in range(4):
            self.name_tags.append(load(f'assets/backgrounds/hello_stickers/{i}.png'))
        self.name_tags.append(load('assets/paper/killfeed_larger.png').convert_alpha())
            
        self.challenge_tags = []
        for i in range(4):
            self.challenge_tags.append(load(f'assets/backgrounds/challenge_stickers/{i}.png'))
        self.challenge_tags.append(self.name_tags[-1])
        
        self.shimmer_images = []
        for i in range(33):
            self.shimmer_images.append(load(f'assets/backgrounds/sticker shimmer/{i}.png').convert_alpha())
            
        # create and add screen elements
        self.new_notification_sound = Sound('assets/sounds/new_notification.wav')

        self.header = Text('notifications', 40, 300, 115)
        self.mark_all_text = Text('mark all as read', 30, 280, 168)
        self.delete_all_text = Text('delete all', 30, 280, 202)
        self.mark_all_button = Button('check_s', 30, [400, 168])
        self.delete_all_button = Button('trash_s', 30, [360, 202])
        
        # new notification count
        new_count = len([n for n in self.user.notifications_owned if n.new])
        self.sprite_count_text = Text(f'{new_count}', 30, 45, 25, align='topright', color='red', outline_color='white')
        if self.sprite_count_text.text == '0': self.sprite_count_text.fastOff()

        self.screen_elements.append(self.header)
        self.screen_elements.append(self.mark_all_text)
        self.screen_elements.append(self.delete_all_text)
        self.screen_elements.append(self.mark_all_button)
        self.screen_elements.append(self.delete_all_button)
        self.screen_elements.append(self.sprite_count_text)
        # notification count

    def initGroup(self):
        for notification in reversed(self.user.notifications_owned):
            self.addNotificationSprite(notification, new=False, shimmer_images=self.shimmer_images)

    def handleInputs(self, mouse_pos, events):
        rel_mouse_pos = [mouse_pos[0] - self.x, mouse_pos[1] - self.y]
        
        super().handleInputs(mouse_pos, events)

        # handle events
        for event in events:
            if event.type == MOUSEBUTTONDOWN: 

                if self.delete_all_button.rect.collidepoint(rel_mouse_pos): self.deleteAllNotifications()
                
                if self.mark_all_button.isHovAndEnabled(rel_mouse_pos): self.markNotificationsAsRead()
     
    def checkNotificationsUpdate(self, prev_opponent = None):
        '''check if notifications have been added or removed'''
        
        # prev_opponent of menu needs to be cleared once pending notifications from that opponent have been cleared
        clear_prev_opponent = prev_opponent != None
        
        # compare current notifications with displayed notifications, remove/delete accordingly
        displayed_notifications = set()
        sprites_to_remove = []
        ids_to_update = []
        '''return this list to menu for the shape icon to be updated on friendsprite'''

        # determine which notifications are to be removed
        for sprite in self.group.sprites():
            try: 
                displayed_notifications.add(sprite.notification.id) #if notification.id causes an error, it has been deleted
                
                # remove challenge notifications from previous opponent
                if prev_opponent and sprite.notification.type == 'CHALLENGE' and sprite.notification.sender_id == prev_opponent.id:
                    sprites_to_remove.append(sprite)
                    
            # signal a deleted notification to kill it's sprite
            except (exc.ObjectDeletedError, sqlalchemy.exc.InvalidRequestError):
                sprites_to_remove.append(sprite)
        
        
        # Add sprites for new notifications
        for notification in self.user.notifications_owned:
            
            if notification.id not in displayed_notifications:
                
                if notification.type == 'FAVORITE_CHANGE':
                    ids_to_update.append(notification.sender_id)
                    
                    for sprite in self.group.sprites():
                        if notification.sender_id == sprite.notification.sender_id:
                            sprite.initSurface()
                            
                    continue
                
                if self.current_opp_id != -1: self.new_notification_sound.play()
                sprite = self.addNotificationSprite(notification, shimmer_images=self.shimmer_images)
                
                # remove incoming notifications from current opponent
                if self.current_opp_id == notification.sender_id:
                    sprites_to_remove.append(sprite)
                
        
        # remove sprites with deleted notifications
        for sprite in sprites_to_remove: sprite.next_x += 1000

        return clear_prev_opponent, ids_to_update

    def addNotificationSprite(self, notification: Notification, new: bool = True, shimmer_images: list[Surface] = None):
        
        # create notification on main menu
        if new: self.notifyMenu(notification)
        
        sprite = NotificationSprite(
            self.user, 
            notification,
            -1, 
            self.session, 
            self.name_tags if notification.type == 'FRIEND' else self.challenge_tags,
            self.addFriend,
            self.startNetwork,
            len(self.group),
            True,
            shimmer_images
        )

        self.addSprite(sprite, False)
        
        return sprite

    def deleteAllNotifications(self):
        for sprite in self.group.sprites(): sprite.next_x += 1000
        
    def update(self, mouse_pos, events):
        
        if len(self.user.notifications_owned) != self.sprite_count_text.text:
            self.updateSpriteCountText()

        super().update(mouse_pos, events)
        
    def markNotificationsAsRead(self):
        '''mark all notifications as read'''
        for notification in self.user.notifications_owned:
            notification.new = False
            
        self.updateSpriteCountText()
        
        for sprite in self.group.sprites():
            sprite.new = False
            
        self.session.commit()

    def updateSpriteCountText(self):
        new_count = len([n for n in self.user.notifications_owned if n.new])
        self.sprite_count_text.updateText(f'{new_count}')
            
        if self.sprite_count_text.text == '0': self.sprite_count_text.turnOff()
        else: self.sprite_count_text.turnOn()