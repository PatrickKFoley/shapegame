from pygame.locals import *
import pygame.mouse
from pygame.sprite import Group
from pygame.mixer import Sound
from pygame.surface import Surface
from pygame.transform import smoothscale
from pygame.image import load
import pygame, time, itertools, sys, random
from typing import Union

from createdb import User, Shape as ShapeData, Notification, FRIEND_ADD, FRIEND_CONFIRM, CHALLENGE
from ..screen_elements.text import Text
from ..screen_elements.editabletext import EditableText
from ..screen_elements.clickabletext import ClickableText
from ..screen_elements.button import Button
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
        self.initTexts()

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

    def initTexts(self):
        '''create all text elements'''

        self.logged_in_as_text: Text | None = None
        self.title_text = Text("shapegame", 150, 1920/2, 2*1080/3)
        self.play_text = Text("play", 100, 1920/2, 4*1080/5)
        self.bad_credentials_text = Text("user not found!", 150, 1920/2, 800)
        self.connecting_to_text = Text("waiting for opponent..." , 35, 1920/2, 60)

        self.texts: list[Text] = []
        self.texts.append(self.title_text)
        self.texts.append(self.play_text)
        self.texts.append(self.bad_credentials_text)
        self.texts.append(self.connecting_to_text)

        # create all interactive elements
        self.network_match_clickable = ClickableText("network match", 50, 1920/2 - 200, 975)
        self.local_match_clickable = ClickableText("local match", 50, 1920/2 + 200, 975)
        self.exit_button = Button("exit", 45, [1920 - 25, 1080 - 25])
        self.network_back_button = Button("exit", 45, [1920 - 25, 661 - 25])
        self.register_clickable = ClickableText("register", 50, 1920 / 2, 1050)
        self.username_editable = EditableText("Username: ", 60, 1920/2, 950)
        self.connect_to_player_editable = EditableText("Connect to user: ", 30, 0, 0, "topleft")
        self.username_editable.select()

        self.clickables: list[ClickableText] = []
        self.clickables.append(self.network_back_button)
        self.clickables.append(self.network_match_clickable)
        self.clickables.append(self.local_match_clickable)
        self.clickables.append(self.exit_button)
        self.clickables.append(self.register_clickable)

        for element in [self.network_back_button, self.connecting_to_text]:
            element.turnOff()
            element.alpha = 0
            element.surface.set_alpha(0)

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
        [text.turnOff() for text in self.texts if text not in [self.title_text, self.logged_in_as_text]]
        [clickable.turnOff() for clickable in self.clickables if clickable != self.exit_button]
        self.connecting_to_text.turnOn()

        if opponent: self.connecting_to_text.updateText(f'waiting for {opponent.username}...')
        else: self.connecting_to_text.updateText(f'waiting for opponent...')

        # create connection manager, send initial communication
        self.connection_manager = ConnectionManager('STANDARD.' if opponent == None else f'P2P.{self.user.username}.{opponent.username}')
        self.pid = self.connection_manager.pid
        self.selections = self.connection_manager.getPlayerSelections()
        self.connection_manager.send(f'USER_{self.user.id}.')

        # wait for opponent to connect
        self.network_connected = True
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

        # turn on auxiliary screen elements
        [window.button.turnOn() for window in [self.friends_window, self.collection_window, self.notifications_window]]
        [text.turnOn() for text in self.texts if text not in [self.connecting_to_text, self.title_text]]
        [clickable.turnOn() for clickable in self.clickables if clickable not in [self.exit_button, self.network_back_button]]

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

    def handleInputs(self, mouse_pos, events):
        '''handle any inputs from the user'''

        for event in events:
            if event.type != MOUSEBUTTONDOWN or event.button != 1: return

            self.click_sound.play()

            if self.network_back_button.rect.collidepoint(mouse_pos) and not self.network_back_button.disabled:
                self.network_connected = False

            # quit game
            if self.exit_button.rect.collidepoint(mouse_pos) and not any(window.opened for window in [self.notifications_window, self.collection_window]):

                if self.connection_manager: 
                    self.connection_manager.send('KILL.')
                    self.network_connected = False
                
                else:
                    self.close_sound.play()
                    self.exit_clicked = True
                    pygame.mixer.Sound.fadeout(self.menu_music, 1000)

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

            self.friends_window.checkFriendsUpdate()
            self.notifications_window.checkNotificationsUpdate()

        if self.exit_clicked:
            self.frames_since_exit_clicked += 1

            if self.frames_since_exit_clicked == self.target_fps: sys.exit()

    def updateScreenElements(self):
        '''update all elements on the screen'''

        mouse_pos = pygame.mouse.get_pos()
        events = pygame.event.get()

        self.handleInputs(mouse_pos, events)

        self.cursor_rect.center = mouse_pos

        [text.update() for text in self.texts]
        [clickable.update(mouse_pos) for clickable in self.clickables if clickable not in [None, self.register_clickable]]

        # update sprites
        self.simple_shapes.update()
        self.collection_window.update(mouse_pos, events)
        self.friends_window.update(mouse_pos, events)
        self.notifications_window.update(mouse_pos, events)

        if self.opponent_window != None: 
            self.opponent_window.update(mouse_pos, events)

    def drawScreenElements(self):
        '''draw all elements to the screen'''

        # flip the display
        pygame.display.flip()

        # draw background
        self.screen.blit(self.background, (0, 0))

        # draw text elements
        for element in itertools.chain(self.texts, self.clickables):
            if element not in [None, self.register_clickable, self.bad_credentials_text]:
                self.screen.blit(element.surface, element.rect)

        self.screen.blit(self.collection_window.surface, self.collection_window.rect)
        self.screen.blit(self.friends_window.surface, self.friends_window.rect)
        self.screen.blit(self.notifications_window.surface, self.notifications_window.rect)

        if self.opponent_window != None: 
            self.screen.blit(self.opponent_window.surface, self.opponent_window.rect)

        self.screen.blit(self.cursor, self.cursor_rect)

    def play(self, username = 'pat'):
        '''run the game loop for the main menu'''

        # the login loop would replace this
        self.user = self.session.query(User).filter(User.username == username).one()
        self.logged_in_as_text = Text(f'logged in as: {self.user.username}', 35, 1920/2, 20)
        self.texts.append(self.logged_in_as_text)
        
        self.collection_window = CollectionWindow(self.user, self.session)
        self.friends_window = FriendsWindow(self.user, self.session, self.addFriend, self.startNetwork)
        self.notifications_window = NotificationsWindow(self.user, self.session, self.addFriend, self.startNetwork)

        # start the time for accumulator
        self.prev_time = time.time()

        while True:
            self.updateMenuState()

            self.drawScreenElements()

            self.clock.tick(self.target_fps)
