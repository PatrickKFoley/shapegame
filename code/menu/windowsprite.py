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

class WindowSprite(pygame.sprite.Sprite):

    def __init__(self, user: User, shown_user: User, session: Session, position: int, backgrounds: list[Surface], current_length: int, side: str, new = False):
        super().__init__()
        
        self.user = user
        self.shown_user = shown_user
        self.session = session
        self.position = position
        self.current_length = current_length
        self.backgrounds = backgrounds
        self.side = side
        self.new = new

        self.initSprite()

    def initSprite(self):
        self.height = 170
        self.width = 350
        
        self.x = 250 + (30 * (math.pow(-1, self.position if self.current_length == None else self.current_length))) + (random.randint(-5, 5)) + (50 if self.side == 'right' else 0)
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
        self.background = random.choice(self.backgrounds)
        self.rerender_icons = False

        try:
            self.shape = self.session.query(ShapeData).where(ShapeData.id == self.shown_user.favorite_id).one()
            self.shape_image = smoothscale(load(f'assets/shapes/backgrounds/{self.shape.type}/{color_data[self.shape.color_id].name}.png').convert_alpha(), [100, 100])
            self.username_text = Text(f'{self.shown_user.username}', 60, 133, 40, 'topleft', color_data[self.shape.color_id].text_color, 200, 'black')

            self.face_image = smoothscale(load(f'assets/shapes/faces/{self.shape.type}/{self.shape.face_id}/0.png').convert_alpha(), [100, 100])

        except:
            self.shape_image = smoothscale(load('assets/shapes/backgrounds/circle/black.png').convert_alpha(), [100, 100])
            self.username_text = Text(f'{self.shown_user.username}', 60, 133, 40, 'topleft', max_width=200)
            self.face_image = Surface([1, 1])

        self.delete_button = Button('trash', 35, [310, 125])

        self.buttons = [
            self.delete_button
        ]
        
    def renderIcons(self):
        [button.draw(self.image) for button in self.buttons]

    def positionSelf(self):
        if self.x != self.next_x:

            if not self.fading: 
                self.fading = True
                return True

            self.v += self.a
            self.alpha -= 15
            self.rect.center = [self.x, self.y]
            
            if self.x < self.next_x:
                self.x = min(self.x + 10, self.next_x)
            else:
                self.x = max(self.x - 10, self.next_x)
            
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
            
    def moveUp(self):
        self.next_y -= 175

    def moveDown(self):
        self.next_y += 175
        
    def update(self):
        # rerender icons if need be
        if self.rerender_icons:
            self.renderIcons()

        # fade in if new
        if not self.fading and self.alpha <= 255:
            self.alpha += 15
            self.image.set_alpha(self.alpha)

        # returns true if sprite is moving to the right (is being removed)
        return self.positionSelf()
