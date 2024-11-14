from pygame.locals import *
import pygame.mouse
from pygame.sprite import Group
from pygame.mixer import Sound
from pygame.transform import smoothscale
from pygame.surface import Surface
from pygame.image import load
import pygame
from typing import Callable


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
    def __init__(self, user: User, session: Session, addFriend: Callable, startNetwork: Callable):
        super().__init__(user, session, 'right')
        self.addFriend = addFriend
        self.startNetwork = startNetwork

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

        # create and add screen elements

        self.header = Text('notifications', 40, 300, 115)
        self.mark_all_text = Text('mark all as read', 30, 280, 168)
        self.delete_all_text = Text('delete all', 30, 280, 202)
        self.mark_all_button = Button('check_s', 30, [400, 168])
        self.delete_all_button = Button('trash_s', 30, [360, 202])

        self.texts.append(self.header)
        self.texts.append(self.mark_all_text)
        self.texts.append(self.delete_all_text)
        self.clickables.append(self.mark_all_button)
        self.clickables.append(self.delete_all_button)

        # notification count
        self.notification_count = Text('0', 30, 30, 10, color='red')

    def initGroup(self):
        for notification in reversed(self.user.notifications_owned):
            self.addNotificationSprite(notification)

    def handleInputs(self, mouse_pos, events):
        rel_mouse_pos = [mouse_pos[0] - self.x, mouse_pos[1] - self.y]
        
        super().handleInputs(mouse_pos, events)

        # handle events
        for event in events:
            if event.type == MOUSEBUTTONDOWN: 

                if self.delete_all_button.rect.collidepoint(rel_mouse_pos): self.deleteAllNotifications()
     
    def checkNotificationsUpdate(self):
        '''check if a notification has been added'''

        if len(self.group) != len(self.user.notifications_owned):
            self.addNotificationSprite(self.user.notifications_owned[-1])

    def addNotificationSprite(self, notification: Notification):

        self.addSprite(NotificationSprite(
            self.user, 
            notification,
            -1, 
            self.session, 
            self.name_tags if notification.type == 'FRIEND' else self.challenge_tags,
            self.addFriend,
            self.startNetwork,
            len(self.group),
            True
        ))

    def deleteAllNotifications(self):
        for sprite in self.group.sprites(): sprite.next_x += 1000