import pygame, copy
from pygame.locals import *
from pygame.image import load
from screen_elements.text import Text
from screen_elements.editabletext import EditableText
from screen_elements.clickabletext import ClickableText
from shared_functions import *
from createdb import User, Notification
from sqlalchemy.orm import Session

# how many pixels per frame the window moves
STEP_SIZE = 20

class NotificationSprite(pygame.sprite.Sprite):
    def __init__(self, notification: Notification, index: int):
        super().__init__()

        self.notification = notification
        self.index = index
        self.type = notification.type

        self.width = 1920/4
        self.height = 70

        self.y = 200 + (index * self.height)

        # create text elements
        self.message = Text(notification.message, 40, 20, 20, "topleft")
        self.x = Text("x", 50, self.width-10, -5, "topright", "red")
        self.o = Text("o", 50, self.width-11, 25, "topright", "green")

        self.surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA, 32)
        pygame.draw.rect(self.surface, (0, 0, 0, 200), (10, 10, self.width, self.height))

        self.surface.blit(self.message.surface, self.message.rect)
        self.surface.blit(self.x.surface, self.x.rect)
        self.surface.blit(self.o.surface, self.o.rect)
        self.rect = self.surface.get_rect()
        self.rect.topleft = (0, self.y)

    def moveUp(self):
        self.index -= 1
        self.y = 200 + (self.index * self.height)
        self.rect.topleft = (0, self.y)


class NotificationsWindow:
    def __init__(self, user: User, session: Session):
        self.user = user
        self.session = session

        self.width = int(1920/4)
        self.height = 1080

        self.x = 1920
        self.next_x = self.width
        self.selected = False

        self.background = pygame.transform.smoothscale(load("backgrounds/BG0.png"), (self.width, self.height))
        self.background.set_alpha(235)
        self.surface = self.background.copy()
        self.rect = self.surface.get_rect()

        self.notifications_text = Text("notifications", 75, self.width/2, 75)
        # self.friend_editable = EditableText("add friend: ", 50, self.width/2, 150)

        self.notifications: list[NotificationSprite] = []

        for idx, notification in enumerate(self.user.notifications):
            self.notifications.append(NotificationSprite(notification, idx))

        self.align()

    # toggle the window being opened or closed
    def toggle(self):
        if self.selected:
            self.selected = False
            self.next_x = 1920
        else:
            self.selected = True
            self.next_x = 1920 - self.width

    # called every frame, opens and closes the window
    def move(self):
        # window should move to the left
        if self.selected and self.x > self.next_x:
            self.x -= STEP_SIZE

            # don't let it go too far
            if self.x < self.next_x: self.x = self.next_x

            self.align()

        # window should move to the left
        elif not self.selected and self.x < self.next_x:
            self.x += STEP_SIZE

            # don't let it go too far
            if self.x > self.next_x: self.x = self.next_x

            self.align()
    
    # move the window to its current position
    def align(self):
        self.rect.topleft = [self.x, 0]

    # returns something as a redirect
    def handleEvents(self, mouse_pos, events):
        for event in events:
            # if left click
            if event.type == MOUSEBUTTONDOWN and event.button == 1:

                for notification in self.notifications:

                    rel_mouse_pos = (mouse_pos[0] - 3*1920/4, mouse_pos[1] - notification.y)

                    if notification.x.rect.collidepoint(rel_mouse_pos):
                        self.deleteNotification(notification.index)

                    elif notification.o.rect.collidepoint(rel_mouse_pos):

                        # handle different types of notifications differently
                        if notification.type == "FRIEND":

                            try:
                                friend = self.session.query(User).filter(User.username == notification.notification.additional).one()
                                
                                self.user.friends.append(friend)
                                self.session.add(Notification(friend.id, friend, f'{self.user.username} added you back!', "TEXT"))
                                self.session.commit()

                            except Exception as e:
                                print(f'Error adding friend: {e}')

                            self.deleteNotification(notification.index)

                            return "added friend"

    def deleteNotification(self, index):
        # flag to control if notifications should move upwards
        deleted = False
        deleted_notification = None

        for notification in self.notifications:

            if notification.index == index:
                deleted_notification = notification

                deleted = True

            elif deleted:
                notification.moveUp()

        self.notifications.remove(deleted_notification)
        del deleted_notification


    # update the window and all its elements
    def update(self, mouse_pos, events):
        self.surface = self.background.copy()
        self.move()

        if not self.selected and self.x == 1920: return

        # handle events will return a friends name if one was clicked on
        redirect = self.handleEvents(mouse_pos, events)
        if redirect != None: return redirect

        self.surface.blit(self.notifications_text.surface, self.notifications_text.rect)

        for element in self.notifications:
            self.surface.blit(element.surface, element.rect)