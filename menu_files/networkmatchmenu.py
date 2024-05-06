import pygame, time
import pygame.display
from pygame.locals import *
from pygame import Surface


from menu_files.network_pregame_files.network import Network
from game_files.game import Game
from game_files.circledata import *
from server_files.database_classes import User, Shape
from screen_elements.clickabletext import ClickableText
from screen_elements.doublecheckbox import DoubleCheckbox
from screen_elements.text import Text
from menu_files.main_menu_files.menucircle import MenuShape
from screen_elements.arrow import Arrow
from menu_files.postgame import PostGame

class NetworkMatchMenu():
    def __init__(self, screen: Surface, user: User, shapes: list[Shape], session, circle_images_full: list[list[Surface]], method = "STANDARD."):
        # parameters from menu
        self.screen = screen
        self.user = user
        self.shapes = shapes
        self.session = session
        self.circle_images_full = circle_images_full

        # new required parameters
        self.network = Network(method)
        self.pid = self.network.pid
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
        self.logged_in_as_text = Text("logged in as: " + self.user.username, 35, 1900, 10, "topright")
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

        self.clickables: list[ClickableText] = []
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
        self.you_names: list[Surface] = []
        self.opponent_names: list[Surface] = []

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
                self.screen.blit(self.bad_server_text.surface, self.bad_server_text.rect)
                pygame.display.update()


                frames += 1
                self.clock.tick(60)
            return

        # determine which player your opponent is
        if self.pid == 0: self.pid_opponent = 1
        else: self.pid_opponent = 0

        # Send your user_id to the server
        self.network.send("USER_" + str(self.user.id) + ".")

        # Determine the index of shape you have selected to start
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

        # Above index for opponent
        self.idx_selected_opponent = -1

        # tell the server what shape you have selected
        self.network.send("SELECTED_" + str(self.idx_selected_you) + ".")
        self.network.send("SHAPE_" + str(self.shapes[self.idx_selected_you-1].id) + ".")
        time.sleep(1)

    # menu loop
    def start(self):
        # return if server wasn't found
        if not self.server_found: return
    
        # wait for an opponent to connect to the server (quick return on kill signal)
        redirect = self.awaitOpponent()
        if redirect == "KILL": return

        # display to the user that a match has been found for a moment
        self.screen.blit(self.background, (0, 0))
        self.screen.blit(self.match_found_text.surface, self.match_found_text.rect)
        pygame.display.update()
        time.sleep(0.5)

        while True:
            # update pregame object
            self.pregame = self.network.getPregame()

            # handle inputs from user and opponent (quick return on kill signal)
            redirect = self.handleInputs()
            if redirect == "KILL": break
            
            # update and draw all screen elements
            self.updateAndDraw()
            
            # possibly unnecessary update pregame object
            self.pregame = self.network.getPregame()

            # if the pregame seed is populated, start the game
            if self.pregame.seed != False:
                self.startGame()
                break
                
            # if exit was clicked
            if self.exit_clicked:
                self.network.send("KILL.")
                break

            self.clock.tick(60)

    # loop while waiting for an opponent
    def awaitOpponent(self):
        # while no opponent is connected
        while self.pregame == None or self.pregame.user_ids[self.pid_opponent] == -1 or self.pregame.users_selected[self.pid_opponent] == -1:
            pygame.display.flip()
            self.screen.blit(self.background, (0, 0))
            self.screen.blit(self.searching_text.surface, self.searching_text.rect)
            self.screen.blit(self.exit_clickable.surface, self.exit_clickable.rect)
            self.cursor_rect.center = pygame.mouse.get_pos()
            self.screen.blit(self.cursor, self.cursor_rect)

            for event in pygame.event.get():
                if event.type == MOUSEBUTTONDOWN and self.exit_clickable.rect.collidepoint(pygame.mouse.get_pos()):
                    self.network.send("KILL.")
                    return "KILL"

            self.pregame = self.network.getPregame()
            self.clock.tick(60)

        # query for opponent user and shapes
        self.shapes_opponent = self.session.query(Shape).filter(Shape.owner_id == int(self.pregame.user_ids[self.pid_opponent])).all()
        self.user_opponent = self.session.query(User).filter(User.id == int(self.pregame.user_ids[self.pid_opponent])).one()

        # Build opponent shapes + username tags for each player
        for counter, shape in enumerate(self.shapes_opponent):
            self.opponent_group.add(MenuShape(counter+1, shape, self.circle_images_full[shape.face_id][shape.color_id], len(self.shapes_opponent), "OPPONENT"))
            self.opponent_names.append(Text(self.user_opponent.username, 100, 1515, 685, "center", colors[shape.color_id][2]))

        for shape in self.shapes:
            self.you_names.append(Text(self.user.username, 100, 420, 685, "center", colors[shape.color_id][2]))

        # Determine opponents selected shape
        if len(self.shapes_opponent) >= 5:
            self.idx_selected_opponent = 3
        elif len(self.shapes_opponent) == 4:
            self.idx_selected_opponent = 3
        elif len(self.shapes_opponent) == 3:
            self.idx_selected_opponent = 2
        elif len(self.shapes_opponent) == 2:
            self.idx_selected_opponent = 2
        else:
            self.idx_selected_opponent = 1

        # select the appropriate shape for you and user
        for counter, shape in enumerate(self.opponent_group):
            if counter+1 == self.idx_selected_opponent:
                shape.select()
            else:
                shape.disable()

        for counter, shape in enumerate(self.you_group):
            if counter+1 == self.idx_selected_you:
                shape.select()
            else:
                shape.disable()

        self.connecting_flag = True

    # update and draw all screen elements
    def updateAndDraw(self):
        pygame.display.flip()
        self.screen.blit(self.background, (0, 0))

        self.you_group.update(self.screen)
        self.you_group.draw(self.screen)
        self.opponent_group.update(self.screen)
        self.opponent_group.draw(self.screen)

        self.screen.blit(self.title_text.surface, (1920 / 2 - self.title_text.surface.get_size()[0] / 2, 50 - 35-25))  
        self.screen.blit(self.exit_clickable.surface, self.exit_clickable.rect)
        self.screen.blit(self.checkbox.surface, self.checkbox.rect)
        self.screen.blit(self.ready_checkbox.surface, self.ready_checkbox.rect)
        self.screen.blit(self.right.surface, self.right.rect)
        self.screen.blit(self.left.surface, self.left.rect)
        self.screen.blit(self.logged_in_as_text.surface, self.logged_in_as_text.rect)
        self.screen.blit(self.you_names[self.idx_selected_you-1].surface, self.you_names[self.idx_selected_you-1].rect)
        self.screen.blit(self.opponent_names[self.idx_selected_opponent-1].surface, self.opponent_names[self.idx_selected_opponent-1].rect)

        self.cursor_rect.center = pygame.mouse.get_pos()
        self.screen.blit(self.cursor, self.cursor_rect)

    # handle all inputs from the user
    def handleInputs(self):
        for event in pygame.event.get():
            if event.type == MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
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

        # return in case opponent sent kill signal
        return self.handleOpponentInputs()

    # handle all inputs (changes to pregame) by user
    def handleOpponentInputs(self):
        # check if opponent clicked ready
        if self.pregame.players_ready[self.pid_opponent] != self.ready_checkbox.opp_checked:
            self.ready_checkbox.oppToggle()

        # check if opponent clicked keeps
        if self.pregame.keeps[self.pid_opponent] != self.checkbox.opp_checked:
            self.checkbox.oppToggle()

        # check if opponent left
        if self.pregame.kill[self.pid_opponent]:

            self.screen.blit(self.background, (0, 0))
            self.screen.blit(self.opponent_disconnected_text.surface, self.opponent_disconnected_text.rect)
            pygame.display.update()

            time.sleep(0.5)
            return "KILL"
        
        # Check if your record of the opponent selected shape matches with server
        if self.idx_selected_opponent != self.pregame.users_selected[self.pid_opponent]:
            if self.idx_selected_opponent < self.pregame.users_selected[self.pid_opponent]:
                self.idx_selected_opponent += 1

                if len(self.shapes_opponent) >= 6:
                    for opponent_shape in self.opponent_group.sprites():
                        opponent_shape.moveLeft()

            else:
                self.idx_selected_opponent -= 1

                if len(self.shapes_opponent) >= 6:
                    for opponent_shape in self.opponent_group.sprites():
                            opponent_shape.moveRight()

            for counter, shape in enumerate(self.opponent_group):
                if (counter + 1) == self.idx_selected_opponent:
                    shape.select()
                else:
                    shape.disable()

    # create Game and PostGame
    def startGame(self):
        self.screen.blit(self.background, (0, 0))
        self.screen.blit(self.loading_text.surface, self.loading_text.rect)
        pygame.display.update()

        # (possibly unnecessary) send your shape id one last time just in case
        self.network.send("SHAPE_" + str(self.shapes[self.idx_selected_you-1].id) + ".")

        # THIS IS TRASH - Game should just take database shape objects
        # task for a different day though
        your_circle = {}
        your_shape = self.shapes[self.idx_selected_you -1]
        their_circle = {}
        their_shape = self.shapes_opponent[self.idx_selected_opponent -1]

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
    
        self.start_sound.play()
        pygame.mixer.Sound.fadeout(self.menu_music, 1000)

        # group ids and parameter order depends on which user you are
        if self.pid == 0:
            your_circle["group_id"] = 0
            their_circle["group_id"] = 1

            game = Game(your_circle, their_circle, self.user.username, self.user_opponent.username, self.screen, self.pregame.seed)

        else:
            your_circle["group_id"] = 1
            their_circle["group_id"] = 0

            game = Game(their_circle, your_circle, self.user_opponent.username, self.user.username, self.screen, self.pregame.seed)
        
        # play the game
        game.play_game()
        del game

        # if the server has not determined a winner yet
        while self.pregame.winner == None:
            # update pregame object
            self.pregame = self.network.getPregame()

            # check to see if exit clicked
            for event in pygame.event.get():
                if event.type == MOUSEBUTTONDOWN:
                    self.click_sound.play()

                    if self.exit_clickable.rect.collidepoint(mouse_pos): return

            # update mouse position
            mouse_pos = pygame.mouse.get_pos()
            self.cursor_rect.center = mouse_pos

            # draw elements to the screen
            pygame.display.flip()
            self.screen.blit(self.background, [0,0])
            self.screen.blit(self.awaiting_text.surface, self.awaiting_text.rect)
            self.screen.blit(self.cursor, self.cursor_rect)

            self.clock.tick(60)

        # create and start the post-game menu
        postGame = PostGame(self.pregame.winner == self.pid, your_shape, their_shape, (self.pregame.keeps[0] == 1 and self.pregame.keeps[1] == 1), self.pregame.xp_earned, self.you_names[self.idx_selected_you-1], self.opponent_names[self.idx_selected_opponent-1], self.screen)
        postGame.start()
        del postGame
