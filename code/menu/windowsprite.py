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

    def __init__(self, user: User, session: Session, position: int, new = False):
        self.user = user
        self.session = session
        self.position = position
        self.new = new

        self.initSprite()

    def initSprite(self):
        self.height = 170
        self.width = 350