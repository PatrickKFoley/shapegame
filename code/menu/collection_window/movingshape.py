from pygame.locals import *
from pygame.transform import smoothscale
from pygame.surface import Surface
from pygame.image import load
import pygame, pytz

from createdb import Shape as ShapeData
from ...screen_elements.text import Text
from ...game.gamedata import color_data, shape_data as shape_model_data
from sqlalchemy import func


class MovingShape(pygame.sprite.Sprite):
    def __init__(self, image: Surface, side: str = 'top'):
        super().__init__()

        self.image = image.convert_alpha()
        self.side = side

        self.x = 705
        self.y = 200 if self.side == 'top' else 1080-200
        self.next_y = 1080-219 if self.side == 'top' else 200
        self.v = 0
        self.a = 1.5


        self.image.set_alpha(255)
        self.rect = self.image.get_rect()
        self.rect.center = [self.x, self.y]

    def update(self):

        # move to target position
        if self.y == self.next_y: return

        distance = abs(self.y - self.next_y)

        if distance > 50:
            self.v += self.a
        else:
            self.v = max(1, distance * 0.2)
            
        if self.y > self.next_y:
            self.y = max(self.y - self.v, self.next_y)
        elif self.y < self.next_y:
            self.y = min(self.y + self.v, self.next_y)

        self.rect.center = [self.x, self.y]

