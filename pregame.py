from pygame.locals import *
from network import Network
from request import Request
from network import Network

class Pregame:
    def __init__(self, id):
        self.id = id
        self.ready = False

        self.players_ready = [False, False]

        self.faces = [0, 0]
        self.colors = [0, 0]

        self.seed = False

