import pygame
from pygame.locals import *
from game_files.circledata import *
from pygame.image import load
from screen_elements.text import Text
from screen_elements.editabletext import EditableText
from screen_elements.clickabletext import ClickableText
from createdb import User, Notification, Shape, friends
from sqlalchemy.orm import Session
from sqlalchemy import delete

# how many pixels per frame the window moves
STEP_SIZE = 20

class FriendSprite(pygame.sprite.Sprite):
    def __init__(self, friend: User, index: int, session: Session, scroll = 0):
        super().__init__()

        self.friend = friend
        self.username = friend.username
        self.index = index
        self.session = session

        self.width = 1920/4 - 10
        self.height = 180

        self.y = 200 + (index * self.height)
        self.next_y = self.y
        self.y_init = self.y
        self.y_scroll = scroll

        self.surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA, 32)
        pygame.draw.rect(self.surface, (0, 0, 0, 200), (10, 10, self.width, self.height))

        try:
            self.friend_favorite = self.session.query(Shape).where(Shape.id == self.friend.favorite_id).one()
            self.friend_name = Text(self.friend.username, 75, 190, self.height/3, "topleft", colors[self.friend_favorite.color_id][2])
            self.favorite_circle = pygame.transform.smoothscale(pygame.image.load("circles/{}/{}/0.png".format(self.friend_favorite.face_id, colors[self.friend_favorite.color_id][0])), (150, 150))
        except:
            self.favorite_circle = pygame.Surface((1, 1), pygame.SRCALPHA, 32)
            self.friend_name = Text(self.friend.username, 75, 190, self.height/3, "topleft")

        
        self.favorite_circle_rect = self.favorite_circle.get_rect()
        self.favorite_circle_rect.center = (95, 95)

        self.x = Text("x", 75, self.width-5, -5, "topright", "red")
        self.o = Text("play", 60, self.width-5, self.height - 72, "topright", "green")


        self.surface.blit(self.favorite_circle, self.favorite_circle_rect)
        self.surface.blit(self.friend_name.surface, self.friend_name.rect)
        # self.surface.blit(self.x.surface, self.x.rect)
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
        self.next_y = 200 + (self.index * self.height) + self.y_scroll
        self.rect.topleft = (0, self.y)

    def scroll(self, amount):
        self.y_scroll += amount

        self.y = self.y_scroll + self.y_init
        self.next_y = self.y
        self.rect.topleft = (0, self.y)

class FriendsWindow:
    def __init__(self, user: User, session: Session):
        self.user = user
        self.session = session

        self.width = int(1920/4)
        self.height = 1080

        self.y = 0
        self.y_scroll = 0
        self.x = 0 - self.width
        self.next_x = 0 - self.width
        self.selected = False

        self.background = pygame.transform.smoothscale(load("backgrounds/BG0.png"), (self.width, self.height))
        self.background.set_alpha(235)
        self.surface = self.background.copy()
        self.rect = self.surface.get_rect()

        self.bad_credentials_flag = False
        self.already_friends_flag = False
        self.thats_you_flag = False
        self.frames_flag_raised = 0 # lower flag after some time

        self.friends_text = Text("friends", 100, self.width/2, 65)
        self.friend_editable = EditableText("add friend: ", 50, self.width/2, 140)
        self.bad_credentials = Text("no user found :(", 40, self.width/2, 185)
        self.already_friends = Text("already following :)", 40, self.width/2, 185)
        self.thats_you = Text("thats you, silly :3", 40, self.width/2, 185)

        self.friend_sprites: list[FriendSprite] = []

        for idx, friend in enumerate(self.user.friends):
            self.friend_sprites.append(FriendSprite(friend, idx, self.session))

        # now that we have sprites, figure out min and max for scroll amounts
        self.lock_scroll = True
        # (max) amount of scrolling permitted, determined by number of friends
        self.scroll_min: 0

        if len(self.friend_sprites) >= 5:
            self.lock_scroll = False

            # calculate the pixel length for all elements in the window
            px_len = 200 + (len(self.friend_sprites) * self.friend_sprites[0].height)

            # max scroll is window height - px_len
            self.scroll_min = (px_len - 1080 + 10) * -1

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
        self.rect.topleft = [self.x, self.y]

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
                for friend_sprite in self.friend_sprites:

                    rel_mouse_pos = (mouse_pos[0], mouse_pos[1] - friend_sprite.y)

                    if friend_sprite.x.rect.collidepoint(rel_mouse_pos):
                        # self.removeFriend(friend_sprite.index)
                        pass

                    elif friend_sprite.o.rect.collidepoint(rel_mouse_pos):
                        return friend_sprite.username

            # if enter pressed
            elif event.type == KEYDOWN and event.key == K_RETURN:
                # try to add user as friend
                username = self.friend_editable.getText()

                # lower flags
                self.already_friends_flag = False
                self.bad_credentials_flag = False
                self.thats_you_flag = False

                try:
                    friend = self.session.query(User).filter(User.username == username).one()
                except Exception as e:
                    self.bad_credentials_flag = True
                    print(f"Could not add friend, none found: {e}")

                for friend in self.user.friends:
                    if friend.username == username:
                        self.already_friends_flag = True

                if username == self.user.username: self.thats_you_flag = True
                
                if self.already_friends_flag or self.bad_credentials_flag or self.thats_you_flag:
                    return

                # if found, add as friend and notify
                try:
                    # NO CLUE WHY THIS NEEDS TO BE REPEATED
                    # otherwise friend is always the previously added friend
                    friend = self.session.query(User).filter(User.username == username).one()

                    # update database
                    self.session.add(Notification(friend.id, friend, f'{self.user.username} now follows you', "FRIEND", self.user.username))
                    self.user.friends.append(friend)
                    self.session.commit()

                except Exception as e:
                    self.session.rollback()
                    print(f'error adding a friend{e}')
                    return

                # add a friend_sprite for this new friend
                # self.friends_clickables.append(ClickableText(friend.username, 50, 50, 250 + ((len(self.user.friends) - 1) * 60), "topleft"))
                self.friend_sprites.append(FriendSprite(friend, len(self.user.friends)-1, self.session, self.y_scroll))

                # determine new min for scroll
                if len(self.friend_sprites) >= 5:
                    self.lock_scroll = False

                    # calculate the pixel length for all elements in the window
                    px_len = 200 + (len(self.friend_sprites) * self.friend_sprites[0].height)

                    # max scroll is window height - px_len
                    self.scroll_min = (px_len - 1080 + 10) * -1
                    print(self.scroll_min)

            # handle mouse scroll
            elif event.type == MOUSEWHEEL:
                if event.y == -1:
                    self.scroll("down")

                elif event.y == 1:
                    self.scroll("up")

            # handle arrow keys
            elif event.type == KEYDOWN:
                if event.key == K_DOWN:
                    self.scroll("down")

                elif event.key == K_UP:
                    self.scroll("up")

    def scroll(self, direction = "down"):
        # determine if we don't want to scroll
        if self.lock_scroll: return
        if direction == "up" and self.y_scroll == 0: return
        if direction == "down" and self.y_scroll == self.scroll_min: return

        # determine the jump size
        JUMP_SIZE = 20
        if direction == "down": JUMP_SIZE *= -1
        
        # ensure that we don't scroll to0 far
        if direction == "up":
            while self.y_scroll + JUMP_SIZE > 0:
                JUMP_SIZE -= 1
        else:
            while self.y_scroll + JUMP_SIZE < self.scroll_min:
                JUMP_SIZE += 1

        # keep a record of where we are scrolling
        self.y_scroll += JUMP_SIZE

        # all the elements on the screen
        self.friends_text.scroll(JUMP_SIZE)
        self.friend_editable.scroll(JUMP_SIZE)
        for sprite in self.friend_sprites:
            sprite.scroll(JUMP_SIZE)

    # instantly open the window
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

        # show errors if flag raised
        if self.bad_credentials_flag:
            self.frames_flag_raised += 1
            self.surface.blit(self.bad_credentials.surface, self.bad_credentials.rect)
        elif self.already_friends_flag:
            self.frames_flag_raised += 1
            self.surface.blit(self.already_friends.surface, self.already_friends.rect)
        elif self.thats_you_flag:
            self.frames_flag_raised += 1
            self.surface.blit(self.thats_you.surface, self.thats_you.rect)

        # lower flags after 3 seconds
        if self.frames_flag_raised == 180:
            self.frames_flag_raised = 0

            self.already_friends_flag = False
            self.bad_credentials_flag = False
            self.thats_you_flag = False
        
        
        for element in self.friend_sprites:
            element.update()
            self.surface.blit(element.surface, element.rect)

    def removeFriend(self, index):
        deleted = False
        deleted_friend = None

        for friend_sprite in self.friend_sprites:

            if friend_sprite.index == index:
                deleted_friend = friend_sprite
                deleted = True

            elif deleted:
                friend_sprite.moveUp()

        # entry = self.session.query(friends).where((friends.c.user_id == self.user.id) & (friends.c.friend_id == friend_sprite.friend.id))
        # self.session.delete(entry)

        # Construct the delete query
        delete_query = delete(friends).where(
            (friends.c.user_id == self.user.id) & (friends.c.friend_id == friend_sprite.friend.id)
        )

        # Execute the query
        # self.user.friends.remove(friend_sprite.friend)
        self.session.execute(delete_query)

        self.session.commit()

        self.friend_sprites.remove(deleted_friend)
        del deleted_friend

                

    