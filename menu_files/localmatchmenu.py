import pygame, random, pygame_textinput, math, numpy as np
from pygame.locals import *
from menu_files.main_menu_files.simplecircle import SimpleCircle
from game_files.game import Game
from game_files.game2 import Game2
from game_files.circledata import *
from screen_elements.clickabletext import ClickableText
from screen_elements.arrow import Arrow
from createdb import User, Shape as DbShape

class LocalMatchMenu():
    def __init__(self, screen, circle_images_full):

        self.screen = screen

        self.cursor = pygame.transform.smoothscale(pygame.image.load("backgrounds/cursor.png"), (12, 12))
        self.cursor_rect = self.cursor.get_rect()
        self.cursor_rect.center = pygame.mouse.get_pos()
        self.background = pygame.image.load("backgrounds/BG1.png")
        self.title, x = self.createText("shapegame", 150)
        self.title_rect = self.title.get_rect()
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
        

        self.try_again, self.try_again_rect = self.createText("User not found!", 150)
        self.try_again_rect.center = [1920 / 2, 800]

        # pre-define these text elements
        self.logged_in_as = self.logged_in_as_rect = None
        self.shape_tokens_clickable = None

        self.server_not_found, self.server_not_found_rect = self.createText("server not found", 150)
        self.server_not_found_rect.center = [1920 / 2, 1080 / 2]



        self.loading, self.loading_rect = self.createText("loading", 150)
        self.loading_rect.center = [1920 / 2, 1080 / 2]

        self.simulating, self.simulating_rect = self.createText("simulating", 150)
        self.simulating_rect.center = [1920 / 2, 1080 / 2]

        self.start_clickable = ClickableText("start", 100, 1920 / 2, 750)
        self.simulate_clickable = ClickableText("simulate", 65, 1920 / 2, 850)
        self.exit_clickable = ClickableText("back", 50, 1870, 1045)

        self.clickables = []
        self.clickables.append(self.start_clickable)
        self.clickables.append(self.simulate_clickable)
        self.clickables.append(self.exit_clickable)

        self.screen.blit(self.background, (0, 0))
        self.screen.blit(self.title, self.title_rect)
        pygame.display.set_caption("shapegame")
        pygame.display.update()

        self.num_faces = 5
        self.stat_rects = [{}, {}]

        self.face_0 = random.randint(0, self.num_faces - 1)
        self.color_0 = random.randint(0, len(colors)-1)
        self.face_1 = random.randint(0, self.num_faces - 1)
        self.color_1 = random.randint(0, len(colors)-1)

        self.face_ids = [self.face_0, self.face_1]

        self.c0_count = circles[self.face_0]["team_size"]
        self.c1_count = circles[self.face_1]["team_size"]

        self.shown_circles = [[self.face_0, colors[self.color_0][0]], [self.face_1, colors[self.color_1][0]]]

        self.circles = pygame.sprite.Group()

        self.circle_images_full = circle_images_full

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
        # self.color_right_1 = self.arrow_right
        # self.color_right_1_rect = self.color_right_1.get_rect()
        # self.color_right_1_rect.center = (1920 / 3 + 50, 2 * 1080 / 3 + 230)

        self.color_right_1 = Arrow(1920 / 3 + 50, 2 * 1080 / 3 + 230, "->", 50, 50)

        # self.color_left_1 = self.arrow_left
        # self.color_left_1_rect = self.color_right_1.get_rect()
        # self.color_left_1_rect.center = (1920 / 3 - 50, 2 * 1080 / 3 + 230)

        self.color_left_1 = Arrow(1920 / 3 - 50, 2 * 1080 / 3 + 230,  "<-", 50, 50)

        # self.face_right_1 = self.arrow_right
        # self.face_right_1_rect = self.face_right_1.get_rect()
        # self.face_right_1_rect.center = (1920 / 3 + 50, 2 * 1080 / 3 + 270)

        self.face_right_1 = Arrow(1920 / 3 + 50, 2 * 1080 / 3 + 290, "->", 50, 50)

        # self.face_left_1 = self.arrow_left
        # self.face_left_1_rect = self.face_right_1.get_rect()
        # self.face_left_1_rect.center = (1920 / 3 - 50, 2 * 1080 / 3 + 270)

        self.face_left_1 = Arrow(1920 / 3 - 50, 2 * 1080 / 3 + 290, "<-", 50, 50)

        # self.color_right_0 = self.arrow_right
        # self.color_right_0_rect = self.color_right_0.get_rect()
        # self.color_right_0_rect.center = (2 * 1920 / 3 + 50, 2 * 1080 / 3 + 230)

        self.color_right_0 = Arrow(2 * 1920 / 3 + 50, 2 * 1080 / 3 + 230, "->", 50, 50)

        # self.color_left_0 = self.arrow_left
        # self.color_left_0_rect = self.color_right_0.get_rect()
        # self.color_left_0_rect.center = (2 * 1920 / 3 - 50, 2 * 1080 / 3 + 230)

        self.color_left_0 = Arrow(2 * 1920 / 3 - 50, 2 * 1080 / 3 + 230, "<-", 50, 50)

        # self.face_right_0 = self.arrow_right
        # self.face_right_0_rect = self.face_right_0.get_rect()
        # self.face_right_0_rect.center = (2 * 1920 / 3 + 50, 2 * 1080 / 3 + 270)

        self.face_right_0 = Arrow(2 * 1920 / 3 + 50, 2 * 1080 / 3 + 290, "->", 50, 50)

        # self.face_left_0 = self.arrow_left
        # self.face_left_0_rect = self.face_right_0.get_rect()
        # self.face_left_0_rect.center = (2 * 1920 / 3 - 50, 2 * 1080 / 3 + 270)

        self.face_left_0 = Arrow(2 * 1920 / 3 - 50, 2 * 1080 / 3 + 290, "<-", 50, 50)

        self.l_left = Arrow(1920 - 155, 880, "<-", 50, 50)
        self.l_right = Arrow(1920 - 90, 880, "->", 50, 50)

        self.r_left = Arrow(90, 880, "<-", 50, 50)
        self.r_right = Arrow(155, 880, "->", 50, 50)

        self.clickables.append(self.color_right_1)
        self.clickables.append(self.color_left_1)
        self.clickables.append(self.face_right_1)
        self.clickables.append(self.face_left_1)
        self.clickables.append(self.color_right_0)
        self.clickables.append(self.color_left_0)
        self.clickables.append(self.face_right_0)
        self.clickables.append(self.face_left_0)
        self.clickables.append(self.l_left)
        self.clickables.append(self.l_right)
        self.clickables.append(self.r_left)
        self.clickables.append(self.r_right)
    


        self.l_count_obj = self.font.render(str(self.c0_count), 1, "white")
        self.l_count_rect = self.l_count_obj.get_rect()
        self.l_count_rect.center = (1920 - 125, 820)
        
        # self.l_left = self.arrow_left
        # self.l_left_rect = self.l_left.get_rect()
        # self.l_left_rect.center = (1920 - 150, 880)

        # self.l_right = self.arrow_right
        # self.l_right_rect = self.l_right.get_rect()
        # self.l_right_rect.center = (1920 - 95, 880)

        

        self.r_count_obj = self.font.render(str(self.c1_count), 1, "white")
        self.r_count_rect = self.r_count_obj.get_rect()
        self.r_count_rect.center = (125, 820)
        
        # self.r_left = self.arrow_left
        # self.r_left_rect = self.r_left.get_rect()
        # self.r_left_rect.center = (100, 880)

        # self.r_right = self.arrow_right
        # self.r_right_rect = self.r_right.get_rect()
        # self.r_right_rect.center = (150, 880)

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

    def start(self):
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


            self.screen.blit(self.color_right_1.surface, self.color_right_1.rect)
            self.screen.blit(self.color_left_1.surface, self.color_left_1.rect)
            self.screen.blit(self.face_right_1.surface, self.face_right_1.rect)
            self.screen.blit(self.face_left_1.surface, self.face_left_1.rect)


            self.screen.blit(self.color_right_0.surface, self.color_right_0.rect)
            self.screen.blit(self.color_left_0.surface, self.color_left_0.rect)
            self.screen.blit(self.face_right_0.surface, self.face_right_0.rect)
            self.screen.blit(self.face_left_0.surface, self.face_left_0.rect)

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
            self.screen.blit(self.l_left.surface, self.l_left.rect)
            self.screen.blit(self.l_right.surface, self.l_right.rect)

            self.screen.blit(self.r_count_obj, self.r_count_rect)
            self.screen.blit(self.r_left.surface, self.r_left.rect)
            self.screen.blit(self.r_right.surface, self.r_right.rect)

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

                        if self.seed_input_rect.collidepoint(pygame.mouse.get_pos()):
                            self.seed_input_clicked = True
                            self.seed_input.cursor_visible = True
                            unclick_seed_input = False

                        elif self.color_right_1.rect.collidepoint(pygame.mouse.get_pos()):
                            self.color_1 += 1
                            if self.color_1 == len(colors): self.color_1 = 0
                            self.changeCircles()

                        elif self.color_left_1.rect.collidepoint(pygame.mouse.get_pos()):
                            self.color_1 -= 1
                            if self.color_1 == -1: self.color_1 = len(colors) - 1
                            # start_clicked = True
                            self.changeCircles()

                        elif self.face_right_1.rect.collidepoint(pygame.mouse.get_pos()):
                            self.face_1 += 1
                            if self.face_1 == self.num_faces: self.face_1 = 0
                            self.changeCircles()

                        elif self.face_left_1.rect.collidepoint(pygame.mouse.get_pos()):
                            self.face_1 -= 1
                            if self.face_1 == -1: self.face_1 = self.num_faces - 1
                            self.changeCircles()

                        elif self.color_right_0.rect.collidepoint(pygame.mouse.get_pos()):
                            self.color_0 += 1
                            if self.color_0 == len(colors): self.color_0 = 0
                            self.changeCircles()

                        elif self.color_left_0.rect.collidepoint(pygame.mouse.get_pos()):
                            self.color_0 -= 1
                            if self.color_0 == -1: self.color_0 = len(colors) - 1
                            # start_clicked = True
                            self.changeCircles()

                        elif self.face_right_0.rect.collidepoint(pygame.mouse.get_pos()):
                            self.face_0 += 1
                            if self.face_0 == self.num_faces: self.face_0 = 0
                            self.changeCircles()

                        elif self.face_left_0.rect.collidepoint(pygame.mouse.get_pos()):
                            self.face_0 -= 1
                            if self.face_0 == -1: self.face_0 = self.num_faces - 1
                            self.changeCircles()

                        elif self.start_clickable.rect.collidepoint(pygame.mouse.get_pos()):
                            start_clicked = True

                        elif self.simulate_clickable.rect.collidepoint(pygame.mouse.get_pos()):
                            simulate_clicked = True

                        elif self.l_left.rect.collidepoint(pygame.mouse.get_pos()):
                            if self.c0_count != 1: self.c0_count -= 1

                        elif self.l_right.rect.collidepoint(pygame.mouse.get_pos()):
                            if self.c0_count != 20: self.c0_count += 1

                        elif self.r_left.rect.collidepoint(pygame.mouse.get_pos()):
                            if self.c1_count != 1: self.c1_count -= 1

                        elif self.r_right.rect.collidepoint(pygame.mouse.get_pos()):
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
                game = Game(circle_0, circle_1, "team 1", "team 2", self.screen, seed, real)
                winner, self.stats_surface = game.play_game()
                self.game_played = True

            if start_clicked:
                self.start_sound.play()
                pygame.mixer.Sound.fadeout(self.menu_music, 1000)

                self.screen.blit(self.background, (0, 0))
                self.screen.blit(self.loading, self.loading_rect)
                pygame.display.update()

                seed = self.seed_input.value
                if seed == "Seed (optional)":
                    seed = False

                user_1 = User("someone")
                user_2 = User("someone else")
                shape_1 = DbShape(user_1.id, user_1, self.face_0, self.color_0, 1, circles[self.face_0]["velocity"], circles[self.face_0]["radius_min"], circles[self.face_0]["radius_max"], circles[self.face_0]["health"], circles[self.face_0]["dmg_multiplier"], circles[self.face_0]["luck"], circles[self.face_0]["team_size"], user_1.username, circles[self.face_0]["name"], "whatever")
                shape_2 = DbShape(user_2.id, user_2, self.face_1, self.color_1, 1, circles[self.face_1]["velocity"], circles[self.face_1]["radius_min"], circles[self.face_1]["radius_max"], circles[self.face_1]["health"], circles[self.face_1]["dmg_multiplier"], circles[self.face_1]["luck"], circles[self.face_1]["team_size"], user_2.username, circles[self.face_1]["name"], "whatever")

                print("Playing game with seed: {}".format(seed))
                
                game = Game2(self.screen, shape_1, shape_2, user_1, user_2, seed, False, False)
                game.play()
                self.game_played = True

                # circle_0 = circles[self.face_0].copy()
                # circle_1 = circles[self.face_1].copy()

                # circle_0["color"] = colors[self.color_0]
                # circle_0["group_id"] = 0
                # circle_0["face_id"] = self.face_0
                # circle_0["team_size"] = self.c0_count

                # circle_1["color"] = colors[self.color_1]
                # circle_1["group_id"] = 1
                # circle_1["face_id"] = self.face_1
                # circle_1["team_size"] = self.c1_count

                # seed = self.seed_input.value
                # if seed == "Seed (optional)":
                #     seed = False
                
                # real = True
                # print("Playing game with seed: {}".format(seed))
                # self.start_sound.play()
                # pygame.mixer.Sound.fadeout(self.menu_music, 1000)
                # game = Game(circle_0, circle_1, circle_0["name"], circle_1["name"], self.screen, seed, real, True)
                # winner, self.stats_surface = game.play_game()
                # self.game_played = True


            self.cursor_rect.center = pygame.mouse.get_pos()
            self.screen.blit(self.cursor, self.cursor_rect)

            if self.exit_clicked:
                running = False

            # limits FPS to 60
            self.clock.tick(60)
            # print(self.clock.get_fps())

    # HELPERS FROM MENU

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

    # LOCAL MATCH MENU FUNCTIONS

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

    def changeCircles(self):
        self.circle_1 = self.circle_images[self.face_0][self.color_0]
        self.circle_2 = self.circle_images[self.face_1][self.color_1]
        self.face_ids = [self.face_0, self.face_1]

        self.c0_count = circles[self.face_0]["team_size"]
        self.c1_count = circles[self.face_1]["team_size"]
