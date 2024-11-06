from pygame.locals import *
import pygame.mouse
from pygame.sprite import Group
from pygame.mixer import Sound
from pygame.transform import smoothscale
from pygame.surface import Surface
from pygame.image import load
import pygame, random, math

from createdb import User, Shape as ShapeData, Notification, friends, GamePlayed
from ...screen_elements.text import Text
from ...screen_elements.editabletext import EditableText
from ...screen_elements.button import Button
from ...game.gamedata import color_data
from sqlalchemy import func, delete, select, case
from sqlalchemy.orm import Session

class NotificationSprite(pygame.sprite.Sprite):

    # INIT

    def __init__(self, user: User, notification: Notification, position: int, session: Session, current_length = None):
        super().__init__()

        self.user = user
        self.notification = notification
        self.position = position
        self.session = session
        self.current_length = current_length

        self.initSprite()
        self.initSurface()

    def initSprite(self):
        self.height = 170
        self.width = 350

        self.x = 250 + (30 * (math.pow(-1, self.position if self.current_length == None else self.current_length))) + (random.randint(-5, 5))
        self.y = 350 + self.position * 175 + random.randint(-10, 10)
        self.next_y = self.y
        self.next_x = self.x
        self.v = 0
        self.a = 1.5
        self.alpha = 0 if self.current_length != None else 255
        self.fading = False

        self.image = Surface([self.width, self.height], pygame.SRCALPHA, 32)
        self.rect = self.image.get_rect()
        self.rect.center = [self.x, self.y]
        self.background = Surface([self.width, self.height], pygame.SRCALPHA, 32)
        self.background.fill((200, 19, 111, 180))
        self.rerender_icons = False

        # try:
        #     self.shape = self.session.query(ShapeData).where(ShapeData.id == self.friend.favorite_id).one()
        #     self.shape_image = smoothscale(load(f'assets/shapes/backgrounds/{self.shape.type}/{color_data[self.shape.color_id].name}.png').convert_alpha(), [100, 100])
        #     self.username_text = Text(f'{self.friend.username}', 60, 133, 40, 'topleft', color_data[self.shape.color_id].text_color, 200, 'black')

        #     self.face_image = smoothscale(load(f'assets/shapes/faces/{self.shape.type}/{self.shape.face_id}/0.png').convert_alpha(), [100, 100])

        # except:
        #     self.shape_image = smoothscale(load('assets/shapes/backgrounds/circle/black.png').convert_alpha(), [100, 100])
        #     self.username_text = Text(f'{self.friend.username}', 60, 133, 40, 'topleft', max_width=200)
        #     self.face_image = Surface([1, 1])


        # self.challenge_button = Button('swords', 35, [150, 125])
        # self.info_button = Button('question', 35, [230, 125])
        self.delete_button = Button('trash', 35, [310, 125])

        self.buttons = [
            # self.challenge_button, self.info_button, 
            self.delete_button
        ]

    def initSurface(self):
        self.image.blit(self.background, [0, 0])

    # def initInfo(self):
    #     self.info_hovered = False
    #     self.info_alpha = 0
    #     self.info_y = 180

    #     self.info_surface = Surface([450, 250], pygame.SRCALPHA, 32)
    #     self.info_rect = self.info_surface.get_rect()
    #     self.info_rect.center = [self.x, self.y + self.info_y]
        
    #     background = load('assets/paper/killfeed_larger.png').convert_alpha()
    #     tape_surface = smoothscale(load('assets/paper/tape_0_xl.png').convert_alpha(), (410, 90))
    #     tape_rect = tape_surface.get_rect()
    #     tape_rect.center = 225, 35

    #     max_level = self.session.execute(select(func.max(ShapeData.level)).where(ShapeData.owner_id == self.friend.id)).scalar()
    #     wins_losses = self.session.execute(
    #         select(
    #             func.count(case((GamePlayed.winner_id == self.user.id, 1))).label("wins"),
    #             func.count(case((GamePlayed.winner_id == self.friend.id, 1))).label("losses")
    #         ).where(
    #             ((GamePlayed.player1_id == self.user.id) & (GamePlayed.player2_id == self.friend.id)) | 
    #             ((GamePlayed.player1_id == self.friend.id) & (GamePlayed.player2_id == self.user.id))
    #         )
    #     ).one()
    #     win_loss = 'n/a' if wins_losses.wins + wins_losses.losses == 0 else f'{round(wins_losses.wins / (wins_losses.wins + wins_losses.losses) * 100)}%'

    #     texts = [
    #         Text('joined on:', 28, 150, 66),
    #         Text(f'{self.friend.date_joined.strftime("%d-%m-%Y")}', 26, 290, 66),
    #         Text(f'wins: {self.friend.num_wins}           shapes: {self.friend.num_shapes}', 28, 225, 115),
    #         Text(f'max level: {max_level}', 28, 225, 140),
    #         Text(f'your win %:  {win_loss}', 28, 225, 190),
    #     ]
        
    #     self.info_surface.blit(background, [25, 20])
    #     [text.draw(self.info_surface) for text in texts]
    #     self.info_surface.blit(tape_surface, tape_rect)

    # UPDATE STATE

    def renderIcons(self):
        [button.draw(self.image) for button in self.buttons]

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
        # if self.info_button.rect.collidepoint(rel_mouse_pos):
        #     self.info_hovered = True
        #     self.info_alpha = min(self.info_alpha + 15, 255)
        #     self.info_surface.set_alpha(self.info_alpha)
        # elif self.info_alpha > 0:
        #     self.info_alpha = max(self.info_alpha - 15, 0)
        #     self.info_surface.set_alpha(self.info_alpha)
        # else: 
        #     self.info_hovered = False
        
        for event in events:
            if event.type == MOUSEBUTTONDOWN:
                # if self.challenge_button.rect.collidepoint(rel_mouse_pos):
                #     print('START GAME')
                
                if self.delete_button.rect.collidepoint(rel_mouse_pos):
                    self.next_x += 1000

    def positionSelf(self):
        if self.x != self.next_x:

            if not self.fading: 
                self.fading = True
                return True

            self.v += self.a
            self.x += self.v
            self.alpha -= 15
            self.rect.center = [self.x, self.y]
            

            if self.alpha <= 0:
                self.kill()
            else: self.image.set_alpha(self.alpha)

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
                self.y = max(self.y - self.v, self.next_y)
            elif self.y < self.next_y:
                self.y = min(self.y + self.v, self.next_y)

            # reset the velocity when the window reaches its target
            if self.y == self.next_y: self.v = 0

            self.rect.center = [self.x, self.y]

    def update(self, mouse_pos, events):

        self.handleInputs(mouse_pos, events)

        # rerender icons if need be
        if self.rerender_icons:
            self.renderIcons()

        # fade in if new
        if not self.fading and self.alpha <= 255:
            self.alpha += 15
            self.image.set_alpha(self.alpha)

        # returns true if sprite is moving to the right (is being removed)
        return self.positionSelf()
    
    # UTILITY

    def moveUp(self):
        self.next_y -= 175

    def moveDown(self):
        self.next_y += 175
