from pygame.locals import *
import pygame.mouse
from pygame.sprite import Group
from pygame.mixer import Sound
from pygame.transform import smoothscale
from pygame.surface import Surface
from pygame.image import load
import pygame, random, math

from createdb import User, Shape as ShapeData, Notification, friends, GamePlayed
from ..screen_elements.text import Text
from ..screen_elements.editabletext import EditableText
from ..screen_elements.button import Button
from ..game.gamedata import color_data
from sqlalchemy import func, delete, select, case
from sqlalchemy.orm import Session

class FriendSprite(pygame.sprite.Sprite):
    def __init__(self, user: User,friend: User, position: int, session: Session, name_tags: list[Surface], current_length = None,):
        super().__init__()

        self.user = user
        self.friend = friend
        self.position = position
        self.session = session

        self.height = 170
        self.width = 350

        self.x = 250 + (30 * (math.pow(-1, position if current_length == None else current_length))) + (random.randint(-5, 5))
        self.y = 350 + position * 175 + random.randint(-10, 10)
        self.next_y = self.y
        self.next_x = self.x
        self.v = 0
        self.a = 1.5
        self.alpha = 0 if current_length != None else 255
        self.fading = False

        self.image = Surface([self.width, self.height], pygame.SRCALPHA, 32)
        self.rect = self.image.get_rect()
        self.rect.center = [self.x, self.y]
        self.background = random.choice(name_tags)
        self.rerender_icons = False

        try:
            self.shape = self.session.query(ShapeData).where(ShapeData.id == self.friend.favorite_id).one()
            self.shape_image = smoothscale(load(f'assets/shapes/backgrounds/{self.shape.type}/{color_data[self.shape.color_id].name}.png').convert_alpha(), [100, 100])
            self.username_text = Text(f'{self.friend.username}', 60, 133, 40, 'topleft', color_data[self.shape.color_id].text_color, 200)

            self.face_image = smoothscale(load(f'assets/shapes/faces/{self.shape.type}/{self.shape.face_id}/0.png').convert_alpha(), [100, 100])

        except:
            self.shape_image = smoothscale(load('assets/shapes/backgrounds/circle/black.png').convert_alpha(), [100, 100])
            self.username_text = Text(f'{self.friend.username}', 60, 133, 40, 'topleft', max_width=200)
            self.face_image = Surface([1, 1])


        self.challenge_button = Button('swords', 35, [150, 125])
        self.info_button = Button('question', 35, [230, 125])
        self.delete_button = Button('trash', 35, [310, 125])

        self.buttons = [
            self.challenge_button, self.info_button, self.delete_button
        ]

        self.renderSurface()
        self.renderInfo()

    def renderInfo(self):
        self.info_hovered = False
        self.info_alpha = 0
        self.info_y = 180

        self.info_surface = Surface([450, 250], pygame.SRCALPHA, 32)
        self.info_rect = self.info_surface.get_rect()
        self.info_rect.center = [self.x, self.y + self.info_y]
        
        background = load('assets/paper/killfeed_larger.png').convert_alpha()
        tape_surface = smoothscale(load('assets/paper/tape_0_xl.png').convert_alpha(), (410, 90))
        tape_rect = tape_surface.get_rect()
        tape_rect.center = 225, 35

        max_level = self.session.execute(select(func.max(ShapeData.level)).where(ShapeData.owner_id == self.friend.id)).scalar()
        wins_losses = self.session.execute(
            select(
                func.count(case((GamePlayed.winner_id == self.user.id, 1))).label("wins"),
                func.count(case((GamePlayed.winner_id == self.friend.id, 1))).label("losses")
            ).where(
                ((GamePlayed.player1_id == self.user.id) & (GamePlayed.player2_id == self.friend.id)) | 
                ((GamePlayed.player1_id == self.friend.id) & (GamePlayed.player2_id == self.user.id))
            )
        ).one()
        win_loss = 'n/a' if wins_losses.wins + wins_losses.losses == 0 else f'{round(wins_losses.wins / (wins_losses.wins + wins_losses.losses) * 100)}%'

        texts = [
            Text('joined on:', 28, 150, 66),
            Text(f'{self.friend.date_joined.strftime("%d-%m-%Y")}', 26, 290, 66),
            Text(f'wins: {self.friend.num_wins}           shapes: {self.friend.num_shapes}', 28, 225, 115),
            Text(f'max level: {max_level}', 28, 225, 140),
            Text(f'your win %:  {win_loss}', 28, 225, 190),
        ]
        
        self.info_surface.blit(background, [25, 20])
        [text.draw(self.info_surface) for text in texts]
        self.info_surface.blit(tape_surface, tape_rect)

    def handleInputs(self, mouse_pos, events):
        rel_mouse_pos = [mouse_pos[0] - self.x + self.width/2, mouse_pos[1] - self.y + self.height/2]

        [button.update(rel_mouse_pos) for button in self.buttons]
        
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
                    print('START GAME')
                
                elif self.delete_button.rect.collidepoint(rel_mouse_pos):
                    self.next_x -= 1000

    def update(self, mouse_pos, events):

        self.handleInputs(mouse_pos, events)

        if self.rerender_icons:
            self.renderIcons()

        if self.x != self.next_x:

            if not self.fading: 
                self.fading = True
                return True

            self.v += self.a
            self.x -= self.v
            self.alpha -= 15
            self.rect.center = [self.x, self.y]
            self.info_rect.center = [self.x, self.y + self.info_y]
            

            if self.alpha <= 0:
                self.kill()
            else: self.image.set_alpha(self.alpha)

        # fade in if new
        if not self.fading and self.alpha <= 255:
            self.alpha += 15
            self.image.set_alpha(self.alpha)

        # move into place
        if self.y != self.next_y:
            # calculate the remaining distance to the target
            distance = abs(self.y - self.next_y)

            # apply acceleration while far from the target, decelerate when close
            if distance > 50:
                self.v += self.a
            else:
                self.v = max(1, distance * 0.2)

            # move the window towards the target position, snap in place if position is exceeded
            if self.y > self.next_y:
                self.y -= self.v

                if self.y < self.next_y:
                    self.y = self.next_y

            elif self.y < self.next_y:
                self.y += self.v
                
                if self.y > self.next_y:
                    self.y = self.next_y 

            # reset the velocity when the window reaches its target
            if self.y == self.next_y:
                self.v = 0

            self.rect.center = [self.x, self.y]
            self.info_rect.center = [self.x, self.y + self.info_y]

    def renderSurface(self):
        self.image.blit(self.background, [0, 0])
        self.image.blit(self.username_text.surface, self.username_text.rect)
        self.image.blit(self.shape_image, [20, 46])
        self.image.blit(self.face_image, [20, 46])
        self.image.blit(self.challenge_button.surface, self.challenge_button.rect)
        self.image.blit(self.info_button.surface, self.info_button.rect)
        self.image.blit(self.delete_button.surface, self.delete_button.rect)

    def renderIcons(self):
        self.image.blit(self.challenge_button.surface, self.challenge_button.rect)
        self.image.blit(self.info_button.surface, self.info_button.rect)
        self.image.blit(self.delete_button.surface, self.delete_button.rect)

    def moveUp(self):
        self.next_y -= 175

    def moveDown(self):
        self.next_y += 175



class FriendsWindow:
    def __init__(self, user: User, session: Session):
        self.user = user
        self.session = session

        self.friends_group = Group()
        self.name_tags = []
        for i in range(4):
            self.name_tags.append(load(f'assets/backgrounds/hello_stickers/{i}.png'))

        for friend in self.user.friends:
            self.friends_group.add(FriendSprite(self.user, friend, len(self.friends_group.sprites()), self.session, self.name_tags))

        self.surface = Surface([550, 2160], pygame.SRCALPHA, 32)
        self.rect = self.surface.get_rect()
        self.rect.topleft = [-500, 0]

        self.frames_flag_raised = 0
        self.already_following_flag = False
        self.bad_credentials_flag = False
        self.thats_you_flag = False

        self.header = Text('followed players', 40, 250, 115)
        self.already_following = Text('already following!', 30, 250, 202)
        self.bad_credentials = Text('user not found!', 30, 250, 202)
        self.thats_you = Text('thats you, silly :3', 30, 250, 202)
        self.search_editable = EditableText('add player: ', 30, 250, 168)

        self.texts = [
            self.header
        ]

        self.button = Button('friends', 45, [525, 25])
        self.clickables = [
            self.button,
        ]

        self.background = load('assets/backgrounds/green_notebook.png').convert_alpha()
        self.background_rect = self.background.get_rect()
        self.background_rect.topleft = [0, 0]

        self.x = -500
        self.next_x = -500
        self.v = 0
        self.a = 1.5
        self.opened = False

        self.y = 0
        self.y_min = -500
        self.y_on_click = 0
        self.mouse_y_on_click = 0
        self.is_held = False

    def handleInputs(self, mouse_pos, events):
        rel_mouse_pos = [mouse_pos[0] - self.x, mouse_pos[1] - self.y]

        self.button.update(rel_mouse_pos)

        sprite_died = False
        for sprite in self.friends_group.sprites():
            if sprite_died: sprite.moveUp()

            if sprite.update(rel_mouse_pos, events): 
                sprite_died = True
                
                self.session.execute(delete(friends).where((friends.c.user_id == self.user.id) & (friends.c.friend_id == sprite.friend.id)))
                self.session.commit()


        self.search_editable.hovered = self.search_editable.rect.collidepoint(rel_mouse_pos)

        # handle events
        for event in events:
            if event.type == MOUSEBUTTONDOWN and event.button == 1:

                if self.button.rect.collidepoint(rel_mouse_pos):
                    self.toggle()

                # if the window is closed the only inputs we want to accept are the open button
                if not self.opened: return

                if self.rect.collidepoint(mouse_pos):
                    self.is_held = True
                    self.y_on_click = int(self.y)
                    self.mouse_y_on_click = mouse_pos[1]

                if self.search_editable.rect.collidepoint(rel_mouse_pos):
                    self.search_editable.select()
                else:
                    self.search_editable.deselect()

            elif event.type == MOUSEBUTTONUP:
                if self.rect.collidepoint(mouse_pos):
                    self.is_held = False

            elif event.type == KEYDOWN:
                if event.key == K_RETURN and (self.search_editable.selected or self.search_editable.hovered):
                    # try to add the user as a friend
                    username = self.search_editable.getText()

                    # lower flags
                    self.already_friends_flag = False
                    self.bad_credentials_flag = False
                    self.thats_you_flag = False

                    # query db for user
                    try:
                        searched_user = self.session.query(User).filter(User.username == username).one()
                    except Exception as e:
                        self.bad_credentials_flag = True
                        print(f"Could not add friend, none found: {e}")
                        return
                
                    # raise flags
                    self.already_friends_flag = any(friend.username == username for friend in self.user.friends)
                    self.thats_you_flag = searched_user.username == self.user.username
                    if self.already_friends_flag or self.thats_you_flag: return

                    # create friend sprite
                    sprite = FriendSprite(self.user, searched_user, -1, self.session, self.name_tags, len(self.friends_group))
                    sprites_copy = self.friends_group.sprites()
                    self.friends_group.empty()
                    self.friends_group.add(sprite)
                    self.friends_group.add(sprites_copy)

                    [sprite.moveDown() for sprite in self.friends_group.sprites()]



                    # add searched user to user following
                    try:
                        searched_user = self.session.query(User).filter(User.username == username).one()
                        self.session.add(Notification(searched_user.id, searched_user, f'{self.user.username} now follows you', "FOLLOWER", self.user.username))
                        self.user.friends.append(searched_user)
                        self.session.commit()

                    except Exception as e:
                        self.session.rollback()
                        print(f'Error creating notification: {e}')
                        return

    def toggle(self):
        self.opened = not self.opened

        if self.opened: self.next_x = 0
        else: self.next_x = -500

    def update(self, mouse_pos, events):
        '''update position of the collection window'''

        if any([self.already_following_flag, self.thats_you_flag, self.bad_credentials_flag]):
            self.frames_flag_raised += 1
            
            if self.frames_flag_raised == 180:
                self.frames_flag_raised = 0
                self.already_following_flag, self.bad_credentials_flag, self.thats_you_flag = False, False, False

        self.search_editable.update(events)

        self.handleInputs(mouse_pos, events)

        # self.friends_group.update(mouse_pos, events)

        # update elements
        
        self.positionWindow(mouse_pos)

        self.renderSurface()

    def positionWindow(self, mouse_pos):
        # update window positions
        if self.x != self.next_x:
        
            # calculate the remaining distance to the target
            distance = abs(self.x - self.next_x)

            # apply acceleration while far from the target, decelerate when close
            if distance > 50:
                self.v += self.a
            else:
                self.v = max(1, distance * 0.2)

            # move the window towards the target position, snap in place if position is exceeded
            if self.x > self.next_x:

                self.x = max(self.x - self.v, self.next_x)

            elif self.x < self.next_x:

                self.x = min(self.x + self.v, self.next_x)

            # reset the velocity when the window reaches its target
            if self.x == self.next_x:
                self.v = 0

        if self.is_held:
            self.y = max(self.y_min, min(mouse_pos[1] - self.mouse_y_on_click + self.y_on_click, 0))
            self.button.rect.center = [self.button.x, self.button.y - self.y]

        self.rect.topleft = [self.x, self.y]

    def renderSurface(self):
        self.surface.fill((0, 0, 0, 0))
        self.surface.blit(self.background, [0, 0])

        [self.surface.blit(clickable.surface, clickable.rect) for clickable in self.clickables]
        [self.surface.blit(text.surface, text.rect) for text in self.texts]

        self.surface.blit(self.search_editable.surface, self.search_editable.rect)

        if self.already_following_flag: self.surface.blit(self.already_following.surface, self.already_following.rect)
        if self.bad_credentials_flag: self.surface.blit(self.bad_credentials.surface, self.bad_credentials.rect)
        if self.thats_you_flag: self.surface.blit(self.thats_you.surface, self.thats_you.rect)

        self.friends_group.draw(self.surface)
        [self.surface.blit(sprite.info_surface, sprite.info_rect) for sprite in self.friends_group.sprites() if sprite.info_hovered]



