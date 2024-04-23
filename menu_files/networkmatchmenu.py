import pygame, time
import pygame.display
from pygame.locals import *
from game_files.game import Game
from menu_files.network_pregame_files.network import Network
from game_files.circledata import *
from server_files.database_user import User
from server_files.database_shape import Shape
from screen_elements.clickabletext import ClickableText
from screen_elements.doublecheckbox import DoubleCheckbox
from menu_files.main_menu_files.menucircle import MenuShape
from screen_elements.arrow import Arrow
from menu_files.postgame import PostGame
from threading import Thread

class NetworkMatchMenu():
    def __init__(self, screen, user, shapes, session, circle_images_full):
        self.screen = screen
        self.network = Network()
        self.user = user
        self.shapes = shapes
        self.session = session
        self.circle_images_full = circle_images_full
        self.winner = None

        self.you_group = pygame.sprite.Group()
        self.opponent_group = pygame.sprite.Group()

        self.you_names = []
        self.opponent_names = []

        counter = 1
        for shape in self.shapes:
            self.you_group.add(MenuShape(counter, shape, self.circle_images_full[shape.face_id][shape.color_id], len(self.shapes)))
            counter += 1

        self.checked = pygame.transform.smoothscale(pygame.image.load("backgrounds/box_checked.png"), (28, 28))
        self.checked_rect = self.checked.get_rect()
        self.unchecked = pygame.transform.smoothscale(pygame.image.load("backgrounds/box_unchecked.png"),  (28, 28))
        self.unchecked_rect = self.unchecked.get_rect()
        self.checked_rect.center = self.unchecked_rect.center = [1118, 900]

        self.ready_checked = pygame.transform.smoothscale(pygame.image.load("backgrounds/box_checked.png"), (133, 133))
        self.ready_checked_rect = self.ready_checked.get_rect()
        self.ready_unchecked = pygame.transform.smoothscale(pygame.image.load("backgrounds/box_unchecked.png"),  (133, 133))
        self.ready_unchecked_rect = self.ready_unchecked.get_rect()
        self.ready_checked_rect.center = self.ready_unchecked_rect.center = [1125, 1000]


        self.cursor = pygame.transform.smoothscale(pygame.image.load("backgrounds/cursor.png"), (12, 12))
        self.cursor_rect = self.cursor.get_rect()
        self.cursor_rect.center = pygame.mouse.get_pos()
        self.background = pygame.image.load("backgrounds/BG1.png")
        self.title, self.title_rect = self.createText("shapegame", 150)
        self.title_rect.center = (1920 / 2, 1080 / 2)
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font("backgrounds/font.ttf", 80)
        self.stats_surface = 0
        self.connecting_flag = False

        self.exit_clicked = False
        self.frames_since_exit_clicked = 0

        self.click_sound = pygame.mixer.Sound("sounds/click.wav")
        self.start_sound = pygame.mixer.Sound("sounds/start.wav")
        self.close_sound = pygame.mixer.Sound("sounds/close.wav")

        self.menu_music = pygame.mixer.Sound("sounds/menu.wav")
        self.menu_music.set_volume(.5)
        self.close_sound.set_volume(.5)
        

        self.logged_in_as, self.logged_in_as_rect = self.createText("logged in as: " + self.user.username, 35)
        self.logged_in_as_rect.topright = (1900, 10)

        self.try_again, self.try_again_rect = self.createText("User not found!", 150)
        self.try_again_rect.center = [1920 / 2, 800]


        self.server_not_found, self.server_not_found_rect = self.createText("server not found", 150)
        self.server_not_found_rect.center = [1920 / 2, 1080 / 2]

        self.play, self.play_rect = self.createText("play", 100)
        self.play_rect.center = [3 * 1920 / 4, 750]
        
        
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

        self.simulating, self.simulating_rect = self.createText("awaiting match results...", 150)
        self.simulating_rect.center = [1920 / 2, 1080 / 2]

        self.exit_clickable = ClickableText("back", 50, 1860, 1045)
        self.checkbox = DoubleCheckbox("playing for keeps", 40, 1920/2, 900)
        self.ready_checkbox = DoubleCheckbox("ready", 100, 1920/2, 1000)

        self.right = Arrow(1920/2 + 50, 800-25, "->")
        self.left = Arrow(1920/2 - 50, 800-25, "<-")

        self.clickables = []
        self.clickables.append(self.exit_clickable)
        self.clickables.append(self.right)
        self.clickables.append(self.left)

        self.screen.blit(self.background, (0, 0))
        self.screen.blit(self.title, self.title_rect)
        pygame.display.set_caption("shapegame")
        pygame.display.update()

    def start(self):
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
        self.network.send("USER_" + str(self.user.id) + ".")

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

        self.network.send("SELECTED_" + str(you_selected) + ".")
        time.sleep(1)

        # Retrieve opponent user id and query for their shapes
        pregame = self.network.getPregame()

        while pregame == None or pregame.user_ids[opponent] == -1:
            pygame.display.flip()
            self.screen.blit(self.background, (0, 0))
            self.screen.blit(self.searching, self.searching_rect)
            self.screen.blit(self.exit_clickable.surface, self.exit_clickable.rect)
            self.cursor_rect.center = pygame.mouse.get_pos()
            self.screen.blit(self.cursor, self.cursor_rect)

            for event in pygame.event.get():
                if event.type == MOUSEBUTTONDOWN and self.exit_clickable.rect.collidepoint(pygame.mouse.get_pos()):
                    self.network.send("KILL.")
                    return

            pregame = self.network.getPregame()
            self.clock.tick(60)

        # -- Load opponent --
        opponent_shapes = self.session.query(Shape).filter(Shape.owner_id == int(pregame.user_ids[opponent])).all()
        opponent_user = self.session.query(User).filter(User.id == int(pregame.user_ids[opponent])).one()
        self.opponent_group.empty()
        text_surface, text_rect = self.createText("loading your shapes", 100)
        text_rect.center = [1920 / 2, 1080 / 2]
        self.screen.blit(self.background, (0, 0))
        self.screen.blit(text_surface, text_rect)
        pygame.display.update()

        # Build opponent shapes + username tags for each player
        counter = 1
        for shape in opponent_shapes:
            self.opponent_group.add(MenuShape(counter, shape, self.circle_images_full[shape.face_id][shape.color_id], len(opponent_shapes), "OPPONENT"))
            
            opponent_username_surface, opponent_username_rect = self.createText(opponent_user.username, 100, colors[shape.color_id][2])
            opponent_username_rect.center = [1515, 750 - 35- 30]

            self.opponent_names.append([opponent_username_surface, opponent_username_rect])

            counter += 1

        for shape in self.shapes:
            you_username_surface, you_username_rect = self.createText(self.user.username, 100, colors[shape.color_id][2])
            you_username_rect.center = [420, 750 - 35 -30]

            self.you_names.append([you_username_surface, you_username_rect])


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
        # right_surface = pygame.transform.smoothscale(pygame.image.load("backgrounds/arrow_right.png"), (75, 50))
        # right_rect = right_surface.get_rect()
        # right_rect.center = [1920 / 2 + 50, 800]

        # left_surface = pygame.transform.smoothscale(pygame.image.load("backgrounds/arrow_left.png"), (75, 50))
        # left_rect = left_surface.get_rect()
        # left_rect.center = [1920 / 2 - 50, 800]

        # other things
        frames = 0
        self.connecting_flag = True
        running = True
        ready = False

        # MAIN LOOP ---------------------------------------------
        self.network.send("SHAPE_" + str(self.shapes[you_selected-1].id) + ".")


        while running:
            self.clock.tick(60)

            mouse_pos = pygame.mouse.get_pos()
            for clickable in self.clickables:
                clickable.update(mouse_pos)
            
            try:
                pregame = self.network.getPregame()

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
                                self.network.send("KILL.")
                                return


                    pregame = self.network.getPregame()
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

            # print(repr(pregame))

            # check if opponent clicked ready
            if pregame.players_ready[opponent] != self.ready_checkbox.opp_checked:
                self.ready_checkbox.oppToggle()

            # check if opponent clicked keeps
            if pregame.keeps[opponent] != self.checkbox.opp_checked:
                self.checkbox.oppToggle()

            # check if opponent left
            if pregame.kill[opponent]:
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
                    # print(mouse_pos)
                    self.click_sound.play()

                    if self.exit_clickable.rect.collidepoint(mouse_pos):
                        self.exit_clicked = True

                    elif self.checkbox.rect.collidepoint(mouse_pos):
                        self.checkbox.toggle()
                        self.network.send("KEEPS_" + str(self.checkbox.getValue()) + ".")

                    elif self.ready_checkbox.rect.collidepoint(mouse_pos):
                        self.ready_checkbox.toggle()
                        self.network.readyUp(str(self.ready_checkbox.getValue()))

                    elif self.right.rect.collidepoint(mouse_pos) or self.left.rect.collidepoint(mouse_pos):
                        if self.left.rect.collidepoint(mouse_pos):
                            # Check if selected shape in bounds
                            if you_selected != 1:
                                you_selected -= 1

                                if len(self.shapes) >= 6:
                                    for shape in self.you_group.sprites():
                                        shape.moveRight()

                        elif self.right.rect.collidepoint(mouse_pos):
                            if you_selected != len(self.shapes):
                                you_selected += 1
                                
                                if len(self.shapes) >= 6:
                                    for shape in self.you_group.sprites():
                                        shape.moveLeft()

                        self.network.send("SELECTED_" + str(you_selected) + ".")
                        self.network.send("SHAPE_" + str(self.shapes[you_selected-1].id) + ".")

                        counter = 0
                        for shape in self.you_group.sprites():
                            counter += 1
                            if counter == you_selected:
                                shape.select()
                            else:
                                shape.disable()

            # self.network.send("SHAPE_" + str(self.shapes[you_selected-1].id + "."))

            # Check if your record of the opponent selected shape matches with server
            if opponent_selected != pregame.users_selected[opponent]:
                if opponent_selected < pregame.users_selected[opponent]:
                    opponent_selected += 1

                    if len(opponent_shapes) >= 6:
                        for opponent_shape in self.opponent_group.sprites():
                            opponent_shape.moveLeft()

                else:
                    opponent_selected -= 1

                    if len(opponent_shapes) >= 6:
                        for opponent_shape in self.opponent_group.sprites():
                                opponent_shape.moveRight()

                counter = 0
                for shape in self.opponent_group.sprites():
                    counter += 1
                    if counter == opponent_selected:
                        shape.select()
                    else:
                        shape.disable()
   
            self.screen.blit(self.background, (0, 0))

            self.you_group.draw(self.screen)
            self.you_group.update(self.screen)

            self.opponent_group.draw(self.screen)
            self.opponent_group.update(self.screen)

            self.screen.blit(self.title, (1920 / 2 - self.title.get_size()[0] / 2, 50 - 35-25))  
            self.screen.blit(self.exit_clickable.surface, self.exit_clickable.rect)
            self.screen.blit(self.checkbox.surface, self.checkbox.rect)
            self.screen.blit(self.ready_checkbox.surface, self.ready_checkbox.rect)
            # self.screen.blit(left_surface, left_rect)
            # self.screen.blit(right_surface, right_rect)
            self.screen.blit(self.right.surface, self.right.rect)
            self.screen.blit(self.left.surface, self.left.rect)
            # self.screen.blit(you_username_surface, you_username_rect)
            # self.screen.blit(opponent_username_surface, opponent_username_rect)
            self.screen.blit(self.you_names[you_selected-1][0], self.you_names[you_selected-1][1])
            self.screen.blit(self.opponent_names[opponent_selected-1][0], self.opponent_names[opponent_selected-1][1])
            self.screen.blit(self.logged_in_as, self.logged_in_as_rect)

            # if pregame.keeps[opponent]: self.screen.blit(self.checked, self.checked_rect)
            # else: self.screen.blit(self.unchecked, self.unchecked_rect)

            self.cursor_rect.center = mouse_pos
            self.screen.blit(self.cursor, self.cursor_rect)

            # if not ready: self.screen.blit(self.ready_q, self.ready_q_rect)
            # else: self.screen.blit(self.ready_e, self.ready_e_rect)

            pygame.display.flip()
            
            if self.exit_clicked:
                self.network.send("KILL.")

                self.opponent_group.empty()
                for shape in self.you_group.sprites():
                    shape.goHome()
                    shape.disable()

                break
            
            # self.network.send("SHAPE_" + str(self.shapes[you_selected-1].id + "."))

            pregame = self.network.getPregame()

            # check if opponent left
            if pregame.kill[opponent]:
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

            if pregame.seed != False:
                self.screen.blit(self.background, (0, 0))
                self.screen.blit(self.loading, (1920 / 2 - self.loading.get_size()[0] / 2, 1080 / 2 - self.loading.get_size()[1] / 2))
                pygame.display.update()

                self.network.send("SHAPE_" + str(self.shapes[you_selected-1].id) + ".")


                # print(you_selected, opponent_selected)

                your_circle = {}
                your_shape = self.shapes[you_selected -1]
                their_circle = {}
                their_shape = opponent_shapes[opponent_selected -1]

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

                    game = Game(your_circle, their_circle, self.user.username, opponent_user.username, self.screen, pregame.seed, real)
                    fake_game = Game(your_circle, their_circle, "", "", None, pregame.seed, False)


                else:
                    your_circle["group_id"] = 1
                    their_circle["group_id"] = 0

                    game = Game(their_circle, your_circle, opponent_user.username, self.user.username, self.screen, pregame.seed, real)
                    fake_game = Game(their_circle, your_circle, "", "", None, pregame.seed, False)

                # self.getWinner(fake_game)
                game.play_game()
                # self.network.receive()
                pregame = self.network.getPregame()

                while pregame.winner == None:
                    pregame = self.network.getPregame()

                    mouse_pos = pygame.mouse.get_pos()
                    self.cursor_rect.center = mouse_pos

                    pygame.display.flip()
                    self.screen.blit(self.background, [0,0])
                    self.screen.blit(self.simulating, self.simulating_rect)
                    self.screen.blit(self.cursor, self.cursor_rect)

                    self.clock.tick(60)

                pygame.display.flip()
                self.screen.blit(self.background, [0,0])
                self.screen.blit(self.loading, self.loading_rect)
                # self.screen.blit(self.cursor, self.cursor_rect)
                pygame.display.update()

                postGame = PostGame(pregame.winner == player_id, your_shape, their_shape, (pregame.keeps[0] == 1 and pregame.keeps[1] == 1), pregame.xp_earned, self.you_names[you_selected-1], self.opponent_names[opponent_selected-1], self.screen)
                postGame.start()

                break
            
            self.cursor_rect.center = pygame.mouse.get_pos()
            self.screen.blit(self.cursor, self.cursor_rect)
            frames += 1    

        # print("RUN")
        for shape in self.you_group.sprites():
            shape.goHome()
            shape.disable()

    # HELPERS

    def getWinner(self, fake_game):
        self.winner = fake_game.play_game()
        print("FAKE GAME DONE")


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
