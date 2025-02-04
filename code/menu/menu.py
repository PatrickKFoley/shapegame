from pygame.locals import *
import pygame.mouse
from pygame.sprite import Group
from pygame.mixer import Sound
from pygame.surface import Surface
from pygame.transform import smoothscale
from pygame.image import load
import pygame, time, itertools, sys, random
from typing import Union

from createdb import User, Shape as ShapeData, Notification, FRIEND_ADD, FRIEND_CONFIRM, CHALLENGE, generateRandomShape
from ..screen_elements.text import Text
from ..screen_elements.editabletext import EditableText
from ..screen_elements.clickabletext import ClickableText
from ..screen_elements.button import Button
from ..screen_elements.screenelement import ScreenElement
from ..game.gamedata import color_data, shape_data as shape_model_data, names, titles
from ..game.game2 import Game2
from .collection_window.collectionwindow import CollectionWindow
from .friends_window.friendswindow import FriendsWindow
from .friends_window.friendsprite import FriendSprite
from .notifications_window.notificationswindow import NotificationsWindow
from ..server.connectionmanager import ConnectionManager
from ..server.playerselections import PlayerSelections
from sqlalchemy import create_engine, func, delete, select, case
from sqlalchemy.orm import sessionmaker as session_maker, Session


class Menu():
    def __init__(self):
        # load cursor and background
        self.screen = pygame.display.set_mode((1920, 1080))
        self.background = load("assets/backgrounds/BG1.png").convert_alpha()
        self.office_supplies = load('assets/backgrounds/grid_paper_w_sides_2.png').convert_alpha()
        self.cursor = smoothscale(load("assets/misc/cursor.png").convert_alpha(), (12, 12))
        self.cursor_rect = self.cursor.get_rect()
        self.cursor_rect.center = pygame.mouse.get_pos()

        # update the display
        self.title_text = Text("shapegame", 150, 1920/2, 1080/2)
        self.screen.blit(self.background, (0, 0))
        self.screen.blit(self.title_text.surface, self.title_text.rect)
        pygame.display.set_caption("shapegame")
        pygame.display.update()

        # misc attributes
        self.exit_clicked = False
        self.frames_since_exit_clicked = 0
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font("assets/misc/font.ttf", 80)
        
        self.target_fps = 60
        self.time_step = 1 / self.target_fps
        self.time_step_accumulator = 0
        self.current_time, self.prev_time = None, None
        self.frames = 0

        # database entries
        self.user: User | None = None

        # database session
        # self.engine = create_engine("postgresql://postgres:postgres@172.105.17.177/root/shapegame/shapegame/database.db", echo=False) # server db
        self.engine = create_engine("sqlite:///database.db", echo=False) # local db
        SessionMaker = session_maker(bind=self.engine, autoflush=False)
        self.session = SessionMaker()

        # sprite groups
        self.simple_shapes = Group()

        # windows
        self.collection_window: CollectionWindow | None = None
        self.opponent_window: CollectionWindow | None = None
        self.friends_window: FriendsWindow | None = None
        self.notifications_window: NotificationsWindow | None = None

        self.connection_manager: ConnectionManager | None = None

        self.initSounds()
        self.initScreenElements()

    # INIT HELPERS

    def initSounds(self):
        '''load all sounds'''
        
        self.click_sound = Sound("assets/sounds/click.wav")
        self.start_sound = Sound("assets/sounds/start.wav")
        self.open_sound = Sound("assets/sounds/open.wav")
        self.menu_music = Sound("assets/sounds/menu.wav")
        self.close_sound = Sound("assets/sounds/close.wav")
        self.open_sound.set_volume(.5)
        self.menu_music.set_volume(.25)
        self.close_sound.set_volume(.5)
        self.open_sound.play()

        # start playing menu music on loop
        self.menu_music.play(-1)

    def initScreenElements(self):
        '''create all screen elements'''

        # create all text elements
        self.logged_in_as_text: Text | None = None
        self.title_text = Text("shapegame", 150, 1920/2, 2*1080/3)
        self.play_text = Text("play", 100, 1920/2, 4*1080/5)
        self.connecting_to_text = Text("waiting for opponent..." , 35, 1920/2, 60)

        # create all interactive elements
        self.network_match_clickable = ClickableText("network match", 50, 1920/2 - 200, 975)
        self.local_match_clickable = ClickableText("local match", 50, 1920/2 + 200, 975)
        self.exit_button = Button("exit", 45, [1920 - 25, 1080 - 25])
        self.back_button = Button("back", 45, [25, 1080 - 25])
        self.network_back_button = Button("exit", 45, [1920 - 25, 661 - 25])
        self.connect_to_player_editable = EditableText("Connect to user: ", 30, 0, 0, "topleft")

        # login elements
        self.register_clickable = ClickableText("register", 50, 1920/2, 1030)
        self.login_clickable = ClickableText("login", 50, 1920/2, 925)
        self.or_text = Text("or", 35, 1920/2, 980)
        self.username_editable = EditableText("Username: ", 60, 1920/3-50, 850, max_chars=10)
        self.password_editable = EditableText("Password: ", 60, 2*1920/3+50, 850, max_chars=10)
        self.password_confirm_editable = EditableText("Confirm Password: ", 50, 1920/2, 925, max_chars=10)
        self.bad_credentials_text = Text("user not found!", 50, 1920/2, 600)
        self.bad_credentials_flag = False
        self.bad_credentials_timer = 0

        self.screen_elements: list[ScreenElement] = []
        self.screen_elements.append(self.title_text)
        self.screen_elements.append(self.play_text)
        self.screen_elements.append(self.connecting_to_text)
        self.screen_elements.append(self.network_back_button)
        self.screen_elements.append(self.login_clickable)
        self.screen_elements.append(self.network_match_clickable)
        self.screen_elements.append(self.local_match_clickable)
        self.screen_elements.append(self.exit_button)
        self.screen_elements.append(self.register_clickable)
        self.screen_elements.append(self.username_editable)
        self.screen_elements.append(self.password_editable)
        self.screen_elements.append(self.or_text)
        self.screen_elements.append(self.password_confirm_editable)
        self.screen_elements.append(self.bad_credentials_text)
        self.screen_elements.append(self.back_button)

        # show only title, exit, and login elements
        [element.fastOff() for element in self.screen_elements if element not in [self.title_text]]

    def initNetworkElements(self):

        self.pid = -1
        self.connection_manager: None | ConnectionManager =     None
        self.selections: None | PlayerSelections =              None
        self.opponent: None | User =                            None
        self.opponent_window: None | CollectionWindow =         None

    # WINDOW CALLBACKS

    def startNetwork(self, opponent: Union[User, None] = None, send_notification: bool = False):
        # refresh database
        self.session.commit()
        
        # send notification to challenged user if necessary
        if send_notification: self.addDbNotification(opponent, self.user, CHALLENGE)

        # turn off auxiliary screen elements
        [window.close() for window in [self.friends_window, self.collection_window, self.notifications_window]]
        [window.button.turnOff() for window in [self.friends_window, self.collection_window, self.notifications_window]]
        [element.turnOff() for element in self.screen_elements if element not in [self.title_text, self.logged_in_as_text, self.exit_button]]
        self.connecting_to_text.turnOn()

        if opponent: self.connecting_to_text.updateText(f'waiting for {opponent.username}...')
        else: self.connecting_to_text.updateText(f'waiting for opponent...')

        # create connection manager, send initial communication
        self.connection_manager = ConnectionManager('STANDARD.' if opponent == None else f'P2P.{self.user.username}.{opponent.username}')
        self.pid = self.connection_manager.pid
        self.selections = self.connection_manager.getPlayerSelections()
        self.connection_manager.send(f'USER_{self.user.id}.')


        # do network pregame
        self.network_connected = True
        self.preGame()
        
        # prepare game to be played if still connected
        if self.network_connected:
            # close windows before anything else
            while not self.collection_window.fully_closed or not self.opponent_window.fully_closed:

                self.updateMenuState()
                self.drawScreenElements()
                self.clock.tick(self.target_fps)

            # play game
            if self.pid == 0:
                Game2(
                    self.screen, 
                    self.collection_window.collection_shapes.sprites()[self.collection_window.selected_index].shape_data,
                    self.opponent_window.collection_shapes.sprites()[self.opponent_window.selected_index].shape_data,
                    self.user,
                    self.opponent,
                    self.selections.seed
                ).play()
            else:
                Game2(
                        self.screen, 
                        self.opponent_window.collection_shapes.sprites()[self.opponent_window.selected_index].shape_data,
                        self.collection_window.collection_shapes.sprites()[self.collection_window.selected_index].shape_data,
                        self.opponent,
                        self.user,
                        self.selections.seed
                    ).play()

            # clear time accumulation
            self.prev_time = time.time()

            # idle while waiting for results
            while self.selections.winner == None:
                self.selections = self.connection_manager.getPlayerSelections()
                self.updateMenuState()
                self.drawScreenElements()
                self.clock.tick(self.target_fps)

        # do network post game if still connected
        # if self.network_connected:
        #     self.postGame()

        if not self.selections.kill[self.pid]: self.connection_manager.send('KILL.')

        # prepare to go back to the menu
        self.collection_window.changeModeTransition()
        if self.opponent_window: self.opponent_window.changeModeTransition()

        # if pregame was abandoned, wait for windows to close before returning to menu
        while not self.collection_window.fully_closed:
            self.updateMenuState()
            self.drawScreenElements()
            self.clock.tick(self.target_fps)

        # prepare to go back to the menu
        self.collection_window.changeModeCollection()
        if self.opponent_window: self.opponent_window.changeModeCollection()

        # delete what needs to be deleted
        # if self.connection_manager: del self.connection_manager
        if self.opponent_window: del self.opponent_window
        self.connection_manager = None
        self.opponent_window = None

        # turn on/off auxiliary screen elements
        [window.button.turnOn() for window in [self.friends_window, self.collection_window, self.notifications_window]]
        [element.turnOn() for element in [self.play_text, self.logged_in_as_text, self.network_back_button, self.local_match_clickable, self.network_match_clickable, self.exit_button]]
        self.network_back_button.turnOff()

    def preGame(self):
        '''wait for user to connect and make selections'''

        # while awaiting opponent
        while (self.selections == None or self.selections.user_ids[0 if self.pid == 1 else 1] == -1 or any(not window.fully_closed for window in [self.friends_window, self.collection_window, self.notifications_window])) and self.network_connected:
            self.selections = self.connection_manager.getPlayerSelections()

            self.updateMenuState()
            self.drawScreenElements()
            self.clock.tick(self.target_fps)

        # search for opponent, create collection window
        if self.network_connected:
            self.session.commit()
            self.opponent = self.session.query(User).filter(User.id == int(self.selections.user_ids[0 if self.pid == 1 else 1])).first()
            self.opponent_window = CollectionWindow(self.opponent, self.session, True)

            self.opponent_window.changeModeNetwork(self.connection_manager)
            self.collection_window.changeModeNetwork(self.connection_manager)
            self.network_back_button.turnOn()

            # clear time accumulation
            self.prev_time = time.time()

        self.connecting_to_text.turnOff()

        # players connected to each other, making selections
        while self.network_connected:
            self.selections = self.connection_manager.getPlayerSelections()

            # break if other player disconnected
            if self.selections.kill[0 if self.pid == 1 else 1]:
                self.network_connected = False

            # update state
            self.updateMenuState()
            self.drawScreenElements()
            self.clock.tick(self.target_fps)

            # check if game is ready to be played
            if (self.selections.players_ready[0] == self.selections.players_ready[1] == True) and self.selections.seed != None: break

        # close windows
        if self.opponent_window:
            self.collection_window.toggle()
            self.opponent_window.toggle()
            self.network_back_button.turnOff()

    def postGame(self):
        self.session.commit()
        
        # prepare windows for post game animation
        windows = [self.opponent_window, self.collection_window]
        for window in windows:
            window.toggle()
            window.nameplate.disable()
            window.selector.disable()

        # winner_window = self.collection_window if self.selections.winner == self.pid else self.opponent_window
        # winner_window.selector.setSelected(0)
        # while winner_window.selected_index > winner_window.selector.selected_index:
            
        #     winner_window.selected_index -= 1
        #     [sprite.moveRight() for sprite in winner_window.collection_shapes.sprites()]
        
        # give windows time to open
        pause_start = time.time()
        while time.time() - pause_start < 1:
            # update state
            self.updateMenuState()
            self.drawScreenElements()
        
        # move all shapes back to original position
        if self.selections.winner == self.pid:
            self.collection_window.moveSpritesHome()
        else:
            self.opponent_window.moveSpritesHome()

        # give shapes time to move
        pause_start = time.time()
        while time.time() - pause_start < 1:
            # update state
            self.updateMenuState()
            self.drawScreenElements()
            self.clock.tick(self.target_fps)

        # shuffle shape between groups
        if self.selections.winner == self.pid:
            shape_data = self.opponent_window.selected_shape.shape_data
            self.opponent_window.removeSelectedShape()
            self.collection_window.addShapeToCollection(shape_data)
        else:
            shape_data = self.collection_window.selected_shape.shape_data
            self.collection_window.removeSelectedShape()
            self.opponent_window.addShapeToCollection(shape_data)

        # give time to animate shape shuffle
        pause_start = time.time()
        while time.time() - pause_start < 5:
            # update state
            self.updateMenuState()
            self.drawScreenElements()
            self.clock.tick(self.target_fps)

        # prepare windows to return to main menu
        for window in windows:
            window.toggle()
            window.nameplate.enable()
            window.selector.enable()

        # hold while windows are open
        while not self.collection_window.fully_closed:
            # update state
            self.updateMenuState()
            self.drawScreenElements()
            self.clock.tick(self.target_fps)

    def addFriend(self, username):
        '''add friend relationship in the database'''

        # lower flags
        self.friends_window.already_following_flag = False
        self.friends_window.bad_credentials_flag = False
        self.friends_window.thats_you_flag = False

        # query db for user
        try:
            searched_user = self.session.query(User).filter(User.username == username).one()
        except Exception as e:
            self.friends_window.bad_credentials_flag = True
            print(f"Could not add friend, none found: {e}")
            return

        # raise flags
        self.friends_window.already_following_flag = any(friend.username == username for friend in self.user.friends)
        self.friends_window.thats_you_flag = searched_user.username == self.user.username
        if self.friends_window.already_following_flag or self.friends_window.thats_you_flag: return

        # add searched user to user friends and create notification
        try:
            searched_user = self.session.query(User).filter(User.username == username).one()

            # if user is already in the searched users friends, send friend confirmation notification
            if any(friend.username == self.user.username for friend in searched_user.friends):                
                self.addDbNotification(searched_user, self.user, FRIEND_CONFIRM)

            else: 
                self.addDbNotification(searched_user, self.user, FRIEND_ADD)
            
            self.user.friends.append(searched_user)
            self.session.commit()

            self.friends_window.checkFriendsUpdate()

        except Exception as e:
            self.session.rollback()
            print(f'Error creating notification: {e}')
            return

    def addDbNotification(self, owner: User, sender: User, type: str):
        '''create and add notification to the database (if a similar notification doesn't already exist)'''

        if any((notification.type == type) and (notification.sender == sender) for notification in owner.notifications_owned): return

        self.session.add(Notification(owner, sender, type))

    # PLAY HELPERS

    def loginLoop(self):
        '''run the game loop for the login/register screen'''

        # start the time for accumulator
        self.prev_time = time.time()

        while self.user == None:
            self.updateMenuState()

            self.drawScreenElements()

            self.clock.tick(self.target_fps)

        # turn on/off screen elements
        turn_off = [self.username_editable, self.password_editable, self.login_clickable, self.register_clickable, self.password_editable, self.password_confirm_editable, self.or_text, self.back_button]
        turn_on = [self.play_text, self.network_match_clickable, self.local_match_clickable, self.exit_button, self.logged_in_as_text, self.friends_window.button, self.notifications_window.button, self.collection_window.button]
        
        [element.turnOff() for element in turn_off]
        [element.turnOn() for element in turn_on]

        self.prev_time = time.time()

    def checkUserLoggingIn(self, mouse_pos):
        '''check if user is logging in'''
        if not (self.user == None and self.login_clickable.isHovAndEnabled(mouse_pos)): return
        
        # Get entered username and password
        username = self.username_editable.getText()
        password = self.password_editable.getText()
        
        try:
            # Query for user with matching username and password
            user = self.session.query(User).filter(User.username == username).first()

            if user and user.check_password(password):
                # Login successful
                self.user = user
                self.logged_in_as_text = Text(f'logged in as: {self.user.username}', 35, 1920/2, 20, fast_off=True)
                self.screen_elements.append(self.logged_in_as_text)

                # Initialize windows after successful login
                self.collection_window = CollectionWindow(self.user, self.session)
                self.friends_window = FriendsWindow(self.user, self.session, self.addFriend, self.startNetwork)
                self.notifications_window = NotificationsWindow(self.user, self.session, self.addFriend, self.startNetwork)

                print('login successful')
            else:
                # provide feedback on what went wrong
                if user == None:
                    self.bad_credentials_text.updateText("user not found!")
                    self.bad_credentials_flag = True
                else:
                    self.bad_credentials_text.updateText("incorrect password!")
                    self.bad_credentials_flag = True

        except Exception as e:
            print(f"Login error: {e}")
            self.bad_credentials_flag = True

    def checkUserRegistering(self, mouse_pos):
        '''check if user is registering'''
        if not (self.user == None and self.register_clickable.isHovAndEnabled(mouse_pos)): return
                
        # if user is at inital screen, turn off login elements
        if not self.login_clickable.disabled:
            [element.turnOff() for element in [self.login_clickable, self.or_text]]
            self.password_confirm_editable.turnOn()
            self.back_button.turnOn()
        
        # if user is at register screen, attempt to register
        else:
            username = self.username_editable.getText()
            password = self.password_editable.getText()
            password_confirm = self.password_confirm_editable.getText()

            try:
                # Validate username length
                if len(username) < 3:
                    self.bad_credentials_text.updateText("username must be at least 3 characters!")
                    self.bad_credentials_flag = True
                    return

                # Validate password length
                if len(password) < 8:
                    self.bad_credentials_text.updateText("password must be 8-10 characters long!")
                    self.bad_credentials_flag = True
                    return

                # Check if username already exists
                existing_user = self.session.query(User).filter(User.username == username).first()
                if existing_user:
                    self.bad_credentials_text.updateText("username taken!")
                    self.bad_credentials_flag = True
                    return
                
                # Validate passwords match
                if password != password_confirm:
                    self.bad_credentials_text.updateText("passwords don't match!")
                    self.bad_credentials_flag = True
                    return

                # Create new user
                new_user = User(username=username, password=password)
                self.session.add(new_user)
                self.session.commit()

                new_shape = generateRandomShape(new_user, self.session)
                new_user.favorite_id = new_shape.id
                self.session.commit()

                # Log in as new user
                self.user = new_user
                self.logged_in_as_text = Text(f'logged in as: {self.user.username}', 35, 1920/2, 20, fast_off=True)
                self.screen_elements.append(self.logged_in_as_text)

                # Initialize windows for new user
                self.collection_window = CollectionWindow(self.user, self.session)
                self.friends_window = FriendsWindow(self.user, self.session, self.addFriend, self.startNetwork)
                self.notifications_window = NotificationsWindow(self.user, self.session, self.addFriend, self.startNetwork)

            except Exception as e:
                print(f"Registration error: {e}")
                self.bad_credentials_flag = True

    def handleInputs(self, mouse_pos, events):
        '''handle any inputs from the user'''

        for event in events:
            if event.type != MOUSEBUTTONDOWN or event.button != 1: return

            self.click_sound.play()

            # check if user attempting to login
            self.checkUserLoggingIn(mouse_pos)

            # check if user attempting to register
            self.checkUserRegistering(mouse_pos)
            
            # quit network matchmaking
            if self.network_back_button.isHovAndEnabled(mouse_pos):
                self.network_connected = False

            # if exit/back button clicked while in register screen, go back to login screen
            if (self.exit_button.isHovAndEnabled(mouse_pos) and not self.back_button.disabled) or (self.back_button.isHovAndEnabled(mouse_pos)):
                self.password_confirm_editable.turnOff()
                self.back_button.turnOff()
                self.or_text.turnOn()
                self.login_clickable.turnOn()
                
            # quit game
            elif self.exit_button.isHovAndEnabled(mouse_pos):


                # if any window is open, do not exit
                if self.collection_window:
                    if any(window.opened for window in [self.notifications_window, self.collection_window]): continue

                if self.connection_manager: 
                    self.connection_manager.send('KILL.')
                    self.network_connected = False
                
                else:
                    self.close_sound.play()
                    self.exit_clicked = True
                    pygame.mixer.Sound.fadeout(self.menu_music, 1000)

                    [element.deselect() for element in self.screen_elements if isinstance(element, EditableText)]
                    [element.turnOff() for element in self.screen_elements if element not in [self.title_text]]
                    [element.button.turnOff() for element in [self.friends_window, self.notifications_window, self.collection_window] if element != None]

            # handle window interactions, if windows exist
            if self.collection_window:
                # if one window is being opened, close any windows that overlap
                side_windows = [self.friends_window, self.notifications_window]
                if self.collection_window.isButtonHovered(mouse_pos):
                    [window.close() for window in side_windows]
                elif any(window.isButtonHovered(mouse_pos) for window in side_windows):
                    self.collection_window.close()

                # if no window is clicked and not in pregame, close all windows
                windows = [self.collection_window, self.friends_window, self.notifications_window]
                if not any(window.rect.collidepoint(mouse_pos) for window in windows) and not self.opponent_window:
                    [window.close() for window in windows]
                
    def updateMenuState(self):
        '''progress the menu state by one tick'''

        self.current_time = time.time()

        self.time_step_accumulator += self.current_time - self.prev_time
        while self.time_step_accumulator >= self.time_step:
            self.time_step_accumulator -= self.time_step

            self.frames += 1
            self.updateScreenElements()

        self.prev_time = self.current_time

        if self.frames % 120 == 0:
            self.session.commit()

            if self.friends_window: self.friends_window.checkFriendsUpdate()
            if self.notifications_window: self.notifications_window.checkNotificationsUpdate()


        if self.exit_clicked:
            self.frames_since_exit_clicked += 1

            if self.frames_since_exit_clicked == self.target_fps: sys.exit()

    def updateScreenElements(self):
        '''update all elements on the screen'''

        mouse_pos = pygame.mouse.get_pos()
        events = pygame.event.get()

        self.handleInputs(mouse_pos, events)

        self.cursor_rect.center = mouse_pos

        # [text.update() for text in self.texts]
        # [clickable.update(events, mouse_pos) for clickable in self.clickables if clickable not in [None]]
        # [editable.update(events, mouse_pos) for editable in self.login_editables]
        [element.update(events, mouse_pos) for element in self.screen_elements]

        # update sprites
        self.simple_shapes.update()
        if self.collection_window: self.collection_window.update(mouse_pos, events)
        if self.friends_window: self.friends_window.update(mouse_pos, events)
        if self.notifications_window: self.notifications_window.update(mouse_pos, events)
        if self.opponent_window: self.opponent_window.update(mouse_pos, events)

    def drawScreenElements(self):
        '''draw all elements to the screen'''

        # flip the display
        pygame.display.flip()

        # draw background
        self.screen.blit(self.background, (0, 0))

        # draw screen elements
        for element in self.screen_elements: element.draw(self.screen)

        # draw windows if they exist
        if self.collection_window: self.collection_window.draw(self.screen)
        if self.friends_window: self.friends_window.draw(self.screen)
        if self.notifications_window: self.notifications_window.draw(self.screen)
        if self.opponent_window: self.opponent_window.draw(self.screen)


        # draw bad credentials text if flag is true, and handle timer
        if self.bad_credentials_flag:
            self.bad_credentials_text.turnOn()

            self.bad_credentials_timer += 1
            if self.bad_credentials_timer == 200:
                self.bad_credentials_flag = False
                self.bad_credentials_timer = 0
                self.bad_credentials_text.turnOff()

        self.screen.blit(self.cursor, self.cursor_rect)

    def pauseFor(self, seconds):
        '''pause the game for a given number of seconds'''

        start_time = time.time()
        while time.time() - start_time < seconds:
            self.updateMenuState()
            self.drawScreenElements()
            self.clock.tick(self.target_fps)

    def play(self, username = 'pat'):
        '''run the game loop for the main menu'''
        # start the time for accumulator
        self.prev_time = time.time()

        self.pauseFor(1)
        [element.turnOn() for element in [self.username_editable, self.password_editable, self.login_clickable, self.register_clickable, self.or_text, self.exit_button]]

        self.loginLoop()

        while True:
            self.updateMenuState()

            self.drawScreenElements()

            self.clock.tick(self.target_fps)
