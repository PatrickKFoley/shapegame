from pygame.locals import *
import pygame.mouse
from pygame.sprite import Group
from pygame.mixer import Sound
from pygame.transform import smoothscale
from pygame.image import load
import pygame, time, itertools, sys, random

from createdb import User, Shape as ShapeData
from ..screen_elements.text import Text
from ..screen_elements.editabletext import EditableText
from ..screen_elements.clickabletext import ClickableText
from ..screen_elements.button import Button
from ..game.gamedata import color_data, shape_data as shape_model_data, names, titles
from .collection_window.collectionwindow import CollectionWindow
from .friendswindow import FriendsWindow
from .notificationswindow import NotificationsWindow
from sqlalchemy import create_engine, func, delete, select, case
from sqlalchemy.orm import sessionmaker as session_maker, Session


class Menu():
    def __init__(self):
        # load cursor and background
        self.screen = pygame.display.set_mode((1920, 1080))
        self.background = load("assets/backgrounds/BG1.png").convert_alpha()
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

        # database entries
        self.user: User | None = None

        # database session
        # self.engine = create_engine("postgresql://postgres:postgres@172.105.17.177/root/shapegame/shapegame/database.db", echo=False) # server db
        self.engine = create_engine("sqlite:///database.db", echo=False) # local db
        SessionMaker = session_maker(bind=self.engine, autoflush=False)
        self.session = SessionMaker()

        # sprite groups
        self.simple_shapes = Group()

        self.collection_window: CollectionWindow | None = None
        self.friends_window: FriendsWindow | None = None
        self.notifications_window: NotificationsWindow | None = None

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

        self.texts: list[Text] = []
        self.texts.append(self.title_text)
        self.texts.append(self.play_text)
        self.texts.append(self.bad_credentials_text)

        # create all interactive elements
        self.network_match_clickable = ClickableText("network match", 50, 1920/2 - 200, 975)
        self.local_match_clickable = ClickableText("local match", 50, 1920/2 + 200, 975)
        self.exit_button = Button("exit", 45, [1920 - 25, 1080 - 25])
        self.register_clickable = ClickableText("register", 50, 1920 / 2, 1050)
        self.username_editable = EditableText("Username: ", 60, 1920/2, 950)
        self.connect_to_player_editable = EditableText("Connect to user: ", 30, 0, 0, "topleft")
        self.username_editable.select()

        self.clickables: list[ClickableText] = []
        self.clickables.append(self.network_match_clickable)
        self.clickables.append(self.local_match_clickable)
        self.clickables.append(self.exit_button)
        self.clickables.append(self.register_clickable)

    # PLAY HELPERS

    def loginLoop(self):
        '''run the game loop for the login/register screen'''

    def handleInputs(self, mouse_pos, events):
        '''handle any inputs from the user'''

        for event in events:
            if event.type != MOUSEBUTTONDOWN or event.button != 1: return

            self.click_sound.play()

            if self.exit_button.rect.collidepoint(mouse_pos) and not any(window.opened for window in [self.notifications_window, self.collection_window]):
                self.close_sound.play()
                self.exit_clicked = True
                pygame.mixer.Sound.fadeout(self.menu_music, 1000)

    def updateMenuState(self):
        '''progress the menu state by one tick'''

        self.current_time = time.time()

        self.time_step_accumulator += self.current_time - self.prev_time
        while self.time_step_accumulator >= self.time_step:
            self.time_step_accumulator -= self.time_step

            self.updateScreenElements()

        self.prev_time = self.current_time

        if self.exit_clicked:
            self.frames_since_exit_clicked += 1

            if self.frames_since_exit_clicked == self.target_fps: sys.exit()

    def updateScreenElements(self):
        '''update all elements on the screen'''

        mouse_pos = pygame.mouse.get_pos()
        events = pygame.event.get()

        self.handleInputs(mouse_pos, events)

        self.cursor_rect.center = mouse_pos

        # update clickable elements
        for clickable in self.clickables:
            if clickable not in [None, self.register_clickable]:
                clickable.update(mouse_pos)

        # update sprites
        self.simple_shapes.update()
        self.collection_window.update(mouse_pos, events)
        self.friends_window.update(mouse_pos, events)
        self.notifications_window.update(mouse_pos, events)

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
        self.screen.blit(self.cursor, self.cursor_rect)

    def play(self):
        '''run the game loop for the main menu'''

        # the login loop would replace this
        self.user = self.session.query(User).filter(User.username == 'pat').one()
        self.logged_in_as_text = Text(f'logged in as: {self.user.username}', 35, 1920/2, 20)
        self.texts.append(self.logged_in_as_text)
        
        self.collection_window = CollectionWindow(self.user, self.session)
        self.friends_window = FriendsWindow(self.user, self.session)
        self.notifications_window = NotificationsWindow(self.user, self.session)

        # start the time for accumulator
        self.prev_time = time.time()

        while True:
            self.updateMenuState()

            self.drawScreenElements()

            # self.clock.tick(self.target_fps)
            self.clock.tick()
