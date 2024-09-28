import pygame, random, os, numpy, math, time, itertools
from pygame import Surface
from pygame.locals import *
from pygame.sprite import Group
import pygame.sprite

from screen_elements.clickabletext import ClickableText
from screen_elements.doublecheckbox import DoubleCheckbox
from screen_elements.text import Text

from createdb import User, Shape as ShapeData

from game_files.shape import Shape
from game_files.powerup2 import Powerup
from game_files.circledata import *
from game_files.circledata import colors as color_data

class Game2:
    def __init__(self, screen: Surface, shape_1_data: ShapeData, shape_2_data: ShapeData, user_1: User, user_2: User, seed = False, player_simulated = False, server_simulated = False):
        # seed randomness
        if seed != False: random.seed(seed)
        
        # parameters from menu
        self.screen = screen
        self.shape_1_data = shape_1_data
        self.shape_2_data = shape_2_data
        self.user_1 = user_1
        self.user_2 = user_2
        self.seed = seed

        # necessary variables for simulating game
        self.running = True
        self.done = False
        self.screen_w = 1720
        self.screen_h = 1080
        self.fps = 60
        self.frames = 0

        self.powerup_data = powerup_data

        # flags for simulation efficiency
        self.player_simulated = player_simulated
        self.server_simulated = server_simulated

        # variables for all data on shapes and teams
        self.team_1_shape_count = shape_1_data.team_size
        self.team_2_shape_count = shape_2_data.team_size
        self.total_shape_count = self.team_1_shape_count + self.team_2_shape_count

        self.team_1_max_hp = shape_1_data.health * shape_1_data.team_size
        self.team_2_max_hp = shape_2_data.health * shape_2_data.team_size

        self.team_2_total_hp = shape_2_data.health * shape_2_data.team_size
        self.team_2_total_hp = shape_2_data.health * shape_2_data.team_size

        self.team_1_group = Group()
        self.team_2_group = Group()

        # additional groups
        self.powerup_group = Group()
        self.laser_group = Group()
        self.buckshot_group = Group()
        self.clouds_group = Group()
        self.explosions_group = Group()
        self.killfeed_group = Group()

        # define containers for images
        self.shape_1_images = []
        self.shape_2_images = []

        self.smoke_images = []
        self.powerup_images_small = []
        self.powerup_images_medium = []

        # ALL SIMULATION NECESSARY THINGS ABOVE THIS POINT
        if self.server_simulated: return

        # TODO load necessary images for stats screen
        if self.player_simulated: 
            return
        
        # load background and update display
        self.background = pygame.image.load("backgrounds/BG1.png")
        self.title_text = Text("shapegame", 150, 1920/2, 1080/10)
        self.screen.blit(self.background, (0, 0))
        self.screen.blit(self.title_text.surface, self.title_text.rect)
        pygame.display.update()

        # necessary variables for playing game
        self.clock = pygame.time.Clock()

        # load images

        # load shape images
        for i in range(0, 4):
            # TODO assuming 100px extra on the radius will be plenty for now, confirm somehow later
            self.shape_1_images.append(pygame.transform.smoothscale(pygame.image.load("circles/{}/{}/{}.png".format(shape_1_data.face_id, color_data[shape_1_data.color_id][0], i)), (shape_1_data.radius_max + 100, shape_1_data.radius_max + 100)))
            self.shape_2_images.append(pygame.transform.smoothscale(pygame.image.load("circles/{}/{}/{}.png".format(shape_2_data.face_id, color_data[shape_2_data.color_id][0], i)), (shape_2_data.radius_max + 100, shape_2_data.radius_max + 100)))

        # load powerup images
        for powerup in self.powerup_data:
            image = pygame.image.load(self.powerup_data[powerup][0])
            self.powerup_images_small.append(pygame.transform.smoothscale(image, (20, 20)))
            self.powerup_images_medium.append(pygame.transform.smoothscale(image, (40, 40)))

        # load sounds

        # create screen elements
        self.exit_clickable = ClickableText("back", 50, 1860, 1045)
        self.clickables = [self.exit_clickable]

        # load and center cursor
        self.cursor = pygame.transform.smoothscale(pygame.image.load("backgrounds/cursor.png"), (12, 12))
        self.cursor_rect = self.cursor.get_rect()
        self.cursor_rect.center = pygame.mouse.get_pos()

        # create shapes
        for i in range(0, shape_1_data.team_size):
            self.team_1_group.add(Shape(shape_1_data, i, 0, self.shape_1_images, self.powerup_images_small))

        for i in range(0, shape_2_data.team_size):
            self.team_2_group.add(Shape(shape_2_data, i, 1, self.shape_2_images, self.powerup_images_small))

    def handleInputs(self):
        """ handle all inputs from user"""
        for event in pygame.event.get():
            if event.type == MOUSEBUTTONDOWN:
                
                if event.button == 1:
                    if self.exit_clickable.rect.collidepoint(pygame.mouse.get_pos()):
                        self.running = False

    def spawnRandomPowerups(self):
        """spawn a random powerup every few seconds"""

        if not self.done and self.frames % (1 * self.fps) == 0:
            powerup_name = random.choice(list(self.powerup_data.keys()))
            powerup_image = self.powerup_images_medium[self.powerup_data[powerup_name][1]]
            xy = [random.randint(20, self.screen_w - 20), random.randint(20, self.screen_h - 20)]

            self.powerup_group.add(Powerup(powerup_name, powerup_image, xy))

    def drawScreenElements(self):
        """update and draw any and all screen elements"""

        # get mouse position
        mouse_pos = pygame.mouse.get_pos()

        # update and draw clickable elements
        for clickable in self.clickables:
            clickable.update(mouse_pos)
            self.screen.blit(clickable.surface, clickable.rect)

        # update and draw cursor
        self.cursor_rect.center = pygame.mouse.get_pos()
        self.screen.blit(self.cursor, self.cursor_rect)

        # finally flip the display
        pygame.display.flip()

    def shapeCollectPowerup(self, shape: Shape, powerup: Powerup):
        """handler for shape collecting a powerup"""

        # shapes can have max 5 powerups
        if len(shape.powerup_arr) == 5: return

        # handle everything that the game has to do regarding the pickup
        # (sounds, killfeed...)
        # if powerup.name == "insta-kill":
        # elif powerup.name == "resurrect":
        # elif powerup.name == "star":
        # elif powerup.name == "muscle":
        # elif powerup.name == "speed":
        # elif powerup.name == "health":
        # elif powerup.name == "bomb":
        # elif powerup.name == "laser":
        # elif powerup.name == "buckshot":
        # elif powerup.name == "mushroom":

        # let shape handle pickup
        shape.collectPowerup(powerup)
        
        # kill powerup
        powerup.kill()

    def detectCollisions(self):
        """simple method for collision detection, will want to be redone"""

        for powerup in self.powerup_group:
            for shape in itertools.chain(self.team_1_group, self.team_2_group):
                dist = math.sqrt((powerup.x - shape.x)**2 + (powerup.y - shape.y)**2)
                max_dist = powerup.r + shape.r

                if (dist <= max_dist):
                    self.shapeCollectPowerup(shape, powerup)

    def updateGameElements(self):
        """update all game elements (shapes, powerups, killfeed), separate from drawGameElements for easier simulation"""

        # spawn powerups
        self.spawnRandomPowerups()

        # update groups
        self.powerup_group.update()
        self.team_1_group.update()
        self.team_2_group.update()

        # detect collisions
        self.detectCollisions()

    def drawGameElements(self):
        """draw all game elements (shapes, powerups, killfeed), separate from updateGameElements for easier simulation"""

        # draw background here since we want shapes on bottom layer
        self.screen.blit(self.background, (0, 0))

        # draw groups
        self.powerup_group.draw(self.screen)
        self.team_1_group.draw(self.screen)
        self.team_2_group.draw(self.screen)

    def resetSingleFrameFlags(self):
        """reset any flags that are raised along the game loop"""

    def play(self):
        """game play driver"""
        while self.running:
            self.frames += 1

            self.resetSingleFrameFlags()

            self.handleInputs()

            self.updateGameElements()

            self.drawGameElements()

            self.drawScreenElements()

            self.clock.tick(self.fps)

            


            

