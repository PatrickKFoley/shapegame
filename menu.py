import pygame, random, pygame_textinput, math, numpy as np, time
from pygame.locals import *
from simplecircle import SimpleCircle
from game import Game
from network import Network
from circledata import *
from user2 import User
from shape import Shape
from clickabletext import ClickableText
from menucircle import MenuShape

from sqlalchemy import create_engine, ForeignKey, Column, String, Integer, CHAR 
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

class Menu():
    def __init__(self):

        self.network = None
        self.user = None
        self.shapes = []

        self.BaseClass = declarative_base()
        self.engine = create_engine("sqlite:///shapegame.db", echo=True)
        self.BaseClass.metadata.create_all(bind=self.engine)

        Session = sessionmaker(bind=self.engine)
        self.session = Session()

        self.collection_group = pygame.sprite.Group()
        self.you_group = pygame.sprite.Group()
        self.opponent_group = pygame.sprite.Group()

        self.cursor = pygame.transform.smoothscale(pygame.image.load("backgrounds/cursor.png"), (12, 12))
        self.cursor_rect = self.cursor.get_rect()
        self.cursor_rect.center = pygame.mouse.get_pos()
        self.screen = pygame.display.set_mode((1920, 1080), pygame.NOFRAME)
        self.background = pygame.image.load("backgrounds/BG1.png")
        self.title, x = self.createText("shapegame", 150)
        self.title_rect = self.title.get_rect()
        self.title_rect.center = (1920 / 2, 1080 / 2)
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font("backgrounds/font.ttf", 80)
        self.game_played = False
        self.stats_surface = 0
        self.connecting_flag = False

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

        self.try_again = pygame.image.load("backgrounds/tryagain.png")
        self.try_again_rect = self.try_again.get_rect()
        self.try_again_rect.center = [1920 / 2, 800]

        self.logged_in_as = self.logged_in_as_rect = None

        self.server_not_found, self.server_not_found_rect = self.createText("server not found", 150)
        self.server_not_found_rect.center = [1920 / 2, 1080 / 2]

        # self.play = pygame.image.load("backgrounds/play.png")
        self.play, self.play_rect = self.createText("play", 100)
        self.play_rect.center = [3 * 1920 / 4, 750]
        
        self.collections, self.collections_rect = self.createText("collections", 100)
        self.collections_rect.center = [1 * 1920 / 4, 750]
        
        self.searching, self.searching_rect = self.createText("searching for opponent...", 150)
        self.searching_rect.center = [1920 / 2, 1080 / 2]
        
        self.match_found, self.match_found_rect = self.createText("match found!", 150)
        self.match_found_rect.center = [1920 / 2, 1080 / 2]
        
        self.opponent_disconnected, self.opponent_disconnected_rect = self.createText("opponent disconnected :()", 150)
        self.opponent_disconnected_rect.center = [1920 / 2, 1080 / 2]
        
        self.you, self.you_rect = self.createText("you", 150)
        self.you_rect.center = (450, 680)

        self.opponent, self.opponent_rect = self.createText("opponent", 150)
        self.opponent_rect.center = (1470, 680)

        self.ready_q, self.ready_q_rect = self.createText("ready?", 150)
        self.ready_q_rect.center = (1920 / 2, 1000)

        self.ready_e, self.ready_e_rect = self.createText("ready!", 150)
        self.ready_e_rect.center = (1920 / 2, 1000)

        self.loading, self.loading_rect = self.createText("loading", 150)
        self.loading_rect.center = [1920 / 2, 1080 / 2]

        self.simulating, self.simulating_rect = self.createText("simulating", 150)
        self.simulating_rect.center = [1920 / 2, 1080 / 2]

        self.network_match_clickable = ClickableText("network match", 50, 3 * 1920 / 4 - 200, 875)
        self.local_match_clickable = ClickableText("local match", 50, 3 * 1920 / 4 + 200, 875)
        self.your_shapes_clickable = ClickableText("your shapes", 50, 1 * 1920 / 4 - 250, 875)
        self.all_shapes_clickable = ClickableText("all shapes & powerups", 50, 1 * 1920 / 4 + 250, 875)
        self.start_clickable = ClickableText("start", 100, 1920 / 2, 750)
        self.simulate_clickable = ClickableText("simulate", 65, 1920 / 2, 850)
        self.exit_clickable = ClickableText("exit", 50, 1870, 1050)

        self.clickables = []
        self.clickables.append(self.network_match_clickable)
        self.clickables.append(self.local_match_clickable)
        self.clickables.append(self.your_shapes_clickable)
        self.clickables.append(self.all_shapes_clickable)
        self.clickables.append(self.start_clickable)
        self.clickables.append(self.simulate_clickable)
        self.clickables.append(self.exit_clickable)

        self.screen.blit(self.background, (0, 0))
        self.screen.blit(self.title, self.title_rect)
        pygame.display.set_caption("shapegame")
        pygame.display.update()

        self.num_faces = 5

        self.face_0 = random.randint(0, self.num_faces - 1)
        self.color_0 = random.randint(0, len(colors)-1)
        self.face_1 = random.randint(0, self.num_faces - 1)
        self.color_1 = random.randint(0, len(colors)-1)

        self.face_ids = [self.face_0, self.face_1]

        self.c0_count = circles[self.face_0]["team_size"]
        self.c1_count = circles[self.face_1]["team_size"]

        self.shown_circles = [[self.face_0, colors[self.color_0][0]], [self.face_1, colors[self.color_1][0]]]

        self.circles = pygame.sprite.Group()

        self.circle_images_full = []
        for i in range(0, 5):
            self.circle_images_full.append([])
            for color in colors:
                self.circle_images_full[i].append(pygame.image.load("circles/{}/{}/0.png".format(i, color[0])))

        self.circle_images_larger = []
        for i in range(0, 5):
            self.circle_images_larger.append([])
            for circle in self.circle_images_full[i]:
                self.circle_images_larger[i].append(pygame.transform.smoothscale(circle, (250, 250)))

        self.circle_images = []
        for i in range(0, 5):
            self.circle_images.append([])
            for circle in self.circle_images_full[i]:
                self.circle_images[i].append(pygame.transform.smoothscale(circle, (200, 200)))


        self.circle_1 = self.circle_images[self.face_0][self.color_0]
        self.circle_2 = self.circle_images[self.face_1][self.color_1]

        self.arrow_right = pygame.transform.smoothscale(pygame.image.load("backgrounds/arrow_right.png"), (50, 50))
        self.arrow_left = pygame.transform.smoothscale(pygame.image.load("backgrounds/arrow_left.png"), (50, 50))


        # draw arrows
        self.color_right_1 = self.arrow_right
        self.color_right_1_rect = self.color_right_1.get_rect()
        self.color_right_1_rect.center = (1920 / 3 + 50, 2 * 1080 / 3 + 230)

        self.color_left_1 = self.arrow_left
        self.color_left_1_rect = self.color_right_1.get_rect()
        self.color_left_1_rect.center = (1920 / 3 - 50, 2 * 1080 / 3 + 230)

        self.face_right_1 = self.arrow_right
        self.face_right_1_rect = self.face_right_1.get_rect()
        self.face_right_1_rect.center = (1920 / 3 + 50, 2 * 1080 / 3 + 270)

        self.face_left_1 = self.arrow_left
        self.face_left_1_rect = self.face_right_1.get_rect()
        self.face_left_1_rect.center = (1920 / 3 - 50, 2 * 1080 / 3 + 270)

        self.color_right_0 = self.arrow_right
        self.color_right_0_rect = self.color_right_0.get_rect()
        self.color_right_0_rect.center = (2 * 1920 / 3 + 50, 2 * 1080 / 3 + 230)

        self.color_left_0 = self.arrow_left
        self.color_left_0_rect = self.color_right_0.get_rect()
        self.color_left_0_rect.center = (2 * 1920 / 3 - 50, 2 * 1080 / 3 + 230)

        self.face_right_0 = self.arrow_right
        self.face_right_0_rect = self.face_right_0.get_rect()
        self.face_right_0_rect.center = (2 * 1920 / 3 + 50, 2 * 1080 / 3 + 270)

        self.face_left_0 = self.arrow_left
        self.face_left_0_rect = self.face_right_0.get_rect()
        self.face_left_0_rect.center = (2 * 1920 / 3 - 50, 2 * 1080 / 3 + 270)


        self.l_count_obj = self.font.render(str(self.c0_count), 1, "white")
        self.l_count_rect = self.l_count_obj.get_rect()
        self.l_count_rect.center = (1920 - 125, 820)
        
        self.l_left = self.arrow_left
        self.l_left_rect = self.l_left.get_rect()
        self.l_left_rect.center = (1920 - 150, 880)

        self.l_right = self.arrow_right
        self.l_right_rect = self.l_right.get_rect()
        self.l_right_rect.center = (1920 - 95, 880)

        self.r_count_obj = self.font.render(str(self.c1_count), 1, "white")
        self.r_count_rect = self.r_count_obj.get_rect()
        self.r_count_rect.center = (125, 820)
        
        self.r_left = self.arrow_left
        self.r_left_rect = self.r_left.get_rect()
        self.r_left_rect.center = (100, 880)

        self.r_right = self.arrow_right
        self.r_right_rect = self.r_right.get_rect()
        self.r_right_rect.center = (150, 880)

        self.seed_input_clicked = False

        self.seed_input_manager = pygame_textinput.TextInputManager()
        self.seed_input_manager.value = "Seed (optional)"
        self.seed_input_manager.cursor_pos = len(self.seed_input_manager.value)

        self.seed_input = pygame_textinput.TextInputVisualizer(self.seed_input_manager, pygame.font.Font("backgrounds/font.ttf", 35))
        self.seed_input.font_color = "white"
        self.seed_input.cursor_color = "white"
        self.seed_input.cursor_visible = False
        self.seed_input_rect = self.seed_input.surface.get_rect()
        self.seed_input_rect.center = [1920 / 2, 1050]

        # Username text input handler
        self.username_input_manager = pygame_textinput.TextInputManager()
        self.username_input_manager.value = "Username: "
        self.username_input_manager.cursor_pos = len(self.username_input_manager.value)

        self.username_input = pygame_textinput.TextInputVisualizer(self.username_input_manager, pygame.font.Font("backgrounds/font.ttf", 50))
        self.username_input.font_color = "white"
        self.username_input.cursor_color = "white"
        self.username_input.cursor_visible = True
        self.username_input_rect = self.username_input.surface.get_rect()
        self.username_input_rect.center = [1920 / 2, 1050]


        # self.seed_input.value = "Seed (optional)"
        # self.seed_input.cursor_pos = 2

        self.stat_rects = [{}, {}]
        self.menu_music.play(-1)

    def createText(self, text, size, color = "white", font_name = "sitkasmallsitkatextbolditalicsitkasubheadingbolditalicsitkaheadingbolditalicsitkadisplaybolditalicsitkabannerbolditalic"):
        font = pygame.font.Font("backgrounds/font.ttf", size)

        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()

        return text_surface, text_rect

    def createCircleStatsSurfaces(self):
        surface_0 = pygame.Surface((400, 400), pygame.SRCALPHA, 32)
        surface_1 = pygame.Surface((400, 400), pygame.SRCALPHA, 32)

        keys = ["Density:", "Velocity:", "Radius:", "Health:", "Damage x:", "Luck:"]
        values_0 = [str(circles[self.face_0]["density"]), str(circles[self.face_0]["velocity"]), 
                    str(circles[self.face_0]["radius_min"]) + " - " + str(circles[self.face_0]["radius_max"]), 
                    str(circles[self.face_0]["health"]), str(circles[self.face_0]["dmg_multiplier"]), 
                    str(circles[self.face_0]["luck"])]
        
        values_1 = [str(circles[self.face_1]["density"]), str(circles[self.face_1]["velocity"]), 
                    str(circles[self.face_1]["radius_min"]) + " - " + str(circles[self.face_1]["radius_max"]), 
                    str(circles[self.face_1]["health"]), str(circles[self.face_1]["dmg_multiplier"]), 
                    str(circles[self.face_1]["luck"])]

        element_count = 0
        font = pygame.font.Font("backgrounds/font.ttf", 35)
        for element in keys:
            key_obj = font.render(element, 1, "white")
            key_rect = key_obj.get_rect()
            key_rect.topright = (250, element_count * 30)

            surface_0.blit(key_obj, key_rect)
            element_count += 1

        keys_for_rects = ["density", "velocity", "radius", "health", "dmg_multiplier", "luck"]

        element_count = 0
        font = pygame.font.Font("backgrounds/font.ttf", 30)
        for element in values_0:
            key_obj = font.render(element, 1, "white")
            key_rect = key_obj.get_rect()
            key_rect.topleft = (270, element_count * 30)

            surface_0.blit(key_obj, key_rect)

            self.stat_rects[0][str(keys_for_rects[element_count])] = key_rect
            element_count += 1

        element_count = 0
        font = pygame.font.Font("backgrounds/font.ttf", 35)
        for element in keys:
            key_obj = font.render(element, 1, "white")
            key_rect = key_obj.get_rect()
            key_rect.topright = (250, element_count * 30)

            surface_1.blit(key_obj, key_rect)
            element_count += 1

        element_count = 0
        font = pygame.font.Font("backgrounds/font.ttf", 30)
        for element in values_1:
            key_obj = font.render(element, 1, "white")
            key_rect = key_obj.get_rect()
            key_rect.topleft = (270, element_count * 30)

            surface_1.blit(key_obj, key_rect)

            self.stat_rects[1][str(keys_for_rects[element_count])] = key_rect
            element_count += 1

        return [surface_0, surface_1]

    def createCircleStatsSurfacesNetwork(self, player_face, opponent_face):
        surface_0 = pygame.Surface((400, 400), pygame.SRCALPHA, 32)
        surface_1 = pygame.Surface((400, 400), pygame.SRCALPHA, 32)
        font = pygame.font.Font("backgrounds/font.ttf", 30)

        keys = ["Density:", "Velocity:", "Radius:", "Health:", "Damage x:", "Luck:", "Team Size:"]
        values_0 = [str(circles_unchanged[player_face]["density"]), str(circles_unchanged[player_face]["velocity"]), 
                    str(circles_unchanged[player_face]["radius_min"]) + " - " + str(circles_unchanged[player_face]["radius_max"]), 
                    str(circles_unchanged[player_face]["health"]), str(circles_unchanged[player_face]["dmg_multiplier"]), 
                    str(circles_unchanged[player_face]["luck"]), str(circles_unchanged[player_face]["team_size"])]
        
        values_1 = [str(circles_unchanged[opponent_face]["density"]), str(circles_unchanged[opponent_face]["velocity"]), 
                    str(circles_unchanged[opponent_face]["radius_min"]) + " - " + str(circles_unchanged[opponent_face]["radius_max"]), 
                    str(circles_unchanged[opponent_face]["health"]), str(circles_unchanged[opponent_face]["dmg_multiplier"]), 
                    str(circles_unchanged[opponent_face]["luck"]), str(circles_unchanged[opponent_face]["team_size"])]

        element_count = 0
        for element in keys:
            key_obj = font.render(element, 1, "white")
            key_rect = key_obj.get_rect()
            key_rect.topright = (250, element_count * 30)

            surface_0.blit(key_obj, key_rect)
            element_count += 1

        keys_for_rects = ["density", "velocity", "radius", "health", "dmg_multiplier", "luck", "team_size"]

        element_count = 0
        for element in values_0:
            key_obj = font.render(element, 1, "white")
            key_rect = key_obj.get_rect()
            key_rect.topleft = (270, element_count * 30)

            surface_0.blit(key_obj, key_rect)

            self.stat_rects[0][str(keys_for_rects[element_count])] = key_rect
            element_count += 1

        element_count = 0
        for element in keys:
            key_obj = font.render(element, 1, "white")
            key_rect = key_obj.get_rect()
            key_rect.topright = (250, element_count * 30)

            surface_1.blit(key_obj, key_rect)
            element_count += 1

        element_count = 0
        for element in values_1:
            key_obj = font.render(element, 1, "white")
            key_rect = key_obj.get_rect()
            key_rect.topleft = (270, element_count * 30)

            surface_1.blit(key_obj, key_rect)

            self.stat_rects[1][str(keys_for_rects[element_count])] = key_rect
            element_count += 1

        return [surface_0, surface_1]

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

    def localPregame(self):
        running = True
        while running:
            # Want to have two circles spawn in from opposite sides of the screen and bounce away from each other
            if len(self.circles) == 0:
                self.addNewCircles()

            if self.game_played:
                if self.stats_surface != 0:
                    self.screen.blit(self.stats_surface, (1920 / 2 - self.stats_surface.get_size()[0] / 2, 25)) 
            else:
                self.circles.draw(self.screen)
            self.circles.update()
            # self.circles.sprites()[0].update()
            self.checkCollisions()
            # self.circles.sprites()[1].update()


            # Bottom half of screen
            simulate_clicked = False
            start_clicked = False
            self.shown_circles = [[self.face_0, colors[self.color_0][0]], [self.face_1, colors[self.color_1][0]]]

            # Draw some shit
            mouse_pos = pygame.mouse.get_pos()
            for clickable in self.clickables:
                clickable.update(mouse_pos)

            pygame.display.flip()
            self.screen.blit(self.background, (0, 0))
            self.screen.blit(self.title, (1920 / 2 - self.title.get_size()[0] / 2, 1080 / 2 - self.title.get_size()[1] / 2))
            self.screen.blit(self.exit_clickable.surface, self.exit_clickable.rect)
            self.screen.blit(self.simulate_clickable.surface, self.simulate_clickable.rect)
            self.screen.blit(self.start_clickable.surface, self.start_clickable.rect)

            # Show two circles 
            self.screen.blit(self.circle_1, (2 * 1920 / 3 - self.circle_1.get_size()[0] / 2, 2 * 1080 / 3))
            self.screen.blit(self.circle_2, (1920 / 3 - self.circle_2.get_size()[0] / 2, 2 * 1080 / 3))


            self.screen.blit(self.color_right_1, self.color_right_1_rect)
            self.screen.blit(self.color_left_1, self.color_left_1_rect)
            self.screen.blit(self.face_right_1, self.face_right_1_rect)
            self.screen.blit(self.face_left_1, self.face_left_1_rect)


            self.screen.blit(self.color_right_0, self.color_right_0_rect)
            self.screen.blit(self.color_left_0, self.color_left_0_rect)
            self.screen.blit(self.face_right_0, self.face_right_0_rect)
            self.screen.blit(self.face_left_0, self.face_left_0_rect)

            [self.surface_0, self.surface_1] = self.createCircleStatsSurfaces()

            self.screen.blit(self.surface_0, (1300, 735))
            self.screen.blit(self.surface_1, (150, 735))

            # pygame.draw.rect(self.screen, "white", (-10, -10, 1940, 410), 2)
            self.l_count_obj = self.font.render(str(self.c0_count), 1, "white")
            self.l_count_rect = self.l_count_obj.get_rect()
            self.l_count_rect.center = (1920 - 125, 820)

            self.r_count_obj = self.font.render(str(self.c1_count), 1, "white")
            self.r_count_rect = self.r_count_obj.get_rect()
            self.r_count_rect.center = (125, 820)

            # draw counts + arrows
            self.screen.blit(self.l_count_obj, self.l_count_rect)
            self.screen.blit(self.l_left, self.l_left_rect)
            self.screen.blit(self.l_right, self.l_right_rect)

            self.screen.blit(self.r_count_obj, self.r_count_rect)
            self.screen.blit(self.r_left, self.r_left_rect)
            self.screen.blit(self.r_right, self.r_right_rect)

            events = pygame.event.get()

            if self.seed_input_clicked: self.seed_input.update(events); self.seed_input_rect = self.seed_input.surface.get_rect(); self.seed_input_rect.center = [1920 / 2, 1000]

            self.screen.blit(self.seed_input.surface, self.seed_input_rect)

            for event in events:
                if event.type == MOUSEBUTTONDOWN:
                    self.click_sound.play()
                    if event.button == 1:
                        # loop through stats rects and check if any of them got clicked?
                        for key, item in self.stat_rects[0].items():
                            if item.collidepoint((pygame.mouse.get_pos()[0]-1300, pygame.mouse.get_pos()[1]-735)):

                                amount = 1
                                pressed_keys = pygame.key.get_pressed()
                                counter = 0
                                for pressed_key in pressed_keys:
                                    if pressed_key == 1 and counter == 225:
                                        amount *= 10
                                    if pressed_key == 1 and counter == 224:
                                        amount *= -1
                                    counter += 1

                                if key == "radius":
                                    circles[self.face_ids[0]]["radius_min"] += amount
                                    circles[self.face_ids[0]]["radius_max"] += amount

                                    if circles[self.face_ids[0]]["radius_max"] > maxes["radius"]:
                                        circles[self.face_ids[0]]["radius_max"] = maxes["radius"]
                                        circles[self.face_ids[0]]["radius_min"] = maxes["radius"] - 10

                                    if circles[self.face_ids[0]]["radius_min"] < mins["radius"]:
                                        circles[self.face_ids[0]]["radius_max"] = mins["radius"]
                                        circles[self.face_ids[0]]["radius_min"] = mins["radius"] - 10
                                else:
                                    if key == "dmg_multiplier" or key == "luck":
                                        amount *= 0.1

                                    circles[self.face_ids[0]][key] = round(amount + circles[self.face_ids[0]][key], 1)

                                    if circles[self.face_ids[0]][key] > maxes[key]:
                                        circles[self.face_ids[0]][key] = maxes[key]

                                    if circles[self.face_ids[0]][key] < mins[key]:
                                        circles[self.face_ids[0]][key] = mins[key]
                                
                                [self.surface_0, self.surface_1] = self.createCircleStatsSurfaces()
                        for key, item in self.stat_rects[1].items():
                            if item.collidepoint((pygame.mouse.get_pos()[0]-150, pygame.mouse.get_pos()[1]-735)):

                                amount = 1
                                pressed_keys = pygame.key.get_pressed()
                                counter = 0
                                for pressed_key in pressed_keys:
                                    if pressed_key == 1 and counter == 225:
                                        amount *= 10
                                    if pressed_key == 1 and counter == 224:
                                        amount *= -1
                                    counter += 1

                                if key == "radius":
                                    circles[self.face_ids[1]]["radius_min"] += amount
                                    circles[self.face_ids[1]]["radius_max"] += amount

                                    if circles[self.face_ids[1]]["radius_max"] > maxes["radius"]:
                                        circles[self.face_ids[1]]["radius_max"] = maxes["radius"]
                                        circles[self.face_ids[1]]["radius_min"] = maxes["radius"] - 10

                                    if circles[self.face_ids[1]]["radius_min"] < mins["radius"]:
                                        circles[self.face_ids[1]]["radius_max"] = mins["radius"]
                                        circles[self.face_ids[1]]["radius_min"] = mins["radius"] - 1
                                else:
                                    if key == "dmg_multiplier" or key == "luck":
                                        amount *= 0.1

                                    circles[self.face_ids[1]][key] = round(amount + circles[self.face_ids[1]][key], 1)

                                    if circles[self.face_ids[1]][key] > maxes[key]:
                                        circles[self.face_ids[1]][key] = maxes[key]

                                    if circles[self.face_ids[1]][key] < mins[key]:
                                        circles[self.face_ids[1]][key] = mins[key]
                                
                                [self.surface_0, self.surface_1] = self.createCircleStatsSurfaces()

                        unclick_seed_input = True

                        if self.network_match_clickable.rect.collidepoint(pygame.mouse.get_pos()):
                            self.networkPreGame()
                            self.exit_clicked = False

                        elif self.seed_input_rect.collidepoint(pygame.mouse.get_pos()):
                            self.seed_input_clicked = True
                            self.seed_input.cursor_visible = True
                            unclick_seed_input = False

                        elif self.color_right_1_rect.collidepoint(pygame.mouse.get_pos()):
                            self.color_1 += 1
                            if self.color_1 == len(colors): self.color_1 = 0
                            self.changeCircles()

                        elif self.color_left_1_rect.collidepoint(pygame.mouse.get_pos()):
                            self.color_1 -= 1
                            if self.color_1 == -1: self.color_1 = len(colors) - 1
                            # start_clicked = True
                            self.changeCircles()

                        elif self.face_right_1_rect.collidepoint(pygame.mouse.get_pos()):
                            self.face_1 += 1
                            if self.face_1 == self.num_faces: self.face_1 = 0
                            self.changeCircles()

                        elif self.face_left_1_rect.collidepoint(pygame.mouse.get_pos()):
                            self.face_1 -= 1
                            if self.face_1 == -1: self.face_1 = self.num_faces - 1
                            self.changeCircles()

                        elif self.color_right_0_rect.collidepoint(pygame.mouse.get_pos()):
                            self.color_0 += 1
                            if self.color_0 == len(colors): self.color_0 = 0
                            self.changeCircles()

                        elif self.color_left_0_rect.collidepoint(pygame.mouse.get_pos()):
                            self.color_0 -= 1
                            if self.color_0 == -1: self.color_0 = len(colors) - 1
                            # start_clicked = True
                            self.changeCircles()

                        elif self.face_right_0_rect.collidepoint(pygame.mouse.get_pos()):
                            self.face_0 += 1
                            if self.face_0 == self.num_faces: self.face_0 = 0
                            self.changeCircles()

                        elif self.face_left_0_rect.collidepoint(pygame.mouse.get_pos()):
                            self.face_0 -= 1
                            if self.face_0 == -1: self.face_0 = self.num_faces - 1
                            self.changeCircles()

                        elif self.start_clickable.rect.collidepoint(pygame.mouse.get_pos()):
                            start_clicked = True

                        elif self.simulate_clickable.rect.collidepoint(pygame.mouse.get_pos()):
                            simulate_clicked = True

                        elif self.l_left_rect.collidepoint(pygame.mouse.get_pos()):
                            if self.c0_count != 1: self.c0_count -= 1

                        elif self.l_right_rect.collidepoint(pygame.mouse.get_pos()):
                            if self.c0_count != 20: self.c0_count += 1

                        elif self.r_left_rect.collidepoint(pygame.mouse.get_pos()):
                            if self.c1_count != 1: self.c1_count -= 1

                        elif self.r_right_rect.collidepoint(pygame.mouse.get_pos()):
                            if self.c1_count != 20: self.c1_count += 1

                        elif self.exit_clickable.rect.collidepoint(pygame.mouse.get_pos()):
                            self.close_sound.play()
                            return

                        if unclick_seed_input:
                            self.seed_input_clicked = False
                            self.seed_input.cursor_visible = False

                if event.type == KEYDOWN:
                    if event.key == 9:
                        self.game_played = not self.game_played

            if simulate_clicked:
                self.screen.blit(self.background, (0, 0))
                self.screen.blit(self.simulating, self.simulating_rect)
                pygame.display.update()

                circle_0 = circles[self.face_0].copy()
                circle_1 = circles[self.face_1].copy()

                circle_0["color"] = colors[self.color_0]
                circle_0["group_id"] = 0
                circle_0["face_id"] = self.face_0

                circle_1["color"] = colors[self.color_1]
                circle_1["group_id"] = 1
                circle_1["face_id"] = self.face_1

                seed = self.seed_input.value
                if seed == "Seed (optional)":
                    seed = False

                real = False
                print("Simulating game with seed: {}".format(seed))
                self.start_sound.play()
                pygame.mixer.Sound.fadeout(self.menu_music, 1000)
                game = Game(circle_0, self.c0_count, circle_1, self.c1_count, self.screen, seed, real)
                self.stats_surface = game.play_game()
                self.game_played = True

            if start_clicked:
                self.screen.blit(self.background, (0, 0))
                self.screen.blit(self.loading, self.loading_rect)
                pygame.display.update()

                circle_0 = circles[self.face_0].copy()
                circle_1 = circles[self.face_1].copy()

                circle_0["color"] = colors[self.color_0]
                circle_0["group_id"] = 0
                circle_0["face_id"] = self.face_0

                circle_1["color"] = colors[self.color_1]
                circle_1["group_id"] = 1
                circle_1["face_id"] = self.face_1

                seed = self.seed_input.value
                if seed == "Seed (optional)":
                    seed = False
                
                real = True
                print("Playing game with seed: {}".format(seed))
                self.start_sound.play()
                pygame.mixer.Sound.fadeout(self.menu_music, 1000)
                game = Game(circle_0, self.c0_count, circle_1, self.c1_count, self.screen, seed, real, True)
                self.stats_surface = game.play_game()
                self.game_played = True

            if self.menu_music.get_num_channels() == 0:
                self.menu_music.play(-1)

            self.cursor_rect.center = pygame.mouse.get_pos()
            self.screen.blit(self.cursor, self.cursor_rect)

            if self.exit_clicked:
                running = False

            # limits FPS to 60
            self.clock.tick(60)
            # print(self.clock.get_fps())

    def start(self):
        # Do while loop to get user to sign in
        try_again_flag = False
        while self.user == None:
            events = pygame.event.get()
            keys_pressed = pygame.key.get_pressed()

            for event in events:
                if event.type == MOUSEBUTTONDOWN and self.exit_clickable.rect.collidepoint(pygame.mouse.get_pos()):
                    self.close_sound.play()
                    self.exit_clicked = True
                    pygame.mixer.Sound.fadeout(self.menu_music, 1000)

                if event.type == KEYDOWN and event.key == K_BACKSPACE and keys_pressed[K_LCTRL]:
                    self.username_input.value = ""

                if event.type == KEYDOWN and event.key == K_RETURN:
                    username = self.username_input.value
                    if username[:9] == "Username:": username = username[10:].lower()

                    try:
                        self.user = self.session.query(User).filter(User.username == username).one()
                        print(self.user)

                        self.logged_in_as, self.logged_in_as_rect = self.createText("logged in as: " + self.user.username, 35)
                        self.logged_in_as_rect.topleft = (10, 1030)

                        self.shapes = self.session.query(Shape).filter(Shape.owner_id == int(self.user.id)).all()

                        # Load your MenuShapes (check if already exists)
                        if len(self.you_group) == 0:
                            counter = 1
                            for shape in self.shapes:
                                self.you_group.add(MenuShape(counter, shape, len(self.shapes)))
                                counter += 1
                    except:
                        try_again_flag = True

            pygame.display.flip()
            self.screen.blit(self.background, (0, 0))
            self.screen.blit(self.title, (1920 / 2 - self.title.get_size()[0] / 2, 1080 / 2 - self.title.get_size()[1] / 2))
            self.screen.blit(self.exit_clickable.surface, self.exit_clickable.rect)
            self.cursor_rect.center = pygame.mouse.get_pos()
            self.screen.blit(self.cursor, self.cursor_rect)

            self.username_input.update(events); 
            self.username_input_rect = self.username_input.surface.get_rect(); 
            self.username_input_rect.center = [1920 / 2, 1000]
            self.screen.blit(self.username_input.surface, self.username_input_rect)

            if self.exit_clicked:
                self.frames_since_exit_clicked += 1
                if self.frames_since_exit_clicked == 60:
                    return

            if try_again_flag:
                self.screen.blit(self.try_again, self.try_again_rect)

            self.clock.tick(60)

        # move rects
        # self.play_rect.center = [2 * 1920/ 3, 2 * 1080 / 3]

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

            events = pygame.event.get()
            for event in events:
                if event.type == MOUSEBUTTONDOWN:
                    self.click_sound.play()
                    if event.button == 1:
                        if self.network_match_clickable.rect.collidepoint(pygame.mouse.get_pos()):
                            self.networkPreGame()
                            self.exit_clicked = False

                        elif self.local_match_clickable.rect.collidepoint(pygame.mouse.get_pos()):
                            self.localPregame()
                            self.exit_clicked = False

                        elif self.your_shapes_clickable.rect.collidepoint(pygame.mouse.get_pos()):
                            self.userCollection()

                        elif self.exit_clickable.rect.collidepoint(pygame.mouse.get_pos()):
                            self.close_sound.play()
                            self.exit_clicked = True
                            pygame.mixer.Sound.fadeout(self.menu_music, 1000)

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
    
    def userCollection(self):
        selected_shape = 0

        # if len(self.collection_group) == 0:
        text_surface, text_rect = self.createText("loading your shapes", 100)
        text_rect.center = [1920 / 2, 1080 / 2]

        self.screen.blit(self.background, (0, 0))
        self.screen.blit(text_surface, text_rect)
        pygame.display.update()
        self.collection_group.empty()

        counter = 1
        for shape in self.shapes:
            self.collection_group.add(MenuShape(counter, shape, len(self.shapes), "COLLECTIONS"))
            counter += 1

        if len(self.shapes) >= 5:
            selected_shape = 3
        elif len(self.shapes) == 4:
            selected_shape = 3
        elif len(self.shapes) == 3:
            selected_shape = 2
        elif len(self.shapes) == 2:
            selected_shape = 2
        else:
            selected_shape = 1

        counter = 0
        for shape in self.collection_group.sprites():
            counter += 1
            if counter == selected_shape:
                shape.toggleSelected()
            
        l_arrow = pygame.transform.smoothscale(pygame.image.load("backgrounds/arrow_left.png"), (75, 50))
        l_arrow_rect = l_arrow.get_rect()
        l_arrow_rect.center = [1920 / 2 - 50, 700]

        r_arrow = pygame.transform.smoothscale(pygame.image.load("backgrounds/arrow_right.png"), (75, 50))
        r_arrow_rect = r_arrow.get_rect()
        r_arrow_rect.center = [1920 / 2 + 50, 700]

        running = True
        while running:
            mouse_pos = pygame.mouse.get_pos()
            for clickable in self.clickables:
                clickable.update(mouse_pos)

            events = pygame.event.get()
            for event in events:
                if event.type == MOUSEBUTTONDOWN:
                    self.click_sound.play()

                    if self.exit_clickable.rect.collidepoint(mouse_pos):
                        self.close_sound.play()
                        running = False
                    
                    elif l_arrow_rect.collidepoint(mouse_pos) or r_arrow_rect.collidepoint(mouse_pos):
                        if l_arrow_rect.collidepoint(mouse_pos):
                            if selected_shape != 1:
                                selected_shape -= 1
                                for shape in self.collection_group.sprites():
                                    if len(self.shapes) >= 6:
                                        shape.moveRight()

                        elif r_arrow_rect.collidepoint(mouse_pos):
                            if selected_shape != len(self.shapes):
                                selected_shape += 1
                                for shape in self.collection_group.sprites():
                                    counter += 1
                                    if len(self.shapes) >= 6:
                                        shape.moveLeft()

                        counter = 0
                        for shape in self.collection_group.sprites():
                            counter += 1
                            if counter == selected_shape:
                                shape.select()
                            else:
                                shape.disable()


            self.collection_group.draw(self.screen)
            self.collection_group.update(self.screen) 

            pygame.display.flip()
            

            self.screen.blit(self.background, (0, 0))
            self.screen.blit(self.title, (1920 / 2 - self.title.get_size()[0] / 2, 1080 / 5 - self.title.get_size()[1] / 2))
            self.screen.blit(self.exit_clickable.surface, self.exit_clickable.rect)

            self.screen.blit(l_arrow, l_arrow_rect)
            self.screen.blit(r_arrow, r_arrow_rect)

            self.cursor_rect.center = pygame.mouse.get_pos()
            self.screen.blit(self.cursor, self.cursor_rect)

            self.clock.tick(60)

        # self.collection_group.empty()
        for shape in self.collection_group.sprites():
            shape.goHome()
            shape.disable()

    def changeCircles(self):
        self.circle_1 = self.circle_images[self.face_0][self.color_0]
        self.circle_2 = self.circle_images[self.face_1][self.color_1]
        self.face_ids = [self.face_0, self.face_1]

        self.c0_count = circles[self.face_0]["team_size"]
        self.c1_count = circles[self.face_1]["team_size"]

    def networkPreGame(self):
        self.network = Network()
        player_id = self.network.getPlayer()

        # Check for server (probably can be done better)
        if player_id != None: 
            player_id = int(player_id)
        else:
            frames = 0
            while frames <= 120:
                self.screen.blit(self.background, (0, 0))
                self.screen.blit(self.server_not_found, self.server_not_found_rect)
                pygame.display.update()


                frames += 1
                self.clock.tick(60)
            return
        
        # Check who you are
        if player_id == 0: opponent = 1
        else: opponent = 0

        # Send your user_id to the server
        self.network.send("USER_" + str(self.user.id))

        # Determine who you have selected
        you_selected = 0
        if len(self.shapes) >= 5:
            you_selected = 3
        elif len(self.shapes) == 4:
            you_selected = 3
        elif len(self.shapes) == 3:
            you_selected = 2
        elif len(self.shapes) == 2:
            you_selected = 2
        else:
            you_selected = 1

        self.network.send("SELECTED_" + str(you_selected))
        time.sleep(0.5)

        # Retrieve opponent user id and query for their shapes
        pregame = self.network.send("GET")
        opponent_shapes = self.session.query(Shape).filter(Shape.owner_id == int(pregame.user_ids[opponent])).all()

        while opponent_shapes == []:
            pygame.display.flip()
            self.screen.blit(self.background, (0, 0))
            self.screen.blit(self.searching, self.searching_rect)
            self.screen.blit(self.exit_clickable.surface, self.exit_clickable.rect)

            # self.cursor_rect.center = pygame.mouse.get_pos()
            # self.screen.blit(self.cursor, self.cursor_rect)

            for event in pygame.event.get():
                if event.type == MOUSEBUTTONDOWN and self.exit_clickable.rect.collidepoint(pygame.mouse.get_pos()):
                    self.network.send("KILL")
                    return

            pregame = self.network.send("GET")
            opponent_shapes = self.session.query(Shape).filter(Shape.owner_id == int(pregame.user_ids[opponent])).all()
            self.clock.tick(2)

        # -- Load opponent --
        self.opponent_group.empty()
        text_surface, text_rect = self.createText("loading your shapes", 100)
        text_rect.center = [1920 / 2, 1080 / 2]
        self.screen.blit(self.background, (0, 0))
        self.screen.blit(text_surface, text_rect)
        pygame.display.update()

        counter = 1
        for shape in opponent_shapes:
            self.opponent_group.add(MenuShape(counter, shape, len(opponent_shapes), "OPPONENT"))
            counter += 1

        # Determine opponents selected shape
        opponent_selected = 0
        if len(opponent_shapes) >= 5:
            opponent_selected = 3
        elif len(opponent_shapes) == 4:
            opponent_selected = 3
        elif len(opponent_shapes) == 3:
            opponent_selected = 2
        elif len(opponent_shapes) == 2:
            opponent_selected = 2
        else:
            opponent_selected = 1

        counter = 0
        for shape in self.opponent_group.sprites():
            counter += 1
            if counter == opponent_selected:
                shape.select()
            else:
                shape.disable()

        counter = 0
        for shape in self.you_group.sprites():
            counter += 1
            if counter == you_selected:
                shape.select()
            else:
                shape.disable()

        # create arrows
        right_surface = pygame.transform.smoothscale(pygame.image.load("backgrounds/arrow_right.png"), (75, 50))
        right_rect = right_surface.get_rect()
        right_rect.center = [1920 / 2 + 50, 800]

        left_surface = pygame.transform.smoothscale(pygame.image.load("backgrounds/arrow_left.png"), (75, 50))
        left_rect = left_surface.get_rect()
        left_rect.center = [1920 / 2 - 50, 800]

        print(you_selected, opponent_selected)

        # other things
        pregame_copy = None
        frames = 0
        self.connecting_flag = True
        running = True
        ready = False

        opponent_user = self.session.query(User).filter(User.id == int(pregame.user_ids[opponent])).one()
        opponent_username_surface, opponent_username_rect = self.createText(opponent_user.username, 100)
        opponent_username_rect.center = [1920 / 2 + 500 + 50, 750]

        you_username_surface, you_username_rect = self.createText(self.user.username, 100)
        you_username_rect.center = [1920 / 2 - 500 + 50, 750]

        while running:
            self.clock.tick(60)

            mouse_pos = pygame.mouse.get_pos()
            for clickable in self.clickables:
                clickable.update(mouse_pos)

            try:
                pregame = self.network.send("GET")

                while not pregame.ready:
                    pygame.display.flip()
                    self.screen.blit(self.background, (0, 0))
                    self.screen.blit(self.searching, self.searching_rect)
                    self.screen.blit(self.exit_clickable.surface, self.exit_clickable.rect)

                    self.cursor_rect.center = pygame.mouse.get_pos()
                    self.screen.blit(self.cursor, self.cursor_rect)

                    for event in pygame.event.get():
                        if event.type == MOUSEBUTTONDOWN:
                            if self.exit_clickable.rect.collidepoint(mouse_pos):
                                self.network.send("KILL")
                                return


                    pregame = self.network.send("GET")
                    self.clock.tick(60)

            except:
                running = False

                self.screen.blit(self.background, (0, 0))
                self.screen.blit(self.opponent_disconnected, self.opponent_disconnected_rect)
                pygame.display.update()

                self.opponent_group.empty()
                for shape in self.you_group.sprites():
                    shape.goHome()
                    shape.disable()

                time.sleep(0.5)
                break

            if self.connecting_flag:
                self.connecting_flag = False

                self.screen.blit(self.background, (0, 0))
                self.screen.blit(self.match_found, self.match_found_rect)
                pygame.display.update()
                time.sleep(0.5)

            for event in pygame.event.get():
                if event.type == MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    self.click_sound.play()

                    if self.exit_clickable.rect.collidepoint(mouse_pos):
                        self.exit_clicked = True

                    elif self.ready_q_rect.collidepoint(mouse_pos):
                        ready = True
                        self.network.send("READY")

                    elif right_rect.collidepoint(mouse_pos) or left_rect.collidepoint(mouse_pos):
                        if left_rect.collidepoint(mouse_pos):
                            # Check if selected shape in bounds
                            if you_selected != 1:
                                you_selected -= 1
                                self.network.send("SELECTED_" + str(you_selected))

                                if len(self.shapes) >= 6:
                                    for shape in self.you_group.sprites():
                                        shape.moveRight()

                        elif right_rect.collidepoint(mouse_pos):
                            if you_selected != len(self.shapes):
                                you_selected += 1
                                self.network.send("SELECTED_" + str(you_selected))

                                if len(self.shapes) >= 6:
                                    for shape in self.you_group.sprites():
                                        shape.moveLeft()

                        counter = 0
                        for shape in self.you_group.sprites():
                            counter += 1
                            if counter == you_selected:
                                shape.select()
                            else:
                                shape.disable()

            # Check if your record of the opponent selected shape matches with server
            if opponent_selected != pregame.users_selected[opponent]:
                if opponent_selected < pregame.users_selected[opponent]:
                    opponent_selected += 1
                    for opponent_shape in self.opponent_group.sprites():
                        opponent_shape.moveLeft()

                else:
                    opponent_selected -= 1
                    for opponent_shape in self.opponent_group.sprites():
                            opponent_shape.moveRight()

                counter = 0
                for shape in self.opponent_group.sprites():
                    counter += 1
                    if counter == opponent_selected:
                        shape.select()
                    else:
                        shape.disable()

            self.you_group.draw(self.screen)
            self.you_group.update(self.screen)

            self.opponent_group.draw(self.screen)
            self.opponent_group.update(self.screen)

            pygame.display.flip()
            self.screen.blit(self.background, (0, 0))
            self.screen.blit(self.title, (1920 / 2 - self.title.get_size()[0] / 2, 50))  
            self.screen.blit(self.exit_clickable.surface, self.exit_clickable.rect)
            self.screen.blit(left_surface, left_rect)
            self.screen.blit(right_surface, right_rect)
            self.screen.blit(you_username_surface, you_username_rect)
            self.screen.blit(opponent_username_surface, opponent_username_rect)

            if not ready: self.screen.blit(self.ready_q, self.ready_q_rect)
            else: self.screen.blit(self.ready_e, self.ready_e_rect)


            if self.exit_clicked:
                self.network.send("KILL")

                self.opponent_group.empty()
                for shape in self.you_group.sprites():
                    shape.goHome()
                    shape.disable()

                break

            if pregame.seed != False:
                self.screen.blit(self.background, (0, 0))
                self.screen.blit(self.loading, (1920 / 2 - self.loading.get_size()[0] / 2, 1080 / 2 - self.loading.get_size()[1] / 2))
                pygame.display.update()


                your_circle = {}
                your_shape = self.shapes[you_selected]
                their_circle = {}
                their_shape = opponent_shapes[opponent_selected]

                your_circle["circle_id"] = 0
                your_circle["face_id"] = your_shape.face_id
                your_circle["color"] = colors[your_shape.color_id]
                your_circle["density"] = your_shape.density
                your_circle["velocity"] = your_shape.velocity
                your_circle["radius_min"] = your_shape.radius_min
                your_circle["radius_max"] = your_shape.radius_max
                your_circle["health"] = your_shape.health
                your_circle["dmg_multiplier"] = your_shape.dmg_multiplier
                your_circle["luck"] = your_shape.luck
                your_circle["team_size"] = your_shape.team_size

                their_circle["circle_id"] = 0
                their_circle["face_id"] = their_shape.face_id
                their_circle["color"] = colors[their_shape.color_id]
                their_circle["density"] = their_shape.density
                their_circle["velocity"] = their_shape.velocity
                their_circle["radius_min"] = their_shape.radius_min
                their_circle["radius_max"] = their_shape.radius_max
                their_circle["health"] = their_shape.health
                their_circle["dmg_multiplier"] = their_shape.dmg_multiplier
                their_circle["luck"] = their_shape.luck
                their_circle["team_size"] = their_shape.team_size
            
                
                real = True
                print("Playing game with seed: {}".format(pregame.seed))
                self.start_sound.play()
                pygame.mixer.Sound.fadeout(self.menu_music, 1000)

                if player_id == 0:
                    your_circle["group_id"] = 0
                    their_circle["group_id"] = 1
                    game = Game(your_circle, your_circle["team_size"], their_circle, their_circle["team_size"], self.screen, pregame.seed, real)
                else:
                    your_circle["group_id"] = 1
                    their_circle["group_id"] = 0
                    game = Game(their_circle, their_circle["team_size"], your_circle, your_circle["team_size"], self.screen, pregame.seed, real)
                self.stats_surface = game.play_game()
                self.network.send("KILL")
                break
            
            self.cursor_rect.center = pygame.mouse.get_pos()
            self.screen.blit(self.cursor, self.cursor_rect)
            frames += 1    

        for shape in self.you_group.sprites():
            shape.goHome()
            shape.disable()