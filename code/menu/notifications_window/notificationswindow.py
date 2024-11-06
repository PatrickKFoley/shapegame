from pygame.locals import *
import pygame.mouse
from pygame.sprite import Group
from pygame.mixer import Sound
from pygame.transform import smoothscale
from pygame.surface import Surface
from pygame.image import load
import pygame

from createdb import User, Notification
from ...screen_elements.scrollbar import ScrollBar
from ...screen_elements.button import Button
from ..scrollablewindow import ScrollableWindow
from .notificationsprite import NotificationSprite
from sqlalchemy import create_engine, func, delete, select, case
from sqlalchemy.orm import Session

class NotificationsWindow(ScrollableWindow):
    def __init__(self, user: User, session: Session):
        super().__init__(user, session, 'right')

        self.initGroup()

    def initGroup(self):
        self.name_tags = []
        for i in range(4):
            self.name_tags.append(load(f'assets/backgrounds/hello_stickers/{i}.png'))
            
        self.challenge_tags = []
        for i in range(4):
            self.challenge_tags.append(load(f'assets/backgrounds/challenge_stickers/{i}.png'))
        
        for notification in self.user.notifications_owned:
            self.addSprite(NotificationSprite(self.user, notification, len(self.group.sprites()), self.session, self.name_tags if notification.type == 'FRIEND' else self.challenge_tags))

    def handleInputs(self, mouse_pos, events):
        rel_mouse_pos = [mouse_pos[0] - self.x, mouse_pos[1] - self.y]
        
        super().handleInputs(mouse_pos, events)

        # handle events
        for event in events:
            if event.type == MOUSEBUTTONDOWN: 

                for sprite in self.group.sprites():
                    pass
