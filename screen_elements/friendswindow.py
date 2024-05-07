import pygame
from pygame.locals import *
from game_files.circledata import *
from pygame.image import load
from screen_elements.text import Text
from screen_elements.editabletext import EditableText
from screen_elements.clickabletext import ClickableText
from createdb import User, Notification, Shape
from sqlalchemy.orm import Session

# how many pixels per frame the window moves
STEP_SIZE = 20

class FriendSprite(pygame.sprite.Sprite):
    def __init__(self, friend: User, index: int, session: Session):
        super().__init__()

        self.friend = friend
        self.index = index
        self.session = session

        self.width = 1920/4 - 10
        self.height = 180

        self.y = 200 + (index * self.height)
        self.next_y = self.y

        self.surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA, 32)
        pygame.draw.rect(self.surface, (0, 0, 0, 200), (10, 10, self.width, self.height))

        self.friend_favorite = self.session.query(Shape).where(Shape.id == self.friend.favorite_id).one()

        self.favorite_circle = pygame.transform.smoothscale(pygame.image.load("circles/{}/{}/0.png".format(self.friend_favorite.face_id, colors[self.friend_favorite.color_id][0])), (150, 150))
        self.favorite_circle_rect = self.favorite_circle.get_rect()
        self.favorite_circle_rect.center = (95, 95)

        self.friend_name = Text(self.friend.username, 75, 190, self.height/3, "topleft", colors[self.friend_favorite.color_id][2])
        self.x = Text("x", 75, self.width-5, -5, "topright", "red")
        self.o = Text("play", 60, self.width-5, self.height - 72, "topright", "green")


        self.surface.blit(self.favorite_circle, self.favorite_circle_rect)
        self.surface.blit(self.friend_name.surface, self.friend_name.rect)
        self.surface.blit(self.x.surface, self.x.rect)
        self.surface.blit(self.o.surface, self.o.rect)

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
        self.background.set_alpha(235)
        self.surface = self.background.copy()
        self.rect = self.surface.get_rect()

        self.friends_text = Text("friends", 100, self.width/2, 75)
        self.friend_editable = EditableText("add friend: ", 50, self.width/2, 150)

        self.friend_sprites: list[FriendSprite] = []

        for idx, friend in enumerate(self.user.friends):
            self.friend_sprites.append(FriendSprite(friend, idx, self.session))



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

                # return a players name if starting a match
                # for clickable in self.friends_clickables:
                #     if clickable.rect.collidepoint(mouse_pos):
                #         return clickable.getText()

            # if enter pressed
            elif event.type == KEYDOWN and event.key == K_RETURN:
                # try to add user as friend
                try:
                    friend = self.session.query(User).filter(User.username == self.friend_editable.getText()).one()
                    
                    # if found, add as friend and notify
                    print(self.user.id)
                    self.session.add(Notification(friend.id, friend, f'{self.user.username} now follows you', "FRIEND", self.user.username))
                    self.user.friends.append(friend)
                    print(friend)
                    self.session.commit()

                    # add a clickable for this new friend
                    self.friends_clickables.append(ClickableText(friend.username, 50, 50, 250 + ((len(self.user.friends) - 1) * 60), "topleft"))


                # user not found
                except Exception as e:
                    print(f'Error adding friend: {e}')

    def open(self):
        self.selected = True
        self.next_x = 0
        self.x = 0
        self.align()

    # update the window and all its elements
    def update(self, mouse_pos, events):
        self.surface = self.background.copy()
        self.move()

        if not self.selected and self.x == 0-self.width: return

        # handle events will return a friends name if one was clicked on
        redirect = self.handleEvents(mouse_pos, events)
        if redirect != None: return redirect

        # update editable
        self.friend_editable.update(events)
        self.surface.blit(self.friends_text.surface, self.friends_text.rect)
        self.surface.blit(self.friend_editable.surface, self.friend_editable.rect)
        
        
        for element in self.friend_sprites:
            element.update()
            self.surface.blit(element.surface, element.rect)


                

    