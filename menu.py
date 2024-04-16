import pygame, random, math, numpy as np, asyncio
from pygame.locals import *
from simplecircle import SimpleCircle
from circledata import *
from user import User
from shape import Shape
from clickabletext import ClickableText
from editabletext import EditableText
from menucircle import MenuShape
from powerupdisplaymenu import PowerupDisplayMenu
from localmatchmenu import LocalMatchMenu
from usercollectionmenu import UserCollectionMenu
from createshapemenu import CreateShapeMenu
from networkmatchmenu import NetworkMatchMenu
from registermenu import RegisterMenu

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

class Menu():
    def __init__(self):
        self.user = None
        self.shapes = []
        self.BaseClass = declarative_base()
        self.engine = create_engine("postgresql://postgres:postgres@172.105.8.221/root/shapegame-server-2024/shapegame.db", echo=False)
        # self.BaseClass.metadata.create_all(bind=self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

        self.you_group = pygame.sprite.Group()
        self.new_shapes_group = pygame.sprite.Group()

        self.cursor = pygame.transform.smoothscale(pygame.image.load("backgrounds/cursor.png"), (12, 12))
        self.cursor_rect = self.cursor.get_rect()
        self.cursor_rect.center = pygame.mouse.get_pos()
        # self.screen = pygame.display.set_mode((1920, 1080), pygame.NOFRAME)
        self.screen = pygame.display.set_mode((1920, 1080))
        self.background = pygame.image.load("backgrounds/BG1.png")
        self.title, self.title_rect = self.createText("shapegame", 150)
        self.title_rect.center = (1920 / 2, 1080 / 2)
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font("backgrounds/font.ttf", 80)
        self.game_played = False
        self.stats_surface = 0
        self.exit_clicked = False
        self.frames_since_exit_clicked = 0

        self.click_sound = pygame.mixer.Sound("sounds/click.wav")
        self.start_sound = pygame.mixer.Sound("sounds/start.wav")
        self.open_sound = pygame.mixer.Sound("sounds/open.wav")
        self.menu_music = pygame.mixer.Sound("sounds/menu.wav")
        self.close_sound = pygame.mixer.Sound("sounds/close.wav")

        self.open_sound.set_volume(.5)
        self.menu_music.set_volume(.5)
        self.close_sound.set_volume(.5)
        
        self.open_sound.play()

        

        # pre-define these text elements
        self.logged_in_as = self.logged_in_as_rect = None
        self.shape_tokens_clickable = None
        self.play, self.play_rect = self.createText("play", 100)
        self.play_rect.center = [3 * 1920 / 4, 750]
        self.try_again, self.try_again_rect = self.createText("User not found!", 150)
        self.try_again_rect.center = [1920 / 2, 800]
        self.collections, self.collections_rect = self.createText("collections", 100)
        self.collections_rect.center = [1 * 1920 / 4, 750]
        
  
        self.network_match_clickable = ClickableText("network match", 50, 3 * 1920 / 4 - 200, 875)
        self.local_match_clickable = ClickableText("local match", 50, 3 * 1920 / 4 + 200, 875)
        self.your_shapes_clickable = ClickableText("your shapes", 50, 1 * 1920 / 4 - 250, 875)
        self.all_shapes_clickable = ClickableText("all shapes & powerups", 50, 1 * 1920 / 4 + 250, 875)
        self.exit_clickable = ClickableText("exit", 50, 1870, 1045)
        self.register_clickable = ClickableText("register", 50, 1920 / 2, 1050)

        self.clickables = []
        self.clickables.append(self.network_match_clickable)
        self.clickables.append(self.local_match_clickable)
        self.clickables.append(self.your_shapes_clickable)
        self.clickables.append(self.all_shapes_clickable)
        self.clickables.append(self.exit_clickable)
        self.clickables.append(self.register_clickable)

        self.screen.blit(self.background, (0, 0))
        self.screen.blit(self.title, self.title_rect)
        pygame.display.set_caption("shapegame")
        pygame.display.update()

        self.num_faces = 5

        self.circles = pygame.sprite.Group()

        self.circle_images_full = []
        for i in range(0, 5):
            self.circle_images_full.append([])
            for color in colors:
                self.circle_images_full[i].append(pygame.image.load("circles/{}/{}/0.png".format(i, color[0])))

        self.circle_images = []
        for i in range(0, 5):
            self.circle_images.append([])
            for circle in self.circle_images_full[i]:
                self.circle_images[i].append(pygame.transform.smoothscale(circle, (200, 200)))

        # # Username text input handler
        self.username_editable = EditableText("Username: ", 60, 1920/2, 950)
        self.username_editable.select()

        self.menu_music.play(-1)

    def start(self):
        # Do while loop to get user to sign in
        try_again_flag = False
        while self.user == None:
            events = pygame.event.get()
            keys_pressed = pygame.key.get_pressed()
            mouse_pos = pygame.mouse.get_pos()

            for event in events:
                if event.type == MOUSEBUTTONDOWN and self.exit_clickable.rect.collidepoint(mouse_pos):
                    self.click_sound.play()
                    self.close_sound.play()
                    self.exit_clicked = True
                    pygame.mixer.Sound.fadeout(self.menu_music, 1000)

                if event.type == MOUSEBUTTONDOWN and self.register_clickable.rect.collidepoint(mouse_pos):
                    self.click_sound.play()
                    self.user, self.shapes = RegisterMenu(self.screen, self.session).start()

                    self.logged_in_as, self.logged_in_as_rect = self.createText("logged in as: " + self.user.username, 35)
                    self.logged_in_as_rect.topleft = (10, 1030)

                    self.shape_tokens_clickable = ClickableText("Shape tokens: " + str(self.user.shape_tokens), 35, 1920/2, 1030)

                if event.type == KEYDOWN and event.key == K_RETURN:
                    username = self.username_editable.getText()

                    try:
                        self.user = self.session.query(User).filter(User.username == username).one()
                        print("USER {}".format(self.user))

                        self.logged_in_as, self.logged_in_as_rect = self.createText("logged in as: " + self.user.username, 35)
                        self.logged_in_as_rect.topleft = (10, 1030)

                        self.shape_tokens_clickable = ClickableText("Shape tokens: " + str(self.user.shape_tokens), 35, 1920/2, 1030)

                        self.shapes = self.session.query(Shape).filter(Shape.owner_id == int(self.user.id)).all()

                        # Load your MenuShapes (check if already exists)
                        if len(self.you_group) == 0:
                            counter = 1
                            for shape in self.shapes:
                                self.you_group.add(MenuShape(counter, shape, self.circle_images_full[shape.face_id][shape.color_id], len(self.shapes)))
                                counter += 1
                    except Exception as e:
                        try_again_flag = True
                        print(e)

            # update clickable texts
            self.username_editable.update(events)            

            mouse_pos = pygame.mouse.get_pos()
            for clickable in self.clickables:
                clickable.update(mouse_pos)

            pygame.display.flip()
            self.screen.blit(self.background, (0, 0))
            self.screen.blit(self.title, (1920 / 2 - self.title.get_size()[0] / 2, 1080 / 2 - self.title.get_size()[1] / 2))
            self.screen.blit(self.exit_clickable.surface, self.exit_clickable.rect)
            self.screen.blit(self.register_clickable.surface, self.register_clickable.rect)
            self.cursor_rect.center = pygame.mouse.get_pos()
            self.screen.blit(self.username_editable.surface, self.username_editable.rect)
            self.screen.blit(self.cursor, self.cursor_rect)

            if self.exit_clicked:
                self.frames_since_exit_clicked += 1
                if self.frames_since_exit_clicked == 60:
                    return

            if try_again_flag:
                self.screen.blit(self.try_again, self.try_again_rect)

            self.clock.tick(60)

        # --- USER NOW LOGGED IN ---

        # add to clickable texts
        self.clickables.append(self.shape_tokens_clickable)

        running = True
        while running:
            # Want to have two circles spawn in from opposite sides of the screen and bounce away from each other
            if len(self.circles) == 0:
                self.addNewCircles()

            if self.game_played:
                if self.stats_surface != 0:
                    self.screen.blit(self.stats_surface, (1920 / 2 - self.stats_surface.get_size()[0] / 2, 50)) 
            else:
                self.circles.draw(self.screen)
            self.circles.update()
            self.checkCollisions()

            # Draw some shit
            mouse_pos = pygame.mouse.get_pos()
            for clickable in self.clickables:
                if clickable != None:
                    clickable.update(mouse_pos)

            pygame.display.flip()
            self.screen.blit(self.background, (0, 0))
            self.screen.blit(self.title, (1920 / 2 - self.title.get_size()[0] / 2, 1080 / 2 - self.title.get_size()[1] / 2))
            self.screen.blit(self.play, self.play_rect)
            self.screen.blit(self.network_match_clickable.surface, self.network_match_clickable.rect)
            self.screen.blit(self.local_match_clickable.surface, self.local_match_clickable.rect)
            self.screen.blit(self.collections, self.collections_rect)
            self.screen.blit(self.your_shapes_clickable.surface, self.your_shapes_clickable.rect)
            self.screen.blit(self.all_shapes_clickable.surface, self.all_shapes_clickable.rect)
            self.screen.blit(self.exit_clickable.surface, self.exit_clickable.rect)
            self.screen.blit(self.logged_in_as, self.logged_in_as_rect)
            self.screen.blit(self.shape_tokens_clickable.surface, self.shape_tokens_clickable.rect)

            events = pygame.event.get()
            mouse_pos = pygame.mouse.get_pos()
            for event in events:
                if event.type == MOUSEBUTTONDOWN:
                    self.click_sound.play()
                    if event.button == 1:
                        redirect = "NONE"

                        if self.network_match_clickable.rect.collidepoint(mouse_pos) and self.shapes == []:
                            redirect = CreateShapeMenu(self.screen, self.user, self.shapes, self.session, self.circle_images_full).start()

                            self.shape_tokens_clickable = ClickableText("Shape tokens: " + str(self.user.shape_tokens), 35, 1920/2, 1030)
                            self.clickables.append(self.shape_tokens_clickable)

                        elif self.network_match_clickable.rect.collidepoint(mouse_pos):
                            self.session.commit()

                            # menu = ThreadedNetworkMatchMenu(self.screen, self.user, self.shapes, self.session, self.circle_images_full)
                            # asyncio.run(menu.start())
                            NetworkMatchMenu(self.screen, self.user, self.shapes, self.session, self.circle_images_full).start()

                            self.session.commit()
                            self.shapes = self.session.query(Shape).filter(Shape.owner_id == int(self.user.id)).all()
                            self.you_group.empty()

                            counter = 1
                            for shape in self.shapes:
                                self.you_group.add(MenuShape(counter, shape, self.circle_images_full[shape.face_id][shape.color_id], len(self.shapes)))
                                counter += 1

                        elif self.local_match_clickable.rect.collidepoint(mouse_pos):
                            LocalMatchMenu(self.screen, self.circle_images_full).start()

                        elif self.all_shapes_clickable.rect.collidepoint(mouse_pos):
                            PowerupDisplayMenu(self.screen, self.circle_images_full).start()

                        elif self.shape_tokens_clickable.rect.collidepoint(mouse_pos) and self.user.shape_tokens != 0:
                            redirect = CreateShapeMenu(self.screen, self.user, self.shapes, self.session, self.circle_images_full).start()

                            self.shape_tokens_clickable = ClickableText("Shape tokens: " + str(self.user.shape_tokens), 35, 1920/2, 1030)
                            self.clickables.append(self.shape_tokens_clickable)

                        elif self.your_shapes_clickable.rect.collidepoint(mouse_pos) and self.shapes == []:
                            redirect = CreateShapeMenu(self.screen, self.user, self.shapes, self.session, self.circle_images_full).start()

                            self.shape_tokens_clickable = ClickableText("Shape tokens: " + str(self.user.shape_tokens), 35, 1920/2, 1030)
                            self.clickables.append(self.shape_tokens_clickable)

                        elif self.your_shapes_clickable.rect.collidepoint(mouse_pos):
                            UserCollectionMenu(self.screen, self.circle_images_full, self.shapes, self.user, self.session).start()

                        elif self.exit_clickable.rect.collidepoint(mouse_pos):
                            self.close_sound.play()
                            self.exit_clicked = True
                            pygame.mixer.Sound.fadeout(self.menu_music, 1000)

                        # check if we want to redirect to another menu

                        if redirect != "NONE":
                            if redirect == "COLLECTIONS":
                                UserCollectionMenu(self.screen, self.circle_images_full, self.shapes, self.user, self.session).start()

                if event.type == KEYDOWN:
                    if event.key == 9:
                        self.game_played = not self.game_played

            if self.menu_music.get_num_channels() == 0:
                self.menu_music.play(-1)

            self.cursor_rect.center = pygame.mouse.get_pos()
            self.screen.blit(self.cursor, self.cursor_rect)

            if self.exit_clicked:
                self.frames_since_exit_clicked += 1
                if self.frames_since_exit_clicked == 60:
                    running = False

            # limits FPS to 60
            self.clock.tick(60)
            # print(self.clock.get_fps())

    # HELPERS

    def createText(self, text, size, color = "white"):
        font = pygame.font.Font("backgrounds/font.ttf", size)
        

        if type(text) == type("string"):
            text_surface = font.render(text, True, color)
            text_rect = text_surface.get_rect()

            return text_surface, text_rect
        
        elif type(text) == type(["array"]):
            text_surfaces = []
            for element in text:
                text_surfaces.append(font.render(element, True, color))

            max_line_length = max(surface.get_size()[0] for surface in text_surfaces)
            line_height = text_surfaces[0].get_size()[1]

            surface = pygame.Surface((max_line_length, (len(text_surfaces) + 1) * line_height), pygame.SRCALPHA, 32)

            for i, text_surface in enumerate(text_surfaces):
                surface.blit(text_surface, [max_line_length/2 - text_surface.get_size()[0]/2, line_height * (i+1)])

            return surface, surface.get_rect()
        
    def createShape(self, owner_id = -1):
        # decrement number of shape tokens
        if owner_id != -1:
            self.session.query(User).filter(User.id == self.user.id).update({'shape_tokens': User.shape_tokens -1})
            self.session.commit()

        face_id = random.randint(0, 4)
        color_id = random.randint(0, len(colors)-1)

        base = circles_unchanged[face_id]

        density = base["density"]
        velocity = base["velocity"] + random.randint(-3, 3)
        radius_min = base["radius_min"] + random.randint(-3, 3)
        radius_max = base["radius_max"] + random.randint(-3, 3)
        health = base["health"] + random.randint(-100, 100)
        dmg_multiplier = round(base["dmg_multiplier"] + round((random.randint(-10, 10) / 10), 2), 2)
        luck = round(base["luck"] + round((random.randint(-10, 10) / 10), 2), 2)
        team_size = base["team_size"] + random.randint(-3, 3)

        if owner_id != -1:
            try:
                shape = Shape(owner_id, face_id, color_id, density, velocity, radius_min, radius_max, health, dmg_multiplier, luck, team_size)
                self.session.add(shape)
                self.session.commit()
                return shape
            except:
                self.session.rollback()
                return False
        else:
            shape = Shape(owner_id, face_id, color_id, density, velocity, radius_min, radius_max, health, dmg_multiplier, luck, team_size)
            return shape

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
        self.circles.add(SimpleCircle((1 * 1920 / 5, 150), self.new_circle_images[self.face_id][self.color_id]))
        for element in self.new_circle_images:
            element.pop(self.color_id)

        self.face_id = random.randint(0, self.num_faces - 1)
        self.color_id = random.randint(0, len(self.new_circle_images[self.face_id])-1)
        self.circles.add(SimpleCircle((2 * 1920 / 5, 150), self.new_circle_images[self.face_id][self.color_id]))
        for element in self.new_circle_images:
            element.pop(self.color_id)

        self.face_id = random.randint(0, self.num_faces - 1)
        self.color_id = random.randint(0, len(self.new_circle_images[self.face_id])-1)
        self.circles.add(SimpleCircle((3 * 1920 / 5, 150), self.new_circle_images[self.face_id][self.color_id]))
        for element in self.new_circle_images:
            element.pop(self.color_id)

        self.face_id = random.randint(0, self.num_faces - 1)
        self.color_id = random.randint(0, len(self.new_circle_images[self.face_id])-1)
        self.circles.add(SimpleCircle((4 * 1920 / 5, 150), self.new_circle_images[self.face_id][self.color_id]))
        for element in self.new_circle_images:
            element.pop(self.color_id)

        self.face_id = random.randint(0, self.num_faces - 1)
        self.color_id = random.randint(0, len(self.new_circle_images[self.face_id])-1)
        self.circles.add(SimpleCircle((5 * 1920 / 5, 150), self.new_circle_images[self.face_id][self.color_id]))
        for element in self.new_circle_images:
            element.pop(self.color_id)

        self.face_id = random.randint(0, self.num_faces - 1)
        self.color_id = random.randint(0, len(self.new_circle_images[self.face_id])-1)
        self.circles.add(SimpleCircle((1 * 1920 / 5, 300), self.new_circle_images[self.face_id][self.color_id]))
        for element in self.new_circle_images:
            element.pop(self.color_id)

        self.face_id = random.randint(0, self.num_faces - 1)
        self.color_id = random.randint(0, len(self.new_circle_images[self.face_id])-1)
        self.circles.add(SimpleCircle((2 * 1920 / 5, 300), self.new_circle_images[self.face_id][self.color_id]))
        for element in self.new_circle_images:
            element.pop(self.color_id)

        self.face_id = random.randint(0, self.num_faces - 1)
        self.color_id = random.randint(0, len(self.new_circle_images[self.face_id])-1)
        self.circles.add(SimpleCircle((3 * 1920 / 5, 300), self.new_circle_images[self.face_id][self.color_id]))
        for element in self.new_circle_images:
            element.pop(self.color_id)

        self.face_id = random.randint(0, self.num_faces - 1)
        self.color_id = random.randint(0, len(self.new_circle_images[self.face_id])-1)
        self.circles.add(SimpleCircle((4 * 1920 / 5, 300), self.new_circle_images[self.face_id][self.color_id]))
        for element in self.new_circle_images:
            element.pop(self.color_id)

        self.face_id = random.randint(0, self.num_faces - 1)
        self.color_id = random.randint(0, len(self.new_circle_images[self.face_id])-1)
        self.circles.add(SimpleCircle((5 * 1920 / 5, 300), self.new_circle_images[self.face_id][self.color_id]))
        for element in self.new_circle_images:
            element.pop(self.color_id)

    def checkCollisions(self):
        for c1 in self.circles.sprites():
            for c2 in self.circles.sprites():
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
