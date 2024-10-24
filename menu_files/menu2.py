from pygame.locals import *
import pygame.mouse
from pygame.sprite import Group
from pygame.mixer import Sound
from pygame.transform import smoothscale
from pygame.surface import Surface
from pygame.image import load
import pygame, time, itertools, sys, pytz, random

from createdb import User, Shape as ShapeData
from screen_elements.text import Text
from screen_elements.editabletext import EditableText
from screen_elements.clickabletext import ClickableText
from screen_elements.arrow import Arrow
from screen_elements.button import Button
from game_files.gamedata import color_data, shape_data as shape_model_data, names, titles
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker as session_maker, Session

def generateRandomShape(user: User, session: Session):
    '''returns randomly generated ShapeData'''

    type = random.choices(['circle', 'triangle', 'square'], weights=[40, 40, 20], k=1)[0]
    face_id = 0
    color_id = random.randint(0, len(color_data)-1)
    density = 1
    velocity = shape_model_data[type].velocity + random.randint(-3, 3)
    radius_min = shape_model_data[type].radius_min + random.randint(-10, 10)
    radius_max = shape_model_data[type].radius_max + random.randint(-10, 10)
    health = shape_model_data[type].health + random.randint(-50, 50)
    dmg_x = round(shape_model_data[type].dmg_multiplier + (random.random() * random.choice([-1, 1])), 1)
    luck = shape_model_data[type].luck + random.randint(-5, 5)
    team_size = shape_model_data[type].team_size + random.randint(-3, 3)
    name = random.choice(names)
    title = titles[0]

    shape_data = ShapeData(user.id, user, type, face_id, color_id, density, velocity, radius_min, radius_max, health, dmg_x, luck, team_size, user.username, name, title)

    user.shape_tokens -= 1

    session.add(shape_data)
    session.commit()

    return shape_data

class CollectionWindow:
    def __init__(self, user: User, session: Session):
        self.user = user
        self.session = session

        self.initCollectionWindow()
        self.initCollectionGroup()

    def initCollectionWindow(self):
        '''create the bottom collection window'''
        self.surface = Surface([1920, 443], pygame.SRCALPHA, 32)
        self.rect = self.surface.get_rect()
        self.rect.topleft = [0, 1030]

        self.shapes_button = Button('shapes', 50, [25, 25])
        self.question_button = Button('question', 40, [590, 131])
        self.add_button = Button('add', 90, [87, 145])
        self.left = Arrow(690, 400, '<-', length=100, width=66)
        self.right = Arrow(810, 400, '->', length=100, width=66)

        self.buttons = [self.shapes_button, self.question_button, self.add_button, self.left, self.right]

        self.background = load('backgrounds/collection_window.png').convert_alpha()
        self.background_rect = self.background.get_rect()
        self.background_rect.topleft = [0, 1080]
        
        self.paper = load('backgrounds/additional_shape_data.png').convert_alpha()
        self.paper_rect = self.paper.get_rect()
        self.paper_rect.center = [1130, 250]

        self.tape_surface = load('backgrounds/tape_0_xl.png')
        self.tape_rect = self.tape_surface.get_rect()
        self.tape_rect.center = [1140, 750]

        self.shape_token_dot = load('backgrounds/shape_token_dot.png').convert_alpha()
        self.shape_token_dot_rect = self.shape_token_dot.get_rect()
        self.shape_token_dot_rect.center = [120, 116]

        self.shape_token_text = Text(f'{self.user.shape_tokens}', 40, 122, 118)

        self.y = 1080
        self.next_y = 1080
        self.v = 0
        self.a = 1.5
        self.opened = False
        self.info_alpha = 0

        self.selected_index = 0
        self.selected_shape: ShapeData | None = None
        self.collection_shapes = Group()

    def initCollectionGroup(self):
        '''create Collection shapes for newly logged in user'''

        for count, shape_data in enumerate(self.user.shapes):
            new_shape = CollectionShape(shape_data, count, self.session)
            self.collection_shapes.add(new_shape)
            
            # set selected shape if user logs in with shapes
            if count == 0: self.selected_shape = new_shape

    def positionWindow(self):
        # update window positions
        if self.y != self.next_y:
        
            # calculate the remaining distance to the target
            distance = abs(self.y - self.next_y)

            # apply acceleration while far from the target, decelerate when close
            if distance > 50:
                self.v += self.a
            else:
                self.v = max(1, distance * 0.2)

            # move the window towards the target position, snap in place if position is exceeded
            if self.y > self.next_y:
                self.y -= self.v

                if self.y < self.next_y:
                    self.y = self.next_y

            elif self.y < self.next_y:
                self.y += self.v
                
                if self.y > self.next_y:
                    self.y = self.next_y 

            # reset the velocity when the window reaches its target
            if self.y == self.next_y:
                self.v = 0

            self.rect.topleft = [0, self.y - 50]

    def userGenerateShape(self):
        '''handle the user adding a shape to their collection'''
        if self.user.shape_tokens == 0: return

        # move all shapes to original position
        while self.selected_index != 0:
            self.selected_index -= 1

            for shape in self.collection_shapes:
                shape.moveRight()

        # create shape in database
        shape_data = generateRandomShape(self.user, self.session)

        # add new collection shape to the front of the list
        new_shape = CollectionShape(shape_data, -1, self.session, True)
        collection_shapes_copy = self.collection_shapes.sprites()
        self.collection_shapes.empty()
        self.collection_shapes.add(itertools.chain([new_shape, collection_shapes_copy]))

        # adjust selected shape and shape positions to introduce new shape from the right
        self.selected_shape = new_shape
        for shape in self.collection_shapes:
            shape.moveRight()

        # recreate shape tokens text
        self.shape_token_text = Text(f'{self.user.shape_tokens}', 40, 122, 118)

    def handleInputs(self, mouse_pos, events):
        mouse_pos = [mouse_pos[0], mouse_pos[1] - self.y + 50]

        # update icons

        for button in self.buttons:
            button.update(mouse_pos)

        # check if the user is hovering over the question mark on collection window
        if self.question_button.rect.collidepoint(mouse_pos) and self.info_alpha < 254: 
            self.info_alpha += 15
            self.info_alpha = min(self.info_alpha, 255)

        elif self.question_button.rect.collidepoint(mouse_pos) and self.info_alpha == 255: pass

        elif self.info_alpha > 0: 
            self.info_alpha -= 15
            self.info_alpha = max(self.info_alpha, 0)

        # handle events
        for event in events:
            if event.type != MOUSEBUTTONDOWN: return

            if self.shapes_button.rect.collidepoint(mouse_pos):
                self.toggle()

            elif self.right.rect.collidepoint(mouse_pos) and self.selected_index != 0:
                self.selected_index -= 1
                self.selected_shape = self.collection_shapes.sprites()[self.selected_index]

                for shape in self.collection_shapes:
                    shape.moveRight()

            elif self.left.rect.collidepoint(mouse_pos) and self.selected_index != len(self.user.shapes)-1:
                self.selected_index += 1
                self.selected_shape = self.collection_shapes.sprites()[self.selected_index]

                for shape in self.collection_shapes:
                    shape.moveLeft()

            elif self.add_button.rect.collidepoint(mouse_pos):
                self.userGenerateShape()

    def update(self, mouse_pos, events):
        '''update position of the collection window'''

        self.handleInputs(mouse_pos, events)

        self.collection_shapes.update()
        
        self.positionWindow()

        self.renderSurface()

    def toggle(self):
        self.opened = not self.opened

        if self.opened: self.next_y = 1080 - self.background.get_size()[1] + 25
        else: self.next_y = 1080

    def renderSurface(self):
        self.surface.blit(self.background, [0, 50])

        # draw buttons
        for button in self.buttons:
            self.surface.blit(button.surface, button.rect)

        self.surface.blit(self.shape_token_dot, self.shape_token_dot_rect)

        # arrows
        self.surface.blit(self.left.surface, self.left.rect)
        self.surface.blit(self.right.surface, self.right.rect)

        # sprites
        self.collection_shapes.draw(self.surface)

        # draw additional info (self.info_alpha increased on hover)
        if self.info_alpha >= 0: 
            if self.paper.get_alpha() != self.info_alpha:
                self.paper.set_alpha(self.info_alpha)
                self.tape_surface.set_alpha(self.info_alpha)
                
                if self.selected_shape != None: self.selected_shape.info_surface.set_alpha(self.info_alpha)

            self.surface.blit(self.paper, self.paper_rect)
            self.surface.blit(self.tape_surface, self.tape_rect)
        
        # if we have a selected shape, show its information
        if self.selected_shape != None: 
            self.surface.blit(self.selected_shape.info_surface, self.selected_shape.info_rect)
            self.surface.blit(self.selected_shape.stats_surface, self.selected_shape.stats_rect)

        # shape tokens
        self.surface.blit(self.shape_token_text.surface, self.shape_token_text.rect)

class CollectionShape(pygame.sprite.Sprite):
    def __init__(self, shape_data: ShapeData, position: int, session, new = False):
        super().__init__()

        self.shape_data = shape_data
        self.position = position
        self.session = session
        self.new = new
        
        self.x = 750 + position * 220
        self.y = 250
        self.next_x = self.x
        self.v = 0
        self.a = 1.5
        self.alpha = 0 if new else 255

        self.generateSurfaces()

    def generateSurfaces(self):
        '''generate the surfaces for window stats, additional info, and shape image'''

        # shape image
        self.face_image = smoothscale(load(f'shape_images/faces/{self.shape_data.type}/{self.shape_data.face_id}/0.png').convert_alpha(), [190, 190])
        self.image = smoothscale(load(f'shape_images/backgrounds/{self.shape_data.type}/{color_data[self.shape_data.color_id].name}.png').convert_alpha(), [190, 190])

        self.image.blit(self.face_image, [0, 0])

        self.rect = self.image.get_rect()
        self.rect.center = [self.x, self.y]

        # stats surface
        self.stats_surface = Surface([580, 340], pygame.SRCALPHA, 32)
        self.stats_rect = self.stats_surface.get_rect()
        self.stats_rect.center = [450, 267]

        # determine all differences in shape value -> baseline shape value
        d_v = round(self.shape_data.velocity - shape_model_data[self.shape_data.type].velocity, 1)
        d_r = round(self.shape_data.radius_min - shape_model_data[self.shape_data.type].radius_min, 1)
        d_hp = round(self.shape_data.health - shape_model_data[self.shape_data.type].health, 1)
        d_dmg = round(self.shape_data.dmg_multiplier - shape_model_data[self.shape_data.type].dmg_multiplier, 1)
        d_luck = round(self.shape_data.luck - shape_model_data[self.shape_data.type].luck, 1)
        d_ts = round(self.shape_data.team_size - shape_model_data[self.shape_data.type].team_size, 1)
        
        texts = [
            # name
            Text(f'{self.shape_data.title} {self.shape_data.name}', 60, 245, 45, color=color_data[self.shape_data.color_id].text_color),

            # labels
            Text('level:', 40, 193, 90, 'topright'),
            Text('wins:', 40, 350, 90, 'topright'),
            Text('velocity:', 32, 193, 128, 'topright'),
            Text('radius:', 32, 193, 157, 'topright'),
            Text('health:', 32, 193, 188, 'topright'),
            Text('damage x:', 32, 193, 219, 'topright'),
            Text('luck:', 32, 193, 249, 'topright'),
            Text('team size:', 32, 193, 279, 'topright'),

            # values
            Text(f'{self.shape_data.level}', 38, 213, 90, 'topleft'),
            Text(f'{self.shape_data.num_wins}', 38, 380, 90, 'topleft'),
            Text(f'{self.shape_data.velocity}', 30, 213, 128, 'topleft'),
            Text(f'{self.shape_data.radius_min} - {self.shape_data.radius_max}', 30, 213, 157, 'topleft'),
            Text(f'{self.shape_data.health}', 30, 213, 188, 'topleft'),
            Text(f'{self.shape_data.dmg_multiplier}', 30, 213, 219, 'topleft'),
            Text(f'{self.shape_data.luck}', 30, 213, 249, 'topleft'),
            Text(f'{self.shape_data.team_size}', 30, 213, 279, 'topleft'),

            # addition/subtraction
            Text(str(d_v) if d_v < 0 else f'+{d_v}', 30, 400, 128, 'topright', 'red' if d_v < 0 else 'green'),
            Text(str(d_r) if d_r < 0 else f'+{d_r}', 30, 400, 157, 'topright', 'red' if d_r < 0 else 'green'),
            Text(str(d_hp) if d_v < 0 else f'+{d_hp}', 30, 400, 188, 'topright', 'red' if d_hp < 0 else 'green'),
            Text(str(d_dmg) if d_v < 0 else f'+{d_dmg}', 30, 400, 219, 'topright', 'red' if d_dmg < 0 else 'green'),
            Text(str(d_luck) if d_v < 0 else f'+{d_luck}', 30, 400, 249, 'topright', 'red' if d_luck < 0 else 'green'),
            Text(str(d_ts) if d_ts < 0 else f'+{d_ts}', 30, 400, 279, 'topright', 'red' if d_ts < 0 else 'green'),
        ]

        for text in texts:
            self.stats_surface.blit(text.surface, text.rect)

        # additional info
        self.info_surface = Surface([510, 300], pygame.SRCALPHA, 32)
        self.info_rect = self.info_surface.get_rect()
        self.info_rect.center = [1130, 250]

        utc_timezone = pytz.timezone('UTC')
        est_timezone = pytz.timezone('US/Eastern')

        obtained_on_datetime = utc_timezone.localize(self.shape_data.obtained_on).astimezone(est_timezone)
        created_on_datetime = utc_timezone.localize(self.shape_data.created_on).astimezone(est_timezone)
        count = self.session.query(func.count(ShapeData.id)).filter(ShapeData.type == self.shape_data.type, ShapeData.color_id == self.shape_data.color_id).scalar()

        texts = [
            Text(['obtained on:', f'{obtained_on_datetime.strftime("%m/%d/%Y, %H:%M")}'], 35, 250, 40),
            Text(['created on:', f'{created_on_datetime.strftime("%m/%d/%Y, %H:%M")}'], 35, 250, 110),
            Text(f'number of owners: {self.shape_data.num_owners}', 32, 250, 180),
            Text(f'created by: {self.shape_data.created_by}', 32, 250, 215),
            Text(f'your shape is 1 of {count}', 32, 250, 250),
        ]

        for text in texts:
            self.info_surface.blit(text.surface, text.rect)

        self.info_surface.set_alpha(0)
        
    def moveLeft(self):
        self.next_x -= 220

    def moveRight(self):
        self.next_x += 220

    def update(self):
        # adjust transparency
        if self.next_x < 750 and self.alpha > 0:
            self.alpha = max(self.alpha - 10, 0)

        elif self.next_x > 530 and self.alpha < 255:
            self.alpha = min(self.alpha + 10, 255)

        if self.image.get_alpha() != self.alpha: self.image.set_alpha(self.alpha)

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

        self.collection_window: CollectionWindow | None = None

        self.initSounds()
        self.initTexts()

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
        self.your_shapes_text = Text('your shapes', 40, 55, 1035, 'topleft')

        self.texts: list[Text] = []
        self.texts.append(self.title_text)
        self.texts.append(self.play_text)
        self.texts.append(self.bad_credentials_text)
        self.texts.append(self.your_shapes_text)

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

    # PLAY HELPERS

    def loginLoop(self):
        '''run the game loop for the login/register screen'''

    def handleInputs(self, mouse_pos, events):
        '''handle any inputs from the user'''

        for event in events:
            if event.type != MOUSEBUTTONDOWN: return

            self.click_sound.play()

            if self.exit_clickable.rect.collidepoint(mouse_pos):
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
        self.screen.blit(self.cursor, self.cursor_rect)

    def play(self):
        '''run the game loop for the main menu'''

        # the login loop would replace this
        self.user = self.session.query(User).filter(User.username == 'pat').one()
        self.collection_window = CollectionWindow(self.user, self.session)
        self.logged_in_as_text = Text(f'logged in as: {self.user.username}', 35, 1920/2, 20)
        self.texts.append(self.logged_in_as_text)

        # start the time for accumulator
        self.prev_time = time.time()

        while True:
            self.updateMenuState()

            self.drawScreenElements()

            self.clock.tick(self.target_fps)
