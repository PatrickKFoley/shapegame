from pygame.locals import *
from pygame.sprite import *
from pygame.mixer import *
from pygame import *

import pygame, random, math, numpy as np

from sqlalchemy.orm import Session
from menu_files.create_shape_files.newmenushape import NewMenuShape
from game_files.circledata import *
from server_files.database_classes import User, Shape
from threading import Thread
from screen_elements.clickabletext import ClickableText
from screen_elements.text import Text

from shared_functions import *

class CreateShapeMenu():
    def __init__(self, screen: Surface, user: User, shapes: list[Shape], session: Session, circle_images_full: list[list[Surface]]):
        # parameters from Menu
        self.user = user
        self.shapes = shapes
        self.screen = screen
        self.session = session
        self.circle_images_full = circle_images_full

        # create pygame objects
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font("backgrounds/font.ttf", 80)

        # pygame sprite group for new shapes
        self.new_shapes_group = Group()

        # load and center cursor, load background
        self.background = pygame.image.load("backgrounds/BG1.png")
        self.cursor = pygame.transform.smoothscale(pygame.image.load("backgrounds/cursor.png"), (12, 12))
        self.cursor_rect = self.cursor.get_rect()
        self.cursor_rect.center = pygame.mouse.get_pos()

        # load sounds
        self.click_sound = Sound("sounds/click.wav")
        self.close_sound = Sound("sounds/close.wav")
        self.close_sound.set_volume(.5)
        
        # create all text elements
        self.shape_tokens_remaining_text: Text | None = None
        self.title_text = Text("shapegame", 150, 1920/2, 1080/2)
        self.create_shape_text = Text("create a new shape!", 150, 1920/2, 90)
        self.logged_in_as_text = Text("logged in as: " + self.user.username, 35, 1900, 10, "topright")

        self.texts: list[Text | None] = []
        self.texts.append(self.title_text)
        self.texts.append(self.create_shape_text)
        self.texts.append(self.logged_in_as_text)

        # create all clickable elements
        self.exit_clickable = ClickableText("exit", 50, 1870, 1045)
        self.go_to_collections_clickable = ClickableText("go to collections", 40, 450, 1045)
        self.create_clickable = ClickableText("create!", 50, 1920/2, 1000)

        self.clickables: list[ClickableText] = []
        self.clickables.append(self.exit_clickable)
        self.clickables.append(self.go_to_collections_clickable)
        self.clickables.append(self.create_clickable)

        # update the display
        self.screen.blit(self.background, (0, 0))
        self.screen.blit(self.title_text.surface, self.title_text.rect)
        pygame.display.update()

        # misc stuff
        self.newest_stats_surface: Surface | None = None

    def start(self):
        self.shape_tokens_remaining_text = Text("shape tokens: " + str(self.user.shape_tokens), 35, 10, 1030, "topleft")
        self.texts.append(self.shape_tokens_remaining_text)

        while True:
            # handle all inputs, which might return a redirect
            redirect = self.handleInputs()
            if redirect != None: return redirect

            # draw all screen elements
            self.drawScreenElements()

            # tick clock
            self.clock.tick(60)

    # start helpers

    def handleInputs(self):
        events = pygame.event.get()
        mouse_pos = pygame.mouse.get_pos()

        # handle inputs
        for event in events:
            if event.type == MOUSEBUTTONDOWN: 
                self.click_sound.play()

                # deselect all new shapes
                for shape in self.new_shapes_group:
                    shape.deselect()

                # if we click on a shape we want to see that shape's stats
                for shape in self.new_shapes_group:
                    if shape.rect.collidepoint(mouse_pos):
                        self.newest_stats_surface = shape.stats_surface
                        shape.select()

                # if we are exiting
                if self.exit_clickable.rect.collidepoint(mouse_pos):
                    self.new_shapes_group.empty()
                    return "NONE"

                # if collections redirect is clicked
                elif self.go_to_collections_clickable.rect.collidepoint(mouse_pos):
                    return "COLLECTIONS"

                elif self.create_clickable.rect.collidepoint(mouse_pos) and self.user.shape_tokens != 0:
                    # create new shape, add to db
                    new_shape = createShape(self.user.id, self.session, self.user.username)
                    new_menu_shape = NewMenuShape(new_shape, self.circle_images_full[new_shape.face_id][new_shape.color_id])
                    self.newest_stats_surface = new_menu_shape.stats_surface

                    # rewrite number of tokens remaining
                    self.texts.remove(self.shape_tokens_remaining_text)
                    self.shape_tokens_remaining_text = Text("shape tokens: " + str(self.user.shape_tokens), 35, 10, 1030, "topleft")
                    self.texts.append(self.shape_tokens_remaining_text)
                    
                    # add to user's collection group
                    self.shapes.append(new_shape)
                    self.new_shapes_group.add(new_menu_shape)

    def drawScreenElements(self):
        # draw + update all elements

        # flip the display, get mouse position
        pygame.display.flip()
        mouse_pos = pygame.mouse.get_pos()

        # draw the background
        self.screen.blit(self.background, (0, 0))
        
        # draw and update new shapes
        self.checkShapeCollisions(self.new_shapes_group)
        self.new_shapes_group.update()
        self.new_shapes_group.draw(self.screen)

        # if there are stats to show
        if self.newest_stats_surface != None:
            self.screen.blit(self.newest_stats_surface, [-50, 640])

        # update and draw clickable elements
        for clickable in self.clickables:

            # only want the create clickable to be shown if user has shape tokens
            if clickable == self.create_clickable:
                if self.user.shape_tokens > 0:
                   self.screen.blit(clickable.surface, clickable.rect)

            # otherwise, show all clickables
            elif clickable != None:
                clickable.update(mouse_pos)
                self.screen.blit(clickable.surface, clickable.rect)

        # draw all text elements
        for text in self.texts:
            if text != None and text != self.title_text:
                self.screen.blit(text.surface, text.rect)

        # if the user has shape tokens to spend
        if self.user.shape_tokens != 0:
            self.screen.blit(self.create_clickable.surface, self.create_clickable.rect)

        # center and draw cursor
        self.cursor_rect.center = mouse_pos
        self.screen.blit(self.cursor, self.cursor_rect)

    # shape related functions

    def checkShapeCollisions(self, group, damage = False):
        for s1 in group.sprites():
            for s2 in group.sprites():
                if s1 == s2: continue

                dist = math.sqrt( (s1.x - s2.x)**2 + (s1.y - s2.y)**2 )
                max_dist = s1.r + s2.r

                if dist <= max_dist: self.collideShapes(s1, s2, damage)

    def collideShapes(self, s1, s2, damage = False):
        if damage:
            # check if either shapes have instant kill, and should win collision
            if 0 in s1.powerups and 0 in s2.powerups:
                pass
            elif 0 in s1.powerups:
                self.shapeDamageShape(s1, s2)
            elif 0 in s2.powerups:
                self.shapeDamageShape(s2, s1)

            else:
                roll_1 = random.randint(1, 20) + s1.luck
                roll_2 = random.randint(1, 20) + s2.luck

                if roll_1 > roll_2:
                    self.shapeDamageShape(s1, s2)
                else:
                    self.shapeDamageShape(s2, s1)

        s1.x -= s1.v_x
        s1.y -= s1.v_y
        s2.x -= s2.v_x
        s2.y -= s2.v_y

        # STEP 1

        [x2, y2] = [s2.x, s2.y]
        [x1, y1] = [s1.x, s1.y]

        norm_vec = np.array([x2 - x1, y2 - y1])

        divisor = math.sqrt(norm_vec[0]**2 + norm_vec[1]**2)
        unit_vec = np.array([norm_vec[0] / divisor, norm_vec[1] / divisor])

        unit_tan_vec = np.array([-1 * unit_vec[1], unit_vec[0]])

        # STEP 2

        v1 = np.array([s1.v_x, s1.v_y])
        m1 = 10

        v2 = np.array([s2.v_x, s2.v_y])
        m2 = 10

        # STEP 3

        v1n = np.dot(unit_vec, v1)

        v1t = np.dot(unit_tan_vec, v1)

        v2n = np.dot(unit_vec, v2)

        v2t = np.dot(unit_tan_vec, v2)

        # STEP 4

        v1tp = v1t

        v2tp = v2t

        # STEP 5

        v1np = ((v1n * (m1 - m2)) + (2 * m2 * v2n)) / (m1 + m2)

        v2np = ((v2n * (m2 - m1)) + (2 * m1 * v1n)) / (m1 + m2)

        # STEP 6

        v1np_ = v1np * unit_vec
        v1tp_ = v1tp * unit_tan_vec

        v2np_ = v2np * unit_vec
        v2tp_ = v2tp * unit_tan_vec

        # STEP 7

        v1p = v1np_ + v1tp_
        s1.setVel(v1p)

        v2p = v2np_ + v2tp_
        s2.setVel(v2p)
