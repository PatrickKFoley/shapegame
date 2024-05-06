from pygame.locals import *
from pygame.sprite import *
from pygame.mixer import *
from pygame import *

import pygame, random, math, numpy as np, sys

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from screen_elements.clickabletext import ClickableText
from screen_elements.editabletext import EditableText
from screen_elements.friendswindow import FriendsWindow
from screen_elements.text import Text
from createdb import User, Shape
from menu_files.main_menu_files.menucircle import MenuShape
from menu_files.main_menu_files.simplecircle import SimpleCircle
from menu_files.powerupdisplaymenu import PowerupDisplayMenu
from menu_files.localmatchmenu import LocalMatchMenu
from menu_files.usercollectionmenu import UserCollectionMenu
from menu_files.createshapemenu import CreateShapeMenu
from menu_files.networkmatchmenu import NetworkMatchMenu
from menu_files.registermenu import RegisterMenu
from game_files.circledata import *

class Menu():
    def __init__(self):
        # misc attributes
        self.num_faces = len(circles)
        self.exit_clicked = False
        self.frames_since_exit_clicked = 0

        # your database entries
        self.user: User | None = None
        self.shapes: list[Shape] = []

        # database session
        self.engine = create_engine("postgresql://postgres:postgres@172.105.8.221/root/shapegame/shapegame/database.db", echo=False)
        SessionMaker = sessionmaker(bind=self.engine)
        self.session = SessionMaker()

        # sprite groups for your shapes (in network match), new shapes, simple circles (on main menu)
        self.you_group = Group()
        self.new_shapes_group = Group()
        self.simple_circle_sprites = Group()

        # load and center cursor, load background        
        self.background = pygame.image.load("backgrounds/BG1.png")
        self.cursor = pygame.transform.smoothscale(pygame.image.load("backgrounds/cursor.png"), (12, 12))
        self.cursor_rect = self.cursor.get_rect()
        self.cursor_rect.center = pygame.mouse.get_pos()

        # create pygame objects
        # self.screen = pygame.display.set_mode((1920, 1080), pygame.NOFRAME)
        self.screen = pygame.display.set_mode((1920, 1080))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font("backgrounds/font.ttf", 80)

        # load all sounds
        self.click_sound = Sound("sounds/click.wav")
        self.start_sound = Sound("sounds/start.wav")
        self.open_sound = Sound("sounds/open.wav")
        self.menu_music = Sound("sounds/menu.wav")
        self.close_sound = Sound("sounds/close.wav")
        self.open_sound.set_volume(.5)
        self.menu_music.set_volume(.5)
        self.close_sound.set_volume(.5)
        self.open_sound.play()
        
        # create all text elements
        self.logged_in_as_text: Text | None = None
        self.shape_tokens_clickable: Text | None = None
        self.title_text = Text("shapegame", 150, 1920/2, 1080/2)
        self.play_text = Text("play", 100, 3*1920/4, 750)
        self.bad_credentials_text = Text("user not found!", 150, 1920/2, 800)
        self.collections_text = Text("collections", 100, 1920/4, 750)

        self.texts: list[Text] = []
        self.texts.append(self.title_text)
        self.texts.append(self.play_text)
        self.texts.append(self.bad_credentials_text)
        self.texts.append(self.collections_text)

        # create all interactive elements
        self.network_match_clickable = ClickableText("network match", 50, 3 * 1920 / 4 - 200, 875)
        self.local_match_clickable = ClickableText("local match", 50, 3 * 1920 / 4 + 200, 875)
        self.your_shapes_clickable = ClickableText("your shapes", 50, 1 * 1920 / 4 - 250, 875)
        self.all_shapes_clickable = ClickableText("all shapes & powerups", 50, 1 * 1920 / 4 + 250, 875)
        self.exit_clickable = ClickableText("exit", 50, 1870, 1045)
        self.register_clickable = ClickableText("register", 50, 1920 / 2, 1050)
        self.username_editable = EditableText("Username: ", 60, 1920/2, 950)
        self.connect_to_player_editable = EditableText("Connect to user: ", 30, 0, 0, "topleft")
        self.username_editable.select()

        self.clickables: list[ClickableText] = []
        self.clickables.append(self.network_match_clickable)
        self.clickables.append(self.local_match_clickable)
        self.clickables.append(self.your_shapes_clickable)
        self.clickables.append(self.all_shapes_clickable)
        self.clickables.append(self.exit_clickable)
        self.clickables.append(self.register_clickable)

        # predefine the friend window (will be created once user has signed in)
        self.friends_window: FriendsWindow | None = None

        # update the display
        self.screen.blit(self.background, (0, 0))
        self.screen.blit(self.title_text.surface, self.title_text.rect)
        pygame.display.set_caption("shapegame")
        pygame.display.update()

        # load all shape images
        self.circle_images_full: list[list[Surface]] = []
        for i in range(0, 5):
            self.circle_images_full.append([])
            for color in colors:
                self.circle_images_full[i].append(pygame.image.load("circles/{}/{}/0.png".format(i, color[0])))

        self.circle_images: list[list[Surface]] = []
        for i in range(0, 5):
            self.circle_images.append([])
            for circle in self.circle_images_full[i]:
                self.circle_images[i].append(pygame.transform.smoothscale(circle, (200, 200)))

        # populate the simple circle group
        self.addNewCircles()

        # start playing menu music on loop
        self.menu_music.play(-1)

    def start(self):
        # run the login loop
        self.loginLoop()

        while True:
            events = pygame.event.get()

            # draw (and update) all screen elements
            self.drawScreenElements(events)

            # handle any inputs
            self.handleInputs(events)

            # leave after 1 second of exit being clicked
            if self.exit_clicked:
                self.frames_since_exit_clicked += 1
                if self.frames_since_exit_clicked == 60:
                    break

            # limits FPS to 60
            self.clock.tick(60)

    def loginLoop(self):
        # raise flag if user enters invalid credentials
        bad_credentials_flag = False
        
        # while user isn't signed in
        while self.user == None:

            # get pygame events
            events = pygame.event.get()
            mouse_pos = pygame.mouse.get_pos()

            # handle events
            for event in events:

                # exit clicked
                if event.type == MOUSEBUTTONDOWN and self.exit_clickable.rect.collidepoint(mouse_pos):
                    self.click_sound.play()
                    self.close_sound.play()
                    self.exit_clicked = True
                    pygame.mixer.Sound.fadeout(self.menu_music, 1000)

                # register clicked
                if event.type == MOUSEBUTTONDOWN and self.register_clickable.rect.collidepoint(mouse_pos):
                    self.click_sound.play()

                    # user's database entries are returned from the register menu
                    registerMenu = RegisterMenu(self.screen, self.session)
                    self.user, self.shapes = registerMenu.start()
                    del registerMenu

                    # create and add text elements 
                    self.logged_in_as_text= Text("logged in as: {}".format(self.user.username), 35, 10, 1030, "topleft")
                    self.shape_tokens_clickable = ClickableText("Shape tokens: " + str(self.user.shape_tokens), 35, 1920/2, 1030)
                    self.texts.append(self.logged_in_as_text)
                    self.clickables.append(self.shape_tokens_clickable)

                # if enter key is pressed
                if event.type == KEYDOWN and event.key == K_RETURN:

                    # get username user has entered
                    username = self.username_editable.getText()

                    # try to sign in
                    try:
                        # query database for user and user's shapes
                        self.user = self.session.query(User).filter(User.username == username).one()

                    # query found no user entries
                    except Exception as e:
                        bad_credentials_flag = True

            # update clickable texts
            self.username_editable.update(events)            

            # update clickable elements
            mouse_pos = pygame.mouse.get_pos()
            for clickable in self.clickables:
                clickable.update(mouse_pos)

            # draw all wanted screen elements
            pygame.display.flip()
            self.screen.blit(self.background, (0, 0))
            self.screen.blit(self.title_text.surface, self.title_text.rect)
            self.screen.blit(self.exit_clickable.surface, self.exit_clickable.rect)
            self.screen.blit(self.register_clickable.surface, self.register_clickable.rect)
            self.screen.blit(self.username_editable.surface, self.username_editable.rect)
            self.cursor_rect.center = mouse_pos
            self.screen.blit(self.cursor, self.cursor_rect)

            # handle exit
            if self.exit_clicked:
                self.frames_since_exit_clicked += 1
                if self.frames_since_exit_clicked == 60:
                    sys.exit()

            # show if credentials bad
            if bad_credentials_flag:
                self.screen.blit(self.bad_credentials_text.surface, self.bad_credentials_text.rect)

            self.clock.tick(60)

        # user has signed in, create and add text elements
        self.logged_in_as_text = Text("logged in as: {}".format(self.user.username), 35, 10, 1030, "topleft")
        self.shape_tokens_clickable = ClickableText("Shape tokens: " + str(self.user.shape_tokens), 35, 1920/2, 1030)
        self.texts.append(self.logged_in_as_text)
        self.clickables.append(self.shape_tokens_clickable)

        # create friends window
        self.friends_window = FriendsWindow()

        # load your (network match) shapes
        
        self.shapes = self.session.query(Shape).filter(Shape.owner_id == int(self.user.id)).all()

        for counter, shape in enumerate(self.shapes):
            self.you_group.add(MenuShape(counter+1, shape, self.circle_images_full[shape.face_id][shape.color_id], len(self.shapes)))


    def drawScreenElements(self, events):
        # draw + update all elements

        # flip the display, get mouse position
        pygame.display.flip()
        mouse_pos = pygame.mouse.get_pos()

        # draw background
        self.screen.blit(self.background, (0, 0))

        # update and draw simple circles
        self.checkCollisions()
        self.simple_circle_sprites.draw(self.screen)
        self.simple_circle_sprites.update()
        
        # update and draw clickable elements
        for clickable in self.clickables:
            if clickable != None and clickable != self.register_clickable:
                clickable.update(mouse_pos)
                self.screen.blit(clickable.surface, clickable.rect)

        # TEMPORARY draw connect to user
        self.connect_to_player_editable.update(events)
        self.screen.blit(self.connect_to_player_editable.surface, self.connect_to_player_editable.rect)

        # draw all text elements
        for text in self.texts:
            if text != None and text != self.bad_credentials_text:
                self.screen.blit(text.surface, text.rect)

        # update and draw friends window
        if self.friends_window != None:
            self.friends_window.update()
            self.screen.blit(self.friends_window.surface, self.friends_window.rect)

        # center and draw cursor
        self.cursor_rect.center = mouse_pos
        self.screen.blit(self.cursor, self.cursor_rect)

    def handleInputs(self, events):
        # handle all inputs to the main display

        # get events, mouse position
        mouse_pos = pygame.mouse.get_pos()

        for event in events:
            if event.type == MOUSEBUTTONDOWN:
                self.click_sound.play()
                
                # if left click
                if event.button == 1:
                    # turn off editable text
                    self.connect_to_player_editable.deselect()

                    # used to "redirect" from one menu to another
                    redirect = "NONE"

                    # clicked network match, but has no shapes
                    if self.network_match_clickable.rect.collidepoint(mouse_pos) and self.shapes == []:
                        # start shape creation menu, which might redirect
                        redirect = CreateShapeMenu(self.screen, self.user, self.shapes, self.session, self.circle_images_full).start()

                        # recreate shape token clickable, incase it changed
                        self.clickables.remove(self.shape_tokens_clickable)
                        self.shape_tokens_clickable = ClickableText("Shape tokens: " + str(self.user.shape_tokens), 35, 1920/2, 1030)
                        self.clickables.append(self.shape_tokens_clickable)

                    # clicked network match
                    elif self.network_match_clickable.rect.collidepoint(mouse_pos):
                        # get changes made to database
                        self.session.commit()

                        # create and start network match menu
                        networkMatch = NetworkMatchMenu(self.screen, self.user, self.shapes, self.session, self.circle_images_full)
                        networkMatch.start()
                        del networkMatch

                        # get changes made to database
                        self.session.commit()
                        self.shapes = self.session.query(Shape).filter(Shape.owner_id == int(self.user.id)).all()
                        
                        # recreate network match shape collection
                        self.you_group.empty()
                        for counter, shape in enumerate(self.shapes):
                            self.you_group.add(MenuShape(counter+1, shape, self.circle_images_full[shape.face_id][shape.color_id], len(self.shapes)))

                    # clicked local match
                    elif self.local_match_clickable.rect.collidepoint(mouse_pos):
                        LocalMatchMenu(self.screen, self.circle_images_full).start()

                    # clicked all shapes
                    elif self.all_shapes_clickable.rect.collidepoint(mouse_pos):
                        PowerupDisplayMenu(self.screen, self.circle_images_full).start()

                    # clicked on create shapes and has shape tokens
                    elif self.shape_tokens_clickable.rect.collidepoint(mouse_pos) and self.user.shape_tokens != 0:
                        # start shape creation menu, which might redirect
                        redirect = CreateShapeMenu(self.screen, self.user, self.shapes, self.session, self.circle_images_full).start()

                        # recreate shape token clickable, incase it changed
                        self.clickables.remove(self.shape_tokens_clickable)
                        self.shape_tokens_clickable = ClickableText("Shape tokens: " + str(self.user.shape_tokens), 35, 1920/2, 1030)
                        self.clickables.append(self.shape_tokens_clickable)

                    # clicked on collection, but has no shapes, but has shape tokens
                    elif self.your_shapes_clickable.rect.collidepoint(mouse_pos) and self.shapes == [] and self.user.shape_tokens != 0:
                        # start shape creation menu, which might redirect
                        redirect = CreateShapeMenu(self.screen, self.user, self.shapes, self.session, self.circle_images_full).start()

                        # recreate shape token clickable, incase it changed
                        self.clickables.remove(self.shape_tokens_clickable)
                        self.shape_tokens_clickable = ClickableText("Shape tokens: " + str(self.user.shape_tokens), 35, 1920/2, 1030)
                        self.clickables.append(self.shape_tokens_clickable)

                    # clicked on collection
                    elif self.your_shapes_clickable.rect.collidepoint(mouse_pos):
                        UserCollectionMenu(self.screen, self.circle_images_full, self.shapes, self.user, self.session).start()

                    # clicked exit
                    elif self.exit_clickable.rect.collidepoint(mouse_pos):
                        self.close_sound.play()
                        self.exit_clicked = True
                        pygame.mixer.Sound.fadeout(self.menu_music, 1000)

                    # connect to user editable clicked
                    elif self.connect_to_player_editable.rect.collidepoint(mouse_pos):
                        self.connect_to_player_editable.select()

                    # check if we want to redirect to another menu
                    if redirect != "NONE":

                        # so far collections is the only redirect
                        if redirect == "COLLECTIONS":
                            UserCollectionMenu(self.screen, self.circle_images_full, self.shapes, self.user, self.session).start()

            elif event.type == KEYDOWN and event.key == K_TAB:
                self.friends_window.toggle()

            elif event.type == KEYDOWN and event.key == K_RETURN and self.connect_to_player_editable.selected:
                client_method = "P2P." + self.connect_to_player_editable.getText() + "." + self.user.username + "."

                # get changes made to database
                self.session.commit()

                # create and start network match menu
                networkMatch = NetworkMatchMenu(self.screen, self.user, self.shapes, self.session, self.circle_images_full, client_method)
                networkMatch.start()
                del networkMatch

                # get changes made to database
                self.session.commit()
                self.shapes = self.session.query(Shape).filter(Shape.owner_id == int(self.user.id)).all()
                
                # recreate network match shape collection
                self.you_group.empty()
                for counter, shape in enumerate(self.shapes):
                    self.you_group.add(MenuShape(counter+1, shape, self.circle_images_full[shape.face_id][shape.color_id], len(self.shapes)))

    # SHAPE FUNCTIONS

    def addNewCircles(self):
        # CHANGE WHEN ADDING FACE_IDS
        self.new_circle_images = [0, 0, 0, 0, 0]
        self.new_circle_images[0] = self.circle_images[0].copy()
        self.new_circle_images[1] = self.circle_images[1].copy()
        self.new_circle_images[2] = self.circle_images[2].copy()
        self.new_circle_images[3] = self.circle_images[3].copy()
        self.new_circle_images[4] = self.circle_images[4].copy()

        self.face_id = random.randint(0, self.num_faces - 1)
        self.color_id = random.randint(0, len(self.new_circle_images[self.face_id])-1)
        self.simple_circle_sprites.add(SimpleCircle((1 * 1920 / 5, 150), self.new_circle_images[self.face_id][self.color_id]))
        for element in self.new_circle_images:
            element.pop(self.color_id)

        self.face_id = random.randint(0, self.num_faces - 1)
        self.color_id = random.randint(0, len(self.new_circle_images[self.face_id])-1)
        self.simple_circle_sprites.add(SimpleCircle((2 * 1920 / 5, 150), self.new_circle_images[self.face_id][self.color_id]))
        for element in self.new_circle_images:
            element.pop(self.color_id)

        self.face_id = random.randint(0, self.num_faces - 1)
        self.color_id = random.randint(0, len(self.new_circle_images[self.face_id])-1)
        self.simple_circle_sprites.add(SimpleCircle((3 * 1920 / 5, 150), self.new_circle_images[self.face_id][self.color_id]))
        for element in self.new_circle_images:
            element.pop(self.color_id)

        self.face_id = random.randint(0, self.num_faces - 1)
        self.color_id = random.randint(0, len(self.new_circle_images[self.face_id])-1)
        self.simple_circle_sprites.add(SimpleCircle((4 * 1920 / 5, 150), self.new_circle_images[self.face_id][self.color_id]))
        for element in self.new_circle_images:
            element.pop(self.color_id)

        self.face_id = random.randint(0, self.num_faces - 1)
        self.color_id = random.randint(0, len(self.new_circle_images[self.face_id])-1)
        self.simple_circle_sprites.add(SimpleCircle((5 * 1920 / 5, 150), self.new_circle_images[self.face_id][self.color_id]))
        for element in self.new_circle_images:
            element.pop(self.color_id)

        self.face_id = random.randint(0, self.num_faces - 1)
        self.color_id = random.randint(0, len(self.new_circle_images[self.face_id])-1)
        self.simple_circle_sprites.add(SimpleCircle((1 * 1920 / 5, 300), self.new_circle_images[self.face_id][self.color_id]))
        for element in self.new_circle_images:
            element.pop(self.color_id)

        self.face_id = random.randint(0, self.num_faces - 1)
        self.color_id = random.randint(0, len(self.new_circle_images[self.face_id])-1)
        self.simple_circle_sprites.add(SimpleCircle((2 * 1920 / 5, 300), self.new_circle_images[self.face_id][self.color_id]))
        for element in self.new_circle_images:
            element.pop(self.color_id)

        self.face_id = random.randint(0, self.num_faces - 1)
        self.color_id = random.randint(0, len(self.new_circle_images[self.face_id])-1)
        self.simple_circle_sprites.add(SimpleCircle((3 * 1920 / 5, 300), self.new_circle_images[self.face_id][self.color_id]))
        for element in self.new_circle_images:
            element.pop(self.color_id)

        self.face_id = random.randint(0, self.num_faces - 1)
        self.color_id = random.randint(0, len(self.new_circle_images[self.face_id])-1)
        self.simple_circle_sprites.add(SimpleCircle((4 * 1920 / 5, 300), self.new_circle_images[self.face_id][self.color_id]))
        for element in self.new_circle_images:
            element.pop(self.color_id)

        self.face_id = random.randint(0, self.num_faces - 1)
        self.color_id = random.randint(0, len(self.new_circle_images[self.face_id])-1)
        self.simple_circle_sprites.add(SimpleCircle((5 * 1920 / 5, 300), self.new_circle_images[self.face_id][self.color_id]))
        for element in self.new_circle_images:
            element.pop(self.color_id)

    def checkCollisions(self):
        for c1 in self.simple_circle_sprites.sprites():
            for c2 in self.simple_circle_sprites.sprites():
                if c1 == c2:
                    continue

                dist = math.sqrt( (c1.x - c2.x)**2 + (c1.y - c2.y)**2 )
                max_dist = c1.r + c2.r
                
                if dist <= max_dist:
                    self.collide(c1, c2)

    def collide(self, c1, c2):
        c1.x -= c1.vx
        c1.y -= c1.vy
        c2.x -= c2.vx
        c2.y -= c2.vy

        # STEP 1

        [x2, y2] = [c2.x, c2.y]
        [x1, y1] = [c1.x, c1.y]

        norm_vec = np.array([x2 - x1, y2 - y1])

        divisor = math.sqrt(norm_vec[0]**2 + norm_vec[1]**2)
        unit_vec = np.array([norm_vec[0] / divisor, norm_vec[1] / divisor])

        unit_tan_vec = np.array([-1 * unit_vec[1], unit_vec[0]])

        # STEP 2

        v1 = np.array([c1.vx, c1.vy])
        m1 = c1.m

        v2 = np.array([c2.vx, c2.vy])
        m2 = c2.m

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
        c1.setVel(v1p)

        v2p = v2np_ + v2tp_
        c2.setVel(v2p)
