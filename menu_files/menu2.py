from pygame.locals import *
import pygame.mouse
from pygame.sprite import Group
from pygame.mixer import Sound
import pygame, time, itertools, sys

from createdb import User, Shape as ShapeData
from screen_elements.text import Text
from screen_elements.editabletext import EditableText
from screen_elements.clickabletext import ClickableText
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker as session_maker

class Menu():
    def __init__(self):
        # load cursor and background
        self.screen = pygame.display.set_mode((1920, 1080))
        self.background = pygame.image.load("backgrounds/BG1.png").convert_alpha()
        self.cursor = pygame.transform.smoothscale(pygame.image.load("backgrounds/cursor.png").convert_alpha(), (12, 12))
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
        self.font = pygame.font.Font("backgrounds/font.ttf", 80)
        
        self.target_fps = 60
        self.time_step = 1 / self.target_fps
        self.time_step_accumulator = 0
        self.current_time, self.prev_time = None, None

        # database entries
        self.user: User | None = None

        # database session
        # self.engine = create_engine("postgresql://postgres:postgres@172.105.17.177/root/shapegame/shapegame/database.db", echo=False) # server db
        self.engine = create_engine("sqlite:///database.db", echo=False) # local db
        SessionMaker = session_maker(bind=self.engine)
        self.session = SessionMaker()

        # sprite groups
        self.simple_shapes = Group()

        self.initSounds()
        self.initTexts()
        self.initCollectionWindow() 

    # INIT HELPERS

    def initSounds(self):
        '''load all sounds'''
        
        self.click_sound = Sound("sounds/click.wav")
        self.start_sound = Sound("sounds/start.wav")
        self.open_sound = Sound("sounds/open.wav")
        self.menu_music = Sound("sounds/menu.wav")
        self.close_sound = Sound("sounds/close.wav")
        self.open_sound.set_volume(.5)
        self.menu_music.set_volume(.5)
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
        self.exit_clickable = ClickableText("exit", 50, 1870, 1045)
        self.register_clickable = ClickableText("register", 50, 1920 / 2, 1050)
        self.username_editable = EditableText("Username: ", 60, 1920/2, 950)
        self.connect_to_player_editable = EditableText("Connect to user: ", 30, 0, 0, "topleft")
        self.username_editable.select()

        self.clickables: list[ClickableText] = []
        self.clickables.append(self.network_match_clickable)
        self.clickables.append(self.local_match_clickable)
        self.clickables.append(self.exit_clickable)
        self.clickables.append(self.register_clickable)

    def initCollectionWindow(self):
        '''create the bottom collection window'''
        icon_size = [50, 50]

        self.shapes_icon = pygame.transform.smoothscale(pygame.image.load('backgrounds/shapes_icon.png').convert_alpha(), icon_size)
        self.shapes_icon_selected = pygame.transform.smoothscale(pygame.image.load('backgrounds/shapes_icon_selected.png').convert_alpha(), icon_size)
        self.shapes_icon_current = self.shapes_icon
        self.shapes_icon_rect = self.shapes_icon_current.get_rect()
        self.shapes_icon_rect.center = [25, 1055]

        self.shapes_background = pygame.image.load('backgrounds/collection_window.png').convert_alpha()
        self.shapes_background_rect = self.shapes_background.get_rect()
        self.shapes_background_rect.topleft = [0, 1080]

        self.shapes_background_y = 1080
        self.shapes_background_next_y = 1080
        self.shapes_background_v = 0
        self.shapes_background_a = 1.5
        self.shapes_background_shown = False

    # PLAY HELPERS

    def loginLoop(self):
        '''run the game loop for the login/register screen'''

    def handleInputs(self):
        '''handle any inputs from the user'''

        mouse_pos = pygame.mouse.get_pos()
        events = pygame.event.get()

        for event in events:
            if event.type != MOUSEBUTTONDOWN: return

            self.click_sound.play()

            if self.exit_clickable.rect.collidepoint(mouse_pos):
                self.close_sound.play()
                self.exit_clicked = True
                pygame.mixer.Sound.fadeout(self.menu_music, 1000)

            elif self.shapes_icon_rect.collidepoint(mouse_pos):
                self.shapes_background_shown = not self.shapes_background_shown

                if self.shapes_background_shown: self.shapes_background_next_y = 1080 - self.shapes_background.get_size()[1]
                else: self.shapes_background_next_y = 1080

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
        self.cursor_rect.center = mouse_pos

        # update clickable elements
        for clickable in self.clickables:
            if clickable not in [None, self.register_clickable]:
                clickable.update(mouse_pos)

        # update sprites
        self.simple_shapes.update()

        self.updateCollectionWindow()
        
    def updateCollectionWindow(self):
        '''update position of the collection window'''
        mouse_pos = pygame.mouse.get_pos()
        
        # update icon
        self.shapes_icon_current = self.shapes_icon_selected if self.shapes_icon_rect.collidepoint(mouse_pos) else self.shapes_icon

        # update window positions
        if self.shapes_background_y == self.shapes_background_next_y: return
        
        # calculate the remaining distance to the target
        distance = abs(self.shapes_background_y - self.shapes_background_next_y)

        # apply acceleration while far from the target, decelerate when close
        if distance > 50:
            self.shapes_background_v += self.shapes_background_a
        else:
            self.shapes_background_v = max(1, distance * 0.2)

        # move the window towards the target position, snap in place if position is exceeded
        if self.shapes_background_y > self.shapes_background_next_y:
            self.shapes_background_y -= self.shapes_background_v

            if self.shapes_background_y < self.shapes_background_next_y:
                self.shapes_background_y = self.shapes_background_next_y

        elif self.shapes_background_y < self.shapes_background_next_y:
            self.shapes_background_y += self.shapes_background_v
            
            if self.shapes_background_y > self.shapes_background_next_y:
                self.shapes_background_y = self.shapes_background_next_y 

        # reset the velocity when the window reaches its target
        if self.shapes_background_y == self.shapes_background_next_y:
            self.shapes_background_v = 0

        self.shapes_background_rect.topleft = [0, self.shapes_background_y]
        self.shapes_icon_rect.center = [25, self.shapes_background_y - 25]

    def drawScreenElements(self):
        '''draw all elements to the screen'''

        # flip the display
        pygame.display.flip()

        # draw background
        self.screen.blit(self.background, (0, 0))

        # draw sprites
        self.simple_shapes.draw(self.screen)

        # draw text elements
        for element in itertools.chain(self.texts, self.clickables):
            if element not in [None, self.register_clickable, self.bad_credentials_text]:
                self.screen.blit(element.surface, element.rect)

        # draw icons
        self.screen.blit(self.shapes_icon_current, self.shapes_icon_rect)

        # draw windows
        self.screen.blit(self.shapes_background, self.shapes_background_rect)

        self.screen.blit(self.cursor, self.cursor_rect)

    def play(self):
        '''run the game loop for the main menu'''

        # the login loop would replace this
        self.user = self.session.query(User).filter(User.username == 'a').one()

        # start the time for accumulator
        self.prev_time = time.time()

        while True:

            self.handleInputs()

            self.updateMenuState()

            self.updateMenuState()

            self.drawScreenElements()

            self.clock.tick(self.target_fps)


