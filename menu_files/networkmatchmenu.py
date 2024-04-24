import pygame, time
import pygame.display
from pygame.locals import *
from pygame import surface

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
    def __init__(self, screen: surface, user: User, shapes: list[Shape], session, circle_images_full: list[list[Surface]]):
        # parameters from menu
        self.screen = screen
        self.user = user
        self.shapes = shapes
        self.session = session
        self.circle_images_full = circle_images_full

        # new required parameters
        self.network = Network()
        self.pid = self.network.getPlayer()
        self.pregame = self.network.getPregame()
        self.clock = pygame.time.Clock()
        self.winner = None
        self.exit_clicked = False
        self.connecting_flag = False
        self.frames_since_exit_clicked = 0
        self.stats_surface = 0

        # parameters for opponent
        self.shapes_opponent = None
        self.user_opponent = None

        # create screen elements
        self.title_text = Text("shapegame", 150, 1920/2, 1080/10)
        self.logged_in_as_text = Text("logged in as: " + self.user.username, 35, 1900, 10)
        self.bad_server_text = Text("server not found", 150, 1920/2, 1080/2)
        self.searching_text = Text("searching for opponent...", 150, 1920/2, 1080/2)
        self.match_found_text = Text("match found!", 150, 1920/2, 1080/2)
        self.opponent_disconnected_text = Text("opponent disconnected :()", 150, 1920/2, 1080/2)
        self.loading_text = Text("loading", 150, 1920/2, 1080/2)
        self.awaiting_text = Text("awaiting match results...", 150, 1920/2, 1080/2)

        self.exit_clickable = ClickableText("back", 50, 1860, 1045)
        self.checkbox = DoubleCheckbox("playing for keeps", 40, 1920/2, 900)
        self.ready_checkbox = DoubleCheckbox("ready", 100, 1920/2, 1000)

        self.right = Arrow(1920/2 + 50, 800-25, "->")
        self.left = Arrow(1920/2 - 50, 800-25, "<-")

        self.clickables = []
        self.clickables.append(self.exit_clickable)
        self.clickables.append(self.right)
        self.clickables.append(self.left)

        # load and center cursor, load background
        self.cursor = pygame.transform.smoothscale(pygame.image.load("backgrounds/cursor.png"), (12, 12))
        self.cursor_rect = self.cursor.get_rect()
        self.cursor_rect.center = pygame.mouse.get_pos()
        self.background = pygame.image.load("backgrounds/BG1.png")

        # update display 
        self.screen.blit(self.background, (0, 0))
        self.screen.blit(self.title_text.surface, self.title_text.rect)
        pygame.display.update()

        # sprite groups for your shapes and opponent shapes
        self.you_group = pygame.sprite.Group()
        self.opponent_group = pygame.sprite.Group()

        # your and your opponents name rendered in the color of all your/their shapes
        self.you_names = []
        self.opponent_names = []

        # create your menu shapes
        for counter, shape in enumerate(self.shapes):
            self.you_group.add(MenuShape(counter+1, shape, self.circle_images_full[shape.face_id][shape.color_id], len(self.shapes)))

        # load sounds
        self.click_sound = pygame.mixer.Sound("sounds/click.wav")
        self.start_sound = pygame.mixer.Sound("sounds/start.wav")
        self.close_sound = pygame.mixer.Sound("sounds/close.wav")

        self.menu_music = pygame.mixer.Sound("sounds/menu.wav")
        self.menu_music.set_volume(.5)
        self.close_sound.set_volume(.5)

        # Check for server (probably can be done better)
        self.server_found = False
        if self.pid != None: 
            self.pid = int(self.pid)
            self.server_found = True
        else:
            frames = 0
            while frames <= 120:
                self.screen.blit(self.background, (0, 0))
                self.screen.blit(self.server_not_found, self.server_not_found_rect)
                pygame.display.update()


                frames += 1
                self.clock.tick(60)
            return

        # determine which player you are (essentially the order you entered matchmaking)
        if self.pid == 0: self.pid_opponent = 1
        else: self.pid_opponent = 0

        # Send your user_id to the server
        self.network.send("USER_" + str(self.user.id) + ".")

        # Determine the index of shape you have selected
        self.idx_selected_you = 0
        if len(self.shapes) >= 5:
            self.idx_selected_you = 3
        elif len(self.shapes) == 4:
            self.idx_selected_you = 3
        elif len(self.shapes) == 3:
            self.idx_selected_you = 2
        elif len(self.shapes) == 2:
            self.idx_selected_you = 2
        else:
            self.idx_selected_you = 1

        self.network.send("SELECTED_" + str(self.idx_selected_you) + ".")
        time.sleep(1)

    def start(self):
        # return if server wasn't found
        if not self.server_found: return
    
        self.awaitOpponent()

        # other things
        frames = 0
        self.connecting_flag = True
        running = True
        ready = False

        # MAIN LOOP ---------------------------------------------
        self.network.send("SHAPE_" + str(self.shapes[self.idx_selected_you-1].id) + ".")


        while running:
            self.clock.tick(60)

            mouse_pos = pygame.mouse.get_pos()
            for clickable in self.clickables:
                clickable.update(mouse_pos)
            
            try:
                self.pregame = self.network.getPregame()

                while not self.pregame.ready:
                    pygame.display.flip()
                    self.screen.blit(self.background, (0, 0))
                    self.screen.blit(self.searching_text.surface, self.searching_text.rect)
                    self.screen.blit(self.exit_clickable.surface, self.exit_clickable.rect)

                    self.cursor_rect.center = pygame.mouse.get_pos()
                    self.screen.blit(self.cursor, self.cursor_rect)

                    for event in pygame.event.get():
                        if event.type == MOUSEBUTTONDOWN:
                            if self.exit_clickable.rect.collidepoint(mouse_pos):
                                self.network.send("KILL.")
                                return


                    self.pregame = self.network.getPregame()
                    self.clock.tick(60)
            except:
                running = False

                self.screen.blit(self.background, (0, 0))
                self.screen.blit(self.opponent_disconnected_text.surface, self.opponent_disconnected_text.rect)
                pygame.display.update()

                self.opponent_group.empty()
                for shape in self.you_group.sprites():
                    shape.goHome()
                    shape.disable()

                time.sleep(0.5)
                break

            # print(repr(self.pregame))

            # check if opponent clicked ready
            if self.pregame.players_ready[self.pid_opponent] != self.ready_checkbox.opp_checked:
                self.ready_checkbox.oppToggle()

            # check if opponent clicked keeps
            if self.pregame.keeps[self.pid_opponent] != self.checkbox.opp_checked:
                self.checkbox.oppToggle()

            # check if opponent left
            if self.pregame.kill[self.pid_opponent]:
                running = False

                self.screen.blit(self.background, (0, 0))
                self.screen.blit(self.opponent_disconnected_text.surface, self.opponent_disconnected_text.rect)
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
                self.screen.blit(self.match_found_text.surface, self.match_found_text.rect)
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
                            if self.idx_selected_you != 1:
                                self.idx_selected_you -= 1

                                if len(self.shapes) >= 6:
                                    for shape in self.you_group.sprites():
                                        shape.moveRight()

                        elif self.right.rect.collidepoint(mouse_pos):
                            if self.idx_selected_you != len(self.shapes):
                                self.idx_selected_you += 1
                                
                                if len(self.shapes) >= 6:
                                    for shape in self.you_group.sprites():
                                        shape.moveLeft()

                        self.network.send("SELECTED_" + str(self.idx_selected_you) + ".")
                        self.network.send("SHAPE_" + str(self.shapes[self.idx_selected_you-1].id) + ".")

                        counter = 0
                        for shape in self.you_group.sprites():
                            counter += 1
                            if counter == self.idx_selected_you:
                                shape.select()
                            else:
                                shape.disable()

            # self.network.send("SHAPE_" + str(self.shapes[self.idx_selected_you-1].id + "."))

            # Check if your record of the opponent selected shape matches with server
            if opponent_selected != self.pregame.users_selected[self.pid_opponent]:
                if opponent_selected < self.pregame.users_selected[self.pid_opponent]:
                    opponent_selected += 1

                    if len(self.shapes_opponent) >= 6:
                        for opponent_shape in self.opponent_group.sprites():
                            opponent_shape.moveLeft()

                else:
                    opponent_selected -= 1

                    if len(self.shapes_opponent) >= 6:
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
            self.screen.blit(self.you_names[self.idx_selected_you-1][0], self.you_names[self.idx_selected_you-1][1])
            self.screen.blit(self.opponent_names[opponent_selected-1][0], self.opponent_names[opponent_selected-1][1])
            self.screen.blit(self.logged_in_as_text.surface, self.logged_in_as_text.rect)

            # if self.pregame.keeps[opponent]: self.screen.blit(self.checked, self.checked_rect)
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
            
            # self.network.send("SHAPE_" + str(self.shapes[self.idx_selected_you-1].id + "."))

            self.pregame = self.network.getPregame()

            # check if opponent left
            if self.pregame.kill[self.pid_opponent]:
                running = False

                self.screen.blit(self.background, (0, 0))
                self.screen.blit(self.opponent_disconnected_text.surface, self.opponent_disconnected_text.rect)
                pygame.display.update()

                self.opponent_group.empty()
                for shape in self.you_group.sprites():
                    shape.goHome()
                    shape.disable()

                time.sleep(0.5)
                break

            if self.pregame.seed != False:
                self.screen.blit(self.background, (0, 0))
                self.screen.blit(self.loading_text.surface, self.loading_text.rect)
                pygame.display.update()

                self.network.send("SHAPE_" + str(self.shapes[self.idx_selected_you-1].id) + ".")


                # print(self.idx_selected_you, opponent_selected)

                your_circle = {}
                your_shape = self.shapes[self.idx_selected_you -1]
                their_circle = {}
                their_shape = self.shapes_opponent[opponent_selected -1]

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
                print("Playing game with seed: {}".format(self.pregame.seed))
                self.start_sound.play()
                pygame.mixer.Sound.fadeout(self.menu_music, 1000)

                if self.pid == 0:
                    your_circle["group_id"] = 0
                    their_circle["group_id"] = 1

                    game = Game(your_circle, their_circle, self.user.username, opponent_user.username, self.screen, self.pregame.seed, real)
                    fake_game = Game(your_circle, their_circle, "", "", None, self.pregame.seed, False)


                else:
                    your_circle["group_id"] = 1
                    their_circle["group_id"] = 0

                    game = Game(their_circle, your_circle, opponent_user.username, self.user.username, self.screen, self.pregame.seed, real)
                    fake_game = Game(their_circle, your_circle, "", "", None, self.pregame.seed, False)

                # self.getWinner(fake_game)
                game.play_game()
                # self.network.receive()
                self.pregame = self.network.getPregame()

                while self.pregame.winner == None:
                    self.pregame = self.network.getPregame()

                    mouse_pos = pygame.mouse.get_pos()
                    self.cursor_rect.center = mouse_pos

                    pygame.display.flip()
                    self.screen.blit(self.background, [0,0])
                    self.screen.blit(self.awaiting_text.surface, self.awaiting_text.rect)
                    self.screen.blit(self.cursor, self.cursor_rect)

                    self.clock.tick(60)

                pygame.display.flip()
                self.screen.blit(self.background, [0,0])
                self.screen.blit(self.loading_text.surface, self.loading_text.rect)
                # self.screen.blit(self.cursor, self.cursor_rect)
                pygame.display.update()

                postGame = PostGame(self.pregame.winner == self.pid, your_shape, their_shape, (self.pregame.keeps[0] == 1 and self.pregame.keeps[1] == 1), self.pregame.xp_earned, self.you_names[self.idx_selected_you-1], self.opponent_names[opponent_selected-1], self.screen)
                postGame.start()

                break
            
            self.cursor_rect.center = pygame.mouse.get_pos()
            self.screen.blit(self.cursor, self.cursor_rect)
            frames += 1    

        # print("RUN")
        for shape in self.you_group.sprites():
            shape.goHome()
            shape.disable()

    def awaitOpponent(self):
            while self.pregame == None or self.pregame.user_ids[self.pid_opponent] == -1:
                pygame.display.flip()
                self.screen.blit(self.background, (0, 0))
                self.screen.blit(self.searching_text.surface, self.searching_text.rect)
                self.screen.blit(self.exit_clickable.surface, self.exit_clickable.rect)
                self.cursor_rect.center = pygame.mouse.get_pos()
                self.screen.blit(self.cursor, self.cursor_rect)

                for event in pygame.event.get():
                    if event.type == MOUSEBUTTONDOWN and self.exit_clickable.rect.collidepoint(pygame.mouse.get_pos()):
                        self.network.send("KILL.")
                        return

                self.pregame = self.network.getPregame()
                self.clock.tick(60)

            # -- Load opponent --
            self.shapes_opponent = self.session.query(Shape).filter(Shape.owner_id == int(self.pregame.user_ids[self.pid_opponent])).all()
            self.user_opponent = self.session.query(User).filter(User.id == int(self.pregame.user_ids[self.pid_opponent])).one()
            self.opponent_group.empty()
            text_surface, text_rect = self.createText("loading your shapes", 100)
            text_rect.center = [1920 / 2, 1080 / 2]
            self.screen.blit(self.background, (0, 0))
            self.screen.blit(text_surface, text_rect)
            pygame.display.update()

            # Build opponent shapes + username tags for each player
            counter = 1
            for shape in self.shapes_opponent:
                self.opponent_group.add(MenuShape(counter, shape, self.circle_images_full[shape.face_id][shape.color_id], len(self.shapes_opponent), "OPPONENT"))
                
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
            if len(self.shapes_opponent) >= 5:
                opponent_selected = 3
            elif len(self.shapes_opponent) == 4:
                opponent_selected = 3
            elif len(self.shapes_opponent) == 3:
                opponent_selected = 2
            elif len(self.shapes_opponent) == 2:
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
                if counter == self.idx_selected_you:
                    shape.select()
                else:
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
