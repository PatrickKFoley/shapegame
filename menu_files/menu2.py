from pygame.locals import *
import pygame.mouse
from pygame.sprite import Group
from pygame.mixer import Sound
from pygame.transform import smoothscale
from pygame.surface import Surface
from pygame.image import load
import pygame, time, itertools, sys

from createdb import User, Shape as ShapeData
from screen_elements.text import Text
from screen_elements.editabletext import EditableText
from screen_elements.clickabletext import ClickableText
from game_files.colordata import color_data
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker as session_maker

class CollectionShape(pygame.sprite.Sprite):
    def __init__(self, shape_data: ShapeData, position: int):
        super().__init__()

        self.shape_data = shape_data
        self.position = position
        
        self.x = 750 + position * 220
        self.y = 882
        self.next_x = self.x
        self.v = 0
        self.a = 1.5

        self.generateSurfaces()

    def generateSurfaces(self):
        '''generate the surfaces for window stats, additional info, and shape image'''

        # shape image
        self.face_image = smoothscale(load(f'shape_images/faces/{self.shape_data.type}/{self.shape_data.face_id}/0.png').convert_alpha(), [190, 190])

        self.image = color_data[self.shape_data.color_id].circle_image
        if self.shape_data.type == 'triangle':
            self.image = color_data[self.shape_data.color_id].triangle_image
        elif self.shape_data.type == 'square':
            self.image = color_data[self.shape_data.color_id].square_image
        self.image = smoothscale(self.image, [190, 190])

        self.image.blit(self.face_image, [0, 0])

        self.rect = self.image.get_rect()
        self.rect.center = [self.x, 1300]

        # stats surface
        self.stats_surface = Surface([570, 440], pygame.SRCALPHA, 32)
        self.stats_rect = self.stats_surface.get_rect()
        self.stats_rect.topleft = [50, 900]

        level = Text('level:', 16, 100, 50, 'topleft')

        self.stats_surface.blit(level.surface, level.rect)

    def moveLeft(self):
        self.next_x -= 100

    def moveRight(self):
        self.next_x += 100

    def update(self):
        # move into place
        if self.x == self.next_x: return

        # calculate the remaining distance to the target
        distance = abs(self.x - self.next_x)

        # apply acceleration while far from the target, decelerate when close
        if distance > 50:
            self.v += self.a
        else:
            self.v = max(1, distance * 0.2)

        # move the window towards the target position, snap in place if position is exceeded
        if self.x > self.next_x:
            self.x -= self.v

            if self.x < self.next_x:
                self.x = self.next_x

        elif self.x < self.next_x:
            self.x += self.v
            
            if self.x > self.next_x:
                self.x = self.next_x 

        # reset the velocity when the window reaches its target
        if self.x == self.next_x:
            self.v = 0

        self.rect.center = [self.x, self.y]

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
        self.collection_shapes = Group()

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

    def initCollectionGroup(self):
        for count, shape_data in enumerate(self.user.shapes):
            print(count)
            self.collection_shapes.add(CollectionShape(shape_data, count))

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

        for shape in self.collection_shapes:
            shape.rect.center = [shape.x, self.shapes_background_y + 220]

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

        # draw windows
        self.screen.blit(self.shapes_background, self.shapes_background_rect)

        # draw sprites
        self.simple_shapes.draw(self.screen)
        self.collection_shapes.draw(self.screen)

        # draw icons
        self.screen.blit(self.shapes_icon_current, self.shapes_icon_rect)

        self.screen.blit(self.cursor, self.cursor_rect)

    def play(self):
        '''run the game loop for the main menu'''

        # the login loop would replace this
        self.user = self.session.query(User).filter(User.username == 'a').one()

        self.initCollectionGroup()

        # start the time for accumulator
        self.prev_time = time.time()

        while True:

            self.handleInputs()

            self.updateMenuState()

            self.updateMenuState()

            self.drawScreenElements()

            self.screen.blit(self.collection_shapes.sprites()[0].stats_surface, self.collection_shapes.sprites()[0].rect)

            self.clock.tick(self.target_fps)


