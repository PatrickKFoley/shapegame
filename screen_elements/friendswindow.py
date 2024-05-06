import pygame
from pygame.locals import *
from pygame.image import load
from screen_elements.text import Text
from screen_elements.editabletext import EditableText
from screen_elements.clickabletext import ClickableText
from createdb import User, Notification
from sqlalchemy.orm import Session

# how many pixels per frame the window moves
STEP_SIZE = 20

class FriendsWindow:
    def __init__(self, user: User, session: Session):
        self.user = user
        self.session = session

        self.width = int(1920/4)
        self.height = 1080

        self.x = 0 - self.width
        self.next_x = 0 - self.width
        self.selected = False

        self.background = pygame.transform.smoothscale(load("backgrounds/BG0.png"), (self.width, self.height))
        self.background.set_alpha(220)
        self.surface = self.background.copy()
        self.rect = self.surface.get_rect()

        self.friends_text = Text("friends", 100, self.width/2, 75)
        self.friend_editable = EditableText("add friend: ", 50, self.width/2, 150)

        self.friends_clickables: list[ClickableText] = []

        for idx, friend in enumerate(self.user.friends):
            self.friends_clickables.append(ClickableText(friend.username, 50, 50, 250 + (idx * 60), "topleft"))

        self.align()

    # toggle the window being opened or closed
    def toggle(self):
        if self.selected:
            self.selected = False
            self.next_x = 0 - self.width
        else:
            self.selected = True
            self.next_x = 0

    # called every frame, opens and closes the window
    def move(self):
        # window should move to the right
        if self.selected and self.x < self.next_x:
            self.x += STEP_SIZE

            # don't let it go too far
            if self.x > self.next_x: self.x = self.next_x

            self.align()

        # window should move to the left
        elif not self.selected and self.x > self.next_x:
            self.x -= STEP_SIZE

            # don't let it go too far
            if self.x < self.next_x: self.x = self.next_x

            self.align()

    # move the window to its current position
    def align(self):
        self.rect.topleft = [self.x, 0]

    # returns a friends name if one is clicked as a redirect
    def handleEvents(self, mouse_pos, events):
        for event in events:
            # if left click
            if event.type == MOUSEBUTTONDOWN and event.button == 1:

                if self.friend_editable.rect.collidepoint(mouse_pos):
                    # turn off editable
                    self.friend_editable.deselect()

                    # if clicking on editable
                    if self.friend_editable.rect.collidepoint(mouse_pos):
                        self.friend_editable.select()

                for clickable in self.friends_clickables:
                    if clickable.rect.collidepoint(mouse_pos):
                        return clickable.getText()

            # if enter pressed
            elif event.type == KEYDOWN and event.key == K_RETURN:
                # try to add user as friend
                try:
                    friend = self.session.query(User).filter(User.username == self.friend_editable.getText()).one()
                    
                    # if found, add as friend and notify
                    self.user.friends.append(friend)
                    self.session.add(Notification(friend.id, friend, f'{self.user.username} added you as a friend!'))
                    self.session.commit()

                    # add a clickable for this new friend
                    self.friends_clickables.append(ClickableText(friend.username, 50, 50, 250 + ((len(self.user.friends) - 1) * 60), "topleft"))


                # user not found
                except Exception as e:
                    print(f'Error adding friend: {e}')

    # update the window and all its elements
    def update(self, mouse_pos, events):
        self.surface = self.background.copy()
        self.move()

        if not self.selected: return

        # handle events will return a friends name if one was clicked on
        redirect = self.handleEvents(mouse_pos, events)
        if redirect != None: return redirect

        # update editable
        self.friend_editable.update(events)
        self.surface.blit(self.friends_text.surface, self.friends_text.rect)
        self.surface.blit(self.friend_editable.surface, self.friend_editable.rect)
        for element in self.friends_clickables:
            element.update(mouse_pos)
            self.surface.blit(element.surface, element.rect)


                

    