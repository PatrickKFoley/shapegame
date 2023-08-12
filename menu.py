import pygame, random, pygame_textinput, math, numpy as np, time
from pygame.locals import *
from simplecircle import SimpleCircle
from game import Game
from network import Network
from circledata import *

class Menu():
    def __init__(self):
        self.network = None

        self.cursor = pygame.transform.scale(pygame.image.load("backgrounds/cursor.png"), (12, 12))
        self.cursor_rect = self.cursor.get_rect()
        self.cursor_rect.center = pygame.mouse.get_pos()
        self.screen = pygame.display.set_mode((1920, 1080), pygame.NOFRAME)
        self.background = pygame.image.load("backgrounds/BG1.png")
        self.title = pygame.image.load("backgrounds/title.png")
        self.title_rect = self.title.get_rect()
        self.title_rect.center = (1920 / 2, 1080 / 2)
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("bahnschrift", 80)
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

        self.play = pygame.image.load("backgrounds/play.png")
        self.play_rect = self.play.get_rect()
        self.play_rect.center = [1920 / 2, 875]

        self.searching = pygame.image.load("backgrounds/searching.png")
        self.searching_rect = self.searching.get_rect()
        self.searching_rect.center = [1920 / 2, 1080 / 2]
        
        self.match_found = pygame.image.load("backgrounds/matchfound.png")
        self.match_found_rect = self.match_found.get_rect()
        self.match_found_rect.center = [1920 / 2, 1080 / 2]

        self.opponent_disconnected = pygame.image.load("backgrounds/opponentdisconnected.png")
        self.opponent_disconnected_rect = self.opponent_disconnected.get_rect()
        self.opponent_disconnected_rect.center = [1920 / 2, 1080 / 2]

        self.you = pygame.image.load("backgrounds/you.png")
        self.you_rect = self.you.get_rect()
        self.you_rect.center = (450, 680)

        self.opponent = pygame.image.load("backgrounds/opponent.png")
        self.opponent_rect = self.opponent.get_rect()
        self.opponent_rect.center = (1470, 680)

        self.ready_red = pygame.image.load("backgrounds/readyred.png")
        self.ready_red_rect = self.ready_red.get_rect()
        self.ready_red_rect.center = (1920 / 2, 1000)

        self.ready_green = pygame.image.load("backgrounds/readygreen.png")
        self.ready_green_rect = self.ready_green.get_rect()
        self.ready_green_rect.center = (1920 / 2, 1000)

        self.simulate = pygame.image.load("backgrounds/simulate.png")
        self.simulate_rect = self.simulate.get_rect()
        self.simulate_rect.center = [1920 / 2, 980]

        self.network_match = pygame.image.load("backgrounds/networkmatch.png")
        self.network_match_rect = self.network_match.get_rect()
        self.network_match_rect.center = [1920 / 2, 725]

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

        self.circle_images = []
        for i in range(0, 5):
            self.circle_images.append([])
            for color in colors:
                self.circle_images[i].append(pygame.transform.scale(pygame.image.load("circles/{}/{}/0.png".format(i, color[0])), (200, 200)))


        self.circle_1 = self.circle_images[self.face_0][self.color_0]
        self.circle_2 = self.circle_images[self.face_1][self.color_1]

        self.arrow_right = pygame.transform.scale(pygame.image.load("backgrounds/arrow_right.png"), (50, 50))
        self.arrow_left = pygame.transform.scale(pygame.image.load("backgrounds/arrow_left.png"), (50, 50))

        self.exit = pygame.image.load("backgrounds/exit.png")
        self.exit_rect = self.exit.get_rect()
        self.exit_rect.center = (1870, 1050)

        self.loading = pygame.image.load("backgrounds/loading.png")
        self.simulating = pygame.image.load("backgrounds/simulating.png")

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

        self.input_manager = pygame_textinput.TextInputManager()
        self.input_manager.value = "Seed (optional)"
        self.input_manager.cursor_pos = len(self.input_manager.value)

        self.seed_input = pygame_textinput.TextInputVisualizer(self.input_manager, pygame.font.SysFont("bahnschrift", 35))
        self.seed_input.font_color = "white"
        self.seed_input.cursor_color = "white"
        self.seed_input.cursor_visible = False
        self.seed_input_rect = self.seed_input.surface.get_rect()
        self.seed_input_rect.center = [1920 / 2, 1050]
        # self.seed_input.value = "Seed (optional)"
        # self.seed_input.cursor_pos = 2

        self.stat_rects = [{}, {}]
        self.menu_music.play(-1)

    def createCircleStatsSurfaces(self):
        surface_0 = pygame.Surface((400, 400), pygame.SRCALPHA, 32)
        surface_1 = pygame.Surface((400, 400), pygame.SRCALPHA, 32)
        font = pygame.font.SysFont("bahnschrift", 30)

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
        for element in keys:
            key_obj = font.render(element, 1, "white")
            key_rect = key_obj.get_rect()
            key_rect.topright = (250, element_count * 30)

            surface_0.blit(key_obj, key_rect)
            element_count += 1

        keys_for_rects = ["density", "velocity", "radius", "health", "dmg_multiplier", "luck"]

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

    def createCircleStatsSurfacesNetwork(self, player_face, opponent_face):
        surface_0 = pygame.Surface((400, 400), pygame.SRCALPHA, 32)
        surface_1 = pygame.Surface((400, 400), pygame.SRCALPHA, 32)
        font = pygame.font.SysFont("bahnschrift", 30)

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

    def show(self):
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
            # self.circles.sprites()[0].update()
            self.checkCollisions()
            # self.circles.sprites()[1].update()


            # Bottom half of screen
            simulate_clicked = False
            play_clicked = False
            self.shown_circles = [[self.face_0, colors[self.color_0][0]], [self.face_1, colors[self.color_1][0]]]

            # Draw some shit
            pygame.display.flip()
            self.screen.blit(self.background, (0, 0))
            self.screen.blit(self.title, (1920 / 2 - self.title.get_size()[0] / 2, 1080 / 2 - self.title.get_size()[1] / 2))
            self.screen.blit(self.play, self.play_rect)
            self.screen.blit(self.exit, self.exit_rect)
            self.screen.blit(self.simulate, self.simulate_rect)
            self.screen.blit(self.network_match, self.network_match_rect)

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

                        if self.network_match_rect.collidepoint(pygame.mouse.get_pos()):
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
                            # play_clicked = True
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
                            # play_clicked = True
                            self.changeCircles()

                        elif self.face_right_0_rect.collidepoint(pygame.mouse.get_pos()):
                            self.face_0 += 1
                            if self.face_0 == self.num_faces: self.face_0 = 0
                            self.changeCircles()

                        elif self.face_left_0_rect.collidepoint(pygame.mouse.get_pos()):
                            self.face_0 -= 1
                            if self.face_0 == -1: self.face_0 = self.num_faces - 1
                            self.changeCircles()

                        elif self.play_rect.collidepoint(pygame.mouse.get_pos()):
                            play_clicked = True

                        elif self.simulate_rect.collidepoint(pygame.mouse.get_pos()):
                            simulate_clicked = True

                        elif self.l_left_rect.collidepoint(pygame.mouse.get_pos()):
                            if self.c0_count != 1: self.c0_count -= 1

                        elif self.l_right_rect.collidepoint(pygame.mouse.get_pos()):
                            if self.c0_count != 20: self.c0_count += 1

                        elif self.r_left_rect.collidepoint(pygame.mouse.get_pos()):
                            if self.c1_count != 1: self.c1_count -= 1

                        elif self.r_right_rect.collidepoint(pygame.mouse.get_pos()):
                            if self.c1_count != 20: self.c1_count += 1

                        elif self.exit_rect.collidepoint(pygame.mouse.get_pos()):
                            self.close_sound.play()
                            self.exit_clicked = True
                            pygame.mixer.Sound.fadeout(self.menu_music, 1000)

                        if unclick_seed_input:
                            self.seed_input_clicked = False
                            self.seed_input.cursor_visible = False

                if event.type == KEYDOWN:
                    if event.key == 9:
                        self.game_played = not self.game_played

            if simulate_clicked:
                self.screen.blit(self.background, (0, 0))
                self.screen.blit(self.simulating, (1920 / 2 - self.simulating.get_size()[0] / 2, 1080 / 2 - self.simulating.get_size()[1] / 2))
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

            if play_clicked:
                self.screen.blit(self.background, (0, 0))
                self.screen.blit(self.loading, (1920 / 2 - self.loading.get_size()[0] / 2, 1080 / 2 - self.loading.get_size()[1] / 2))
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
                self.frames_since_exit_clicked += 1
                if self.frames_since_exit_clicked == 60:
                    running = False

            # limits FPS to 60
            self.clock.tick(60)
            # print(self.clock.get_fps())
    
    def changeCircles(self):
        self.circle_1 = self.circle_images[self.face_0][self.color_0]
        self.circle_2 = self.circle_images[self.face_1][self.color_1]
        self.face_ids = [self.face_0, self.face_1]

        self.c0_count = circles[self.face_0]["team_size"]
        self.c1_count = circles[self.face_1]["team_size"]

    def decodePlayer(self, string):
        tuple = string.split(",")
        return int(tuple[0]), int(tuple[1])

    def encodePlayer(self, tuple):
        return str(tuple[0]) + "," + str(tuple[1])

    def networkPreGame(self):
        self.network = Network()
        player = int(self.network.getPlayer())
        pregame_copy = None
        frames = 0

        self.connecting_flag = True

        if player == 0: opponent = 1
        else: opponent = 0

        face_id = random.randint(0, self.num_faces - 1)
        color_id = random.randint(0, len(colors) - 1)
        
        y_offset = 240

        # create arrows
        color_right = self.arrow_right
        color_right_rect = color_right.get_rect()
        color_right_rect.center = [500, 750 + y_offset]

        color_left = self.arrow_left
        color_left_rect = color_left.get_rect()
        color_left_rect.center = [400, 750 + y_offset]

        face_right = self.arrow_right
        face_right_rect = face_right.get_rect()
        face_right_rect.center = [500, 800 + y_offset]

        face_left = self.arrow_left
        face_left_rect = face_left.get_rect()
        face_left_rect.center = [400, 800 + y_offset]

        player_circle = self.circle_images[0][0]
        player_circle_rect = player_circle.get_rect()
        player_circle_rect.center = (450, 600 + y_offset)

        opponent_circle = self.circle_images[0][0]
        opponent_circle_rect = opponent_circle.get_rect()
        opponent_circle_rect.center = (1470, 600 + y_offset)

        running = True
        ready = False

        pregame = None

        player_stats, opponent_stats = self.createCircleStatsSurfacesNetwork(0, 0)
        player_stats_rect = player_stats.get_rect()
        player_stats_rect.center = (650, 690 + y_offset)
        opponent_stats_rect = opponent_stats.get_rect()
        opponent_stats_rect.center = (1190, 690 + y_offset)

        while running:
            self.clock.tick(60)

            # self.circles.draw(self.screen)
            # self.circles.update()
            # self.checkCollisions()

            try:
                # if frames == 0:
                pregame = self.network.send("GET")

                # if frames % 20 == 0:
                #     pregame = self.network.send("GET")

                while not pregame.ready:
                    pygame.display.flip()
                    self.screen.blit(self.background, (0, 0))
                    self.screen.blit(self.searching, self.searching_rect)
                    self.screen.blit(self.exit, self.exit_rect)

                    self.cursor_rect.center = pygame.mouse.get_pos()
                    self.screen.blit(self.cursor, self.cursor_rect)

                    for event in pygame.event.get():
                        if event.type == MOUSEBUTTONDOWN and self.exit_rect.collidepoint(pygame.mouse.get_pos()):
                            self.network.send("KILL")
                            return

                    pregame = self.network.send("GET")
                    self.clock.tick(60)

            except:
                running = False

                self.screen.blit(self.background, (0, 0))
                self.screen.blit(self.opponent_disconnected, self.opponent_disconnected_rect)
                pygame.display.update()
                time.sleep(0.5)
                break

            if self.connecting_flag:
                self.connecting_flag = False

                self.screen.blit(self.background, (0, 0))
                self.screen.blit(self.match_found, self.match_found_rect)
                pygame.display.update()
                time.sleep(0.5)

            self.network.send("FACE_" + str(face_id))
            self.network.send("COLOR_" + str(color_id))

            for event in pygame.event.get():
                if event.type == MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    self.click_sound.play()

                    if self.exit_rect.collidepoint(mouse_pos):
                        self.exit_clicked = True

                    elif color_right_rect.collidepoint(mouse_pos) and not ready:
                        # if pregame.colors[player] != len(colors) - 1:
                        #     self.network.send("INC_COLOR")

                        color_id += 1
                        if color_id == len(colors): color_id = 0; self.network.send("COLOR_" + str(color_id))


                    elif color_left_rect.collidepoint(mouse_pos) and not ready:
                        # if pregame.colors[player] != 0:
                        #     self.network.send("DEC_COLOR")
                        
                        color_id -= 1
                        if color_id == -1: color_id = len(colors) - 1; self.network.send("COLOR_" + str(color_id))

                    elif face_right_rect.collidepoint(mouse_pos) and not ready:
                        # if pregame.faces[player] != self.num_faces - 1:
                        #     self.network.send("INC_FACE")

                        face_id += 1
                        if face_id == self.num_faces: face_id = 0; self.network.send("FACE_" + str(face_id))

                    elif face_left_rect.collidepoint(mouse_pos) and not ready:
                        # if pregame.faces[player] != 0:
                        #     self.network.send("DEC_FACE")

                        face_id -= 1
                        if face_id == -1: face_id = self.num_faces - 1; self.network.send("FACE_" + str(face_id))

                    elif self.ready_red_rect.collidepoint(mouse_pos):
                        ready = True
                        self.network.send("READY")

            pygame.display.flip()
            self.screen.blit(self.background, (0, 0))
            self.screen.blit(self.title, self.title_rect)  
            self.screen.blit(self.exit, self.exit_rect)

            player_face_id = pregame.faces[player]
            player_color_id = pregame.colors[player]
            opponent_face_id = pregame.faces[opponent]
            opponent_color_id = pregame.colors[opponent]

            player_circle = self.circle_images[player_face_id][player_color_id]
            opponent_circle = self.circle_images[opponent_face_id][opponent_color_id]

            if pregame_copy != None:
                if pregame_copy.faces[opponent] != pregame.faces[opponent] or pregame_copy.colors[opponent] != pregame.colors[opponent] or pregame_copy.faces[player] != pregame.faces[player] or pregame_copy.colors[player] != pregame.colors[player]:
                    player_stats, opponent_stats = self.createCircleStatsSurfacesNetwork(player_face_id, opponent_face_id)

            self.screen.blit(player_circle, player_circle_rect)
            self.screen.blit(opponent_circle, opponent_circle_rect)
            self.screen.blit(player_stats, player_stats_rect)
            self.screen.blit(opponent_stats, opponent_stats_rect)

            self.screen.blit(self.you, self.you_rect)
            self.screen.blit(self.opponent, self.opponent_rect)

            if ready:
                self.screen.blit(self.ready_green, self.ready_green_rect)
            else:
                self.screen.blit(self.ready_red, self.ready_red_rect)

                self.screen.blit(color_right, color_right_rect)
                self.screen.blit(color_left, color_left_rect)
                self.screen.blit(face_right, face_right_rect)
                self.screen.blit(face_left, face_left_rect)

            if self.exit_clicked:
                self.network.send("KILL")
                break

            if pregame.seed != False:
                self.screen.blit(self.background, (0, 0))
                self.screen.blit(self.loading, (1920 / 2 - self.loading.get_size()[0] / 2, 1080 / 2 - self.loading.get_size()[1] / 2))
                pygame.display.update()

                circle_0 = circles_unchanged[player_face_id].copy()
                circle_1 = circles_unchanged[opponent_face_id].copy()

                circle_0["color"] = colors[player_color_id]
                circle_0["group_id"] = 0
                circle_0["face_id"] = player_face_id

                circle_1["color"] = colors[opponent_color_id]
                circle_1["group_id"] = 1
                circle_1["face_id"] = opponent_face_id
                
                real = True
                print("Playing game with seed: {}".format(pregame.seed))
                self.start_sound.play()
                pygame.mixer.Sound.fadeout(self.menu_music, 1000)

                if player == 0:
                    game = Game(circle_0, circle_0["team_size"], circle_1, circle_1["team_size"], self.screen, pregame.seed, real)
                else:
                    circle_0["group_id"] = 1
                    circle_1["group_id"] = 0
                    game = Game(circle_1, circle_1["team_size"], circle_0, circle_0["team_size"], self.screen, pregame.seed, real)
                self.stats_surface = game.play_game()
                self.network.send("KILL")
                break
            
            self.cursor_rect.center = pygame.mouse.get_pos()
            self.screen.blit(self.cursor, self.cursor_rect)

            pregame_copy = pregame   
            frames += 1    
