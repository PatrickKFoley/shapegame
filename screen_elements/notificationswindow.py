import pygame, time
from pygame.locals import *
from pygame.image import load
from screen_elements.text import Text
from screen_elements.editabletext import EditableText
from screen_elements.clickabletext import ClickableText
from shared_functions import *
from createdb import User, Notification
from sqlalchemy.orm import Session
from threading import Thread

# how many pixels per frame the window moves
STEP_SIZE = 20

class NotificationSprite(pygame.sprite.Sprite):
    def __init__(self, notification: Notification, index: int):
        super().__init__()

        self.notification = notification
        self.index = index
        self.type = notification.type
        # TYPES: FRIEND, INVITE, TEXT

        self.width = 1920/4 - 10
        self.height = 125

        self.y = 200 + (index * self.height)
        self.next_y = self.y

        # create text elements
        self.title: Text | None = None
        self.message: Text | None = None
        self.x = Text("x", 75, self.width-5, -5, "topright", "red")
        self.o = Text("o", 75, self.width-10, self.height - 80, "topright", "green")

        # keep the message pixel length < 393
        font_size = 40
        self.message = Text(notification.message, font_size, self.width/2 - 25, 90, "center")
        while self.message.surface.get_size()[0] >= 393:
            font_size -= 2
            
            del self.message
            self.message = Text(notification.message, font_size, self.width/2 - 25, 90, "center")

        # change title to fit type of notification
        if self.type == "FRIEND":
            self.title = Text("new follower!", 50, self.width/2 - 25, 40, "center")
        elif self.type == "INVITE":
            self.title = Text("game invite!", 50, self.width/2 - 25, 40, "center")
        elif self.type == "TEXT":
            self.title = Text("shapegame", 50, self.width/2 - 25, 40, "center")

        self.surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA, 32)
        pygame.draw.rect(self.surface, (0, 0, 0, 200), (10, 10, self.width, self.height))

        self.surface.blit(self.title.surface, self.title.rect)
        self.surface.blit(self.message.surface, self.message.rect)
        self.surface.blit(self.x.surface, self.x.rect)
        if self.type != "TEXT": self.surface.blit(self.o.surface, self.o.rect)
        self.rect = self.surface.get_rect()
        self.rect.topleft = (0, self.y)

    def update(self):
        # if needs to move up
        if self.y > self.next_y:
            self.y -= STEP_SIZE/2

            if self.y < self.next_y:
                self.y = self.next_y

            self.rect.topleft = (0, self.y)

    def moveUp(self):
        self.index -= 1
        self.next_y = 200 + (self.index * self.height)
        self.rect.topleft = (0, self.y)


class NotificationsWindow:
    def __init__(self, user: User, session: Session):
        self.user = user
        self.session = session

        # self.thread_running = True
        # self.thread = Thread(target=self.poll)
        # self.thread.start()
        self.frames = 0

        self.width = int(1920/4)
        self.height = 1080

        self.x = 1920
        self.next_x = self.width
        self.selected = False

        self.background = pygame.transform.smoothscale(load("backgrounds/side_window.png"), (self.width, self.height))
        self.background.set_alpha(235)
        self.surface = self.background.copy()
        self.rect = self.surface.get_rect()

        self.notifications_text = Text("notifications", 75, self.width/2, 75)
        # self.friend_editable = EditableText("add friend: ", 50, self.width/2, 150)

        self.notifications: list[NotificationSprite] = []

        for idx, notification in enumerate(self.user.notifications):
            self.notifications.append(NotificationSprite(notification, idx))

        self.num_notifications = len(self.notifications)

        self.align()

    def __del__(self):
        self.thread_running = False

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
                                
                                self.session.add(Notification(friend.id, friend, f'{self.user.username} added you back', "TEXT"))
                                self.user.friends.append(friend)
                                
                                self.session.commit()

                            except Exception as e:
                                print(f'Error adding friend: {e}')

                            self.deleteNotification(notification.index)

                            return "added friend"
                        
                        # if clicking an invite, return the inviter's name
                        if notification.type == "INVITE":
                            self.deleteNotification(notification.index)
                            return notification.notification.additional

                        if notification.type == "TEXT":
                            self.deleteNotification(notification.index)

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

        # remove database entry
        try:
            entry = self.session.query(Notification).where(Notification.id == notification.notification.id).one()
            self.session.delete(entry)
            self.session.commit()
        except:
            self.session.rollback()
        # self.user.notifications.remove(self.user.notifications[index])
        
        # delete sprite
        self.notifications.remove(deleted_notification)
        del deleted_notification

        self.num_notifications -= 1

    # update the window and all its elements
    def update(self, mouse_pos, events):
        self.surface = self.background.copy()
        self.move()

        self.frames += 1
        if self.frames % 120 == 0: 
            self.session.commit()

        # new notification received
        if self.num_notifications != len(self.user.notifications):
            self.notifications.append(NotificationSprite(self.user.notifications[-1], len(self.user.notifications)-1))

            self.num_notifications += 1

        if not self.selected and self.x == 1920: return

        # handle events will return a friends name if one was clicked on
        redirect = self.handleEvents(mouse_pos, events)
        if redirect != None: return redirect

        self.surface.blit(self.notifications_text.surface, self.notifications_text.rect)

        for element in self.notifications:
            element.update()
            self.surface.blit(element.surface, element.rect)

        