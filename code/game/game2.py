import pygame, random, os, numpy, math, time, itertools, colorsys
from queue import Queue
from pygame import Surface
from pygame.locals import *
from pygame.sprite import Group
import pygame.sprite

from ..screen_elements.clickabletext import ClickableText
from ..screen_elements.doublecheckbox import DoubleCheckbox
from ..screen_elements.text import Text
from ..screen_elements.button import Button
from sharedfunctions import clearSurfaceBeneath

from createdb import User, Shape as ShapeData

from .shape import Shape
from .laser2 import Laser
from .buckshot import Buckshot
from .powerup2 import Powerup
from .killfeed2 import Killfeed
from .clouds2 import Clouds
from .circledata import *
from .gamedata import color_data

ACTION_KILL = 'kill'
ACTION_HEAL = 'heal'
ACTION_RESURRECT = 'resurrect'
ACTION_PICKUP_BOMB = 'pickup_bomb'
ACTION_PICKUP_SKULL = 'pickup_instakill'
ACTION_PICKUP_WINGS = 'pickup_resurrect'
ACTION_PICKUP_STAR = 'pickup_lucky_star'
ACTION_PICKUP_BOXING_GLOVE = 'pickup_boxing_glove'
ACTION_PICKUP_FEATHER = 'pickup_feather'
ACTION_PICKUP_CHERRY = 'pickup_cherry'
ACTION_PICKUP_LASER = 'pickup_laser'
ACTION_PICKUP_BUCKSHOT = 'pickup_buckshot'
ACTION_PICKUP_MUSHROOM = 'pickup_mushroom'
KILL_SKULL = 'kill_skull'
KILL_STAR = 'kill_star'
KILL_BOXING_GLOVE = 'kill_boxing_glove'
KILL_LASER = 'kill_laser'
KILL_BUCKSHOT = 'kill_buckshot'

class Game2:
    def __init__(self, screen: Surface, shape_1_data: ShapeData, shape_2_data: ShapeData, user_1: User, user_2: User, seed = False, player_simulated = False, server_simulated = False):
        # seed randomness
        if seed != False: 
            random.seed(seed)

        print(
            'playing game:',
            f'seed: {seed}\n',
            f'player 1: {user_1.id}',
            f'player 2: {user_2.id}\n',
            f'shape 1: {shape_1_data.id},'
            f'shape 2: {shape_2_data.id}\n'
        )
        
        self.screen = screen
        self.shape_1_data = shape_1_data
        self.shape_2_data = shape_2_data
        self.user_1 = user_1
        self.user_2 = user_2
        self.seed = seed
        self.player_simulated = player_simulated
        self.server_simulated = server_simulated
        self.simulated = player_simulated or server_simulated
        self.powerup_data = powerup_data
        
        self.initSimulationNecessities()
        self.initTeams()

        if self.simulated: return
        
        self.initPlayNecessities()
        self.loadImages()
        self.loadSounds()
        self.populateTeams()
        self.initStatsScreen()
        self.initTeamOverview()

        self.initBoundaryCircle()

    # INIT HELPERS

    def initSimulationNecessities(self):
        '''initiate all variables which are necessary for game simulation'''

        # flags
        self.running = True
        self.done = False
        self.p1_win = False
        self.p2_win = False
        self.player_win_text = None
        self.num_active_bombs = 0

        # screen bounds for shape movement
        self.screen_w = 1920 - 460
        self.screen_h = 1080
        
        # game timing variables
        self.target_fps = 60
        self.frames_played = 0
        self.time_step = 1 / self.target_fps
        self.time_step_accumulator = 0.0
        self.prev_time = None
        self.current_time = None
        
        # testing variables
        self.sum_fps = 0
        self.fps_low = 9999
        self.fps_high = 0

        # predefine containers for images
        self.shape_1_face_images = []
        self.shape_2_face_images = []
        self.smoke_images = []
        self.powerup_images_small = []
        self.powerup_images_medium = []

    def initTeams(self):
        '''initiate all variables on sprites and their groups'''

        # variables for all data on shapes and teams
        self.team_1_team_size = self.shape_1_data.team_size
        self.team_2_team_size = self.shape_2_data.team_size
        self.team_1_shape_count = self.shape_1_data.team_size
        self.team_2_shape_count = self.shape_2_data.team_size
        self.total_shape_count = self.team_1_shape_count + self.team_2_shape_count
        self.team_1_max_hp = self.shape_1_data.health * self.shape_1_data.team_size
        self.team_2_max_hp = self.shape_2_data.health * self.shape_2_data.team_size
        self.team_1_total_hp = self.shape_1_data.health * self.shape_1_data.team_size
        self.team_2_total_hp = self.shape_2_data.health * self.shape_2_data.team_size

        self.team_1_group = Group()
        self.team_2_group = Group()
        self.powerup_group = Group()
        self.laser_group = Group()
        self.buckshot_group = Group()
        self.clouds_group = Group()
        self.explosions_group = Group()

        # killfeed necessities
        self.killfeed_group = Group()
        self.num_killfeeds = 0

    def populateTeams(self):
        '''populate teams'''

        for i in range(0, self.shape_1_data.team_size):
            shape = Shape(i, 0, self.shape_1_data, color_data[self.shape_1_data.color_id], self.shape_1_face_images, self.powerup_images_small)
            
            self.team_1_group.add(shape)

        for i in range(0, self.shape_2_data.team_size):
            shape = Shape(i, 1, self.shape_2_data, color_data[self.shape_2_data.color_id], self.shape_2_face_images, self.powerup_images_small)

            self.team_2_group.add(shape)

    def initPlayNecessities(self):
        '''initiate all misc variables not required for game simulation'''

        # load background and update display
        self.background = pygame.image.load('assets/backgrounds/grid_paper_w_sides_2.png').convert_alpha()
        self.background_clear = pygame.image.load('assets/backgrounds/BG1.png').convert_alpha()
        self.background_clear.set_alpha(0)
        pygame.display.update()

        # necessary variables for playing game
        self.clock = pygame.time.Clock()

        # create screen elements
        self.exit_clickable = Button("exit", 45, [1920 - 25, 1080 - 25])
        self.clickables = [self.exit_clickable]

        # load and center cursor
        self.cursor = pygame.transform.smoothscale(pygame.image.load('assets/misc/cursor.png').convert_alpha(), (12, 12))
        self.cursor_rect = self.cursor.get_rect()
        self.cursor_rect.center = pygame.mouse.get_pos()

    def initStatsScreen(self):
        '''initiate all variables required for the stats screen'''

        self.stats_window_shown = False
        self.stats_window_held = False

        self.shape_rerender_queue = Queue()
        self.shape_rerender_list = []

        self.stats_window_current_x = 1920
        self.stats_window_next_x = 1920
        self.stats_window_velocity = 0
        self.stats_window_acceleration = 1.5
        self.stats_window_y_when_clicked = 0
        self.mouse_y_when_clicked = 0
        self.stats_window_y = 0
        self.stats_window_min_y = (int((161 * 2) + (self.team_1_team_size * 20.6) + (self.team_1_team_size * 20.6)) - 1920) / 2 + 15
        
        self.stats_window: Surface = pygame.image.load('assets/backgrounds/side_window_long.png').convert_alpha()
        self.team_1_stats: Surface = pygame.Surface((self.stats_window.get_size()[0], self.stats_window.get_size()[1]), pygame.SRCALPHA, 32)
        self.team_2_stats: Surface = pygame.Surface((self.stats_window.get_size()[0], self.stats_window.get_size()[1]), pygame.SRCALPHA, 32)
        
        self.team_2_stats_rect = self.team_2_stats.get_rect() # no need for team_1_stats_rect as the stats_window_rect will be identical
        self.stats_window_rect = self.stats_window.get_rect()
        self.stats_window_rect.topleft = [1920, 0]
        self.team_2_stats_rect.topleft = [1920, 164 + int(20.6 * (self.team_1_team_size))]

        self.drawStatsWindowHeaders()

        for shape in itertools.chain(self.team_1_group, self.team_2_group):
            self.renderShapeStats(shape)

    def initTeamOverview(self):
        '''initiate all variables required for the team overview'''

        self.team_overview_surface = pygame.Surface((334, 334), pygame.SRCALPHA, 32)
        self.team_overview_rect = self.team_overview_surface.get_rect()
        self.team_overview_rect.topleft = [1920-310, 125]
        self.team_overview_sections_to_render = ['all']
        
        self.team_1_overview_face_id = 0
        self.team_2_overview_face_id = 0
        self.team_1_overview_images = self.team_1_group.sprites()[0].shape_images
        self.team_2_overview_images = self.team_2_group.sprites()[0].shape_images
        self.team_1_overview_image = self.team_1_overview_images[self.team_1_overview_face_id]
        self.team_2_overview_image = self.team_2_overview_images[self.team_2_overview_face_id]

        self.team_1_hp_p = self.determineTeamOverviewHealthPercent(0)
        self.team_2_hp_p = self.determineTeamOverviewHealthPercent(1)
        self.team_1_hp_text = None
        self.team_2_hp_text = None
        self.team_1_count_text = None
        self.team_2_count_text = None

    def loadImages(self):
        '''load all images into their containers'''
        self.title_text = Text("shapegame", 150, 1920/2, 2*1080/3, outline_color='white')

        def getFaceImages(shape_data: ShapeData):
            '''load and return an array of shape faces for the given shape'''
            images = []
            for i in range(4):
                images.append(pygame.image.load(f'assets/shapes/faces/{shape_data.type}/{shape_data.face_id}/{i}.png').convert_alpha())

            return images

        # load powerup images
        for powerup in self.powerup_data:
            image = pygame.image.load(self.powerup_data[powerup][0]).convert_alpha()
            self.powerup_images_small.append(pygame.transform.smoothscale(image, (20, 20)))
            self.powerup_images_medium.append(pygame.transform.smoothscale(image, (40, 40)))

        # load face images for each shape
        self.shape_1_face_images = getFaceImages(self.shape_1_data)
        self.shape_2_face_images = getFaceImages(self.shape_2_data)

        # load killfeed images

        self.killfeed_backgrounds = []
        self.killfeed_backgrounds.append(pygame.image.load('assets/paper/killfeed_small.png').convert_alpha())
        self.killfeed_backgrounds.append(pygame.image.load('assets/paper/killfeed_large.png').convert_alpha())

        self.killfeed_tapes = []
        self.killfeed_tapes.append(pygame.image.load('assets/paper/tape_0_small.png').convert_alpha())
        self.killfeed_tapes.append(pygame.image.load('assets/paper/tape_0_large.png').convert_alpha())
        self.killfeed_tapes.append(pygame.image.load('assets/paper/tape_1.png').convert_alpha())
        self.killfeed_tapes.append(pygame.image.load('assets/paper/tape_2.png').convert_alpha())

        self.killfeed_action_imgs = {
            'tombstone': pygame.transform.smoothscale(pygame.image.load('assets/powerups/tombstone.png').convert_alpha(), [50, 50]),
            'bomb': pygame.transform.smoothscale(pygame.image.load('assets/powerups/bomb.png').convert_alpha(), [50, 50]),
            'skull': pygame.transform.smoothscale(pygame.image.load('assets/powerups/skull.png').convert_alpha(), [50, 50]),
            'resurrect': pygame.transform.smoothscale(pygame.image.load('assets/powerups/wings.png').convert_alpha(), [50, 50]),
            'star': pygame.transform.smoothscale(pygame.image.load('assets/powerups/star.png').convert_alpha(), [50, 50]),
            'boxing_glove': pygame.transform.smoothscale(pygame.image.load('assets/powerups/boxing_glove.png').convert_alpha(), [50, 50]),
            'feather': pygame.transform.smoothscale(pygame.image.load('assets/powerups/feather.png').convert_alpha(), [50, 50]),
            'cherry': pygame.transform.smoothscale(pygame.image.load('assets/powerups/cherry.png').convert_alpha(), [50, 50]),
            'laser': pygame.transform.smoothscale(pygame.image.load('assets/powerups/green_laser.png').convert_alpha(), [50, 50]),
            'buckshot': pygame.transform.smoothscale(pygame.image.load('assets/powerups/purple_laser.png').convert_alpha(), [50, 50]),
            'mushroom': pygame.transform.smoothscale(pygame.image.load('assets/powerups/mushroom.png').convert_alpha(), [50, 50]),
            'bomb': pygame.transform.smoothscale(pygame.image.load('assets/powerups/bomb.png').convert_alpha(), [50, 50]),
        }

        self.laser_images = []
        for i in range(8):
            self.laser_images.append(pygame.transform.smoothscale(pygame.image.load(f'assets/powerups/laser/{i}.png').convert_alpha(), [40, 40]))

        self.buckshot_images = []
        for i in range(10):
            self.buckshot_images.append(pygame.transform.smoothscale(pygame.image.load(f'assets/powerups/buckshot/{i}.png').convert_alpha(), [40, 40]))

        self.cloud_images = []
        for i in range(5):
            self.cloud_images.append(pygame.transform.smoothscale(pygame.image.load(f'assets/powerups/screen_effects/clouds/{i}.png').convert_alpha(), [100, 100]))

        self.explosion_images = []
        for i in range(7):
            self.explosion_images.append(pygame.transform.smoothscale(pygame.image.load(f'assets/powerups/screen_effects/explosions/{i}.png').convert_alpha(), [100, 100]))

    def loadSounds(self):
        '''load all sounds'''

        # Sounds
        self.death_sounds = []
        self.death_sounds.append(pygame.mixer.Sound("assets/sounds/death/1.wav"))
        self.death_sounds.append(pygame.mixer.Sound("assets/sounds/death/2.wav"))
        self.death_sounds.append(pygame.mixer.Sound("assets/sounds/death/3.wav"))
        self.death_sounds.append(pygame.mixer.Sound("assets/sounds/death/4.wav"))

        self.collision_sounds = []
        self.collision_sounds.append(pygame.mixer.Sound("assets/sounds/collisions/clink1.wav"))
        self.collision_sounds.append(pygame.mixer.Sound("assets/sounds/collisions/clink2.wav"))
        self.collision_sounds.append(pygame.mixer.Sound("assets/sounds/collisions/thud2.wav"))

        self.game_sounds = []
        self.game_sounds.append(pygame.mixer.Sound("assets/sounds/game/1.wav"))

        self.choir_sound = pygame.mixer.Sound("assets/sounds/choir.wav")
        self.explosion_sound = pygame.mixer.Sound("assets/sounds/explosion.flac")
        self.fuse_sound = pygame.mixer.Sound("assets/sounds/fuse.wav")
        self.heal_sound = pygame.mixer.Sound("assets/sounds/heal.wav")
        self.laser_hit_sound = pygame.mixer.Sound("assets/sounds/laser_hit.wav")
        self.laser_sound = pygame.mixer.Sound("assets/sounds/laser.wav")
        self.pop_sound = pygame.mixer.Sound("assets/sounds/pop.wav")
        self.punch_sound = pygame.mixer.Sound("assets/sounds/punch.wav")
        self.shotgun_sound = pygame.mixer.Sound("assets/sounds/shotgun.wav")
        self.twinkle_sound = pygame.mixer.Sound("assets/sounds/twinkle.wav")
        self.win_sound = pygame.mixer.Sound("assets/sounds/win.wav")
        self.wind_sound = pygame.mixer.Sound("assets/sounds/wind.wav")
        self.click_sound = pygame.mixer.Sound("assets/sounds/click.wav")
        self.close_sound = pygame.mixer.Sound("assets/sounds/close.wav")

        self.sounds = [
            self.choir_sound,
            self.explosion_sound,
            self.fuse_sound,
            self.heal_sound,
            self.laser_hit_sound,
            self.laser_sound,
            self.pop_sound,
            self.punch_sound,
            self.shotgun_sound,
            self.twinkle_sound,
            self.win_sound,
            self.wind_sound,
            self.click_sound,
            self.close_sound,
        ]

        [self.sounds.append(sound) for sound in itertools.chain(self.death_sounds, self.collision_sounds, self.game_sounds)]

        self.choir_sound.set_volume(.25)
        self.explosion_sound.set_volume(.1)
        self.fuse_sound.set_volume(.05)
        self.heal_sound.set_volume(.25)
        self.laser_sound.set_volume(.1)
        self.punch_sound.set_volume(.25)
        self.shotgun_sound.set_volume(.05)
        self.twinkle_sound.set_volume(.25)
        self.wind_sound.set_volume(.25)
        self.win_sound.set_volume(.25)

        for sound in self.collision_sounds:
            sound.set_volume(.05)

        for sound in self.death_sounds:
            sound.set_volume(.5)

    def initBoundaryCircle(self):


        # all required numerical data
        self.f_r_max = 910
        self.f_r_min = 350
        self.f_r = self.f_r_max
        self.f_r_next = self.f_r
        self.f_color = (0, 0, 0, 100)
        self.f_hue = 0

        # draw the full sized boundary_circle
        boundary_circle_surface = Surface([self.f_r*2, self.f_r*2], pygame.SRCALPHA, 32)
        boundary_circle_rect = boundary_circle_surface.get_rect()
        pygame.draw.ellipse(boundary_circle_surface, self.f_color, boundary_circle_rect, width=5)
        boundary_circle_rect.center = [730, 540]

        # crop the full sized boundary_circle to the max size
        self.boundary_circle_surface = Surface([self.screen_w, self.screen_h], pygame.SRCALPHA, 32)
        self.boundary_circle_surface.blit(boundary_circle_surface, boundary_circle_rect)
        self.boundary_circle_rect = self.boundary_circle_surface.get_rect()
        self.boundary_circle_rect.center = [730, 540]
    
    def transitionIn(self):

        self.team_overview_surface.set_alpha(0)
        self.background.set_alpha(0)
        self.title_text.turnOff()

        for sprite in itertools.chain(self.team_1_group, self.team_2_group): sprite.stuck = True

        # fade from clear background to background with office supplies
        while self.frames_played < 60:
            events = pygame.event.get()

            self.updateGameState(events)
            self.drawGameElements()
            self.drawScreenElements()
            self.clock.tick(self.target_fps)

            cur_a = self.background.get_alpha()
            if cur_a < 255:
                next_a = min(cur_a + 10, 255)
                self.background.set_alpha(next_a)

        # fade team overview and teams in
        while self.frames_played < 120:
            events = pygame.event.get()

            self.updateGameState(events)
            self.drawGameElements()
            self.drawScreenElements()
            self.clock.tick(self.target_fps)

            cur_a = self.team_overview_surface.get_alpha()
            if cur_a < 255:
                next_a = min(cur_a + 10, 255)
                self.team_overview_surface.set_alpha(next_a)

        for sprite in itertools.chain(self.team_1_group, self.team_2_group):
            sprite.stuck = False

        self.prev_time = time.time()

    def transitionOut(self):

        if self.player_win_text: self.player_win_text.turnOff()
        self.title_text.turnOn()

        pause_start = time.time()
        while time.time() - pause_start < 1:
            events = pygame.event.get()

            self.updateGameState(events)

            cur_a = self.background_clear.get_alpha()
            if cur_a < 255:
                cur_a = min(cur_a + 10, 255)
                self.background_clear.set_alpha(cur_a)

            cur_a = self.team_overview_surface.get_alpha()
            if cur_a > 0:
                cur_a = max(cur_a - 15, 0)
                self.team_overview_surface.set_alpha(cur_a)

            self.drawScreenElements()
            self.screen.blit(self.background_clear, [0, 0])
            self.screen.blit(self.cursor, self.cursor_rect)
            self.exit_clickable.draw(self.screen)
            self.clock.tick(self.target_fps)

    # GAME STATE UPDATE FUNCTIONS

    def updateGameState(self, events):
        self.current_time = time.time()
        
        self.time_step_accumulator += self.current_time - self.prev_time
        while self.time_step_accumulator >= self.time_step:
            self.time_step_accumulator -= self.time_step
            
            self.frames_played += 1
            self.updateGameElements(events)

        self.prev_time = self.current_time

        self.testFps()

    def updateGameElements(self, events):
        '''update all game elements (shapes, powerups, killfeed), separate from drawGameElements for easier simulation'''
        mouse_pos = pygame.mouse.get_pos()

        self.title_text.update(events, mouse_pos)
        if self.player_win_text: self.player_win_text.update(events, mouse_pos)

        # spawn powerups
        self.spawnRandomPowerups()

        # update groups
        self.powerup_group.update()
        self.laser_group.update(self.f_r)
        self.clouds_group.update()
        self.team_1_group.update(self.f_r)
        self.team_2_group.update(self.f_r)

        # update killfeed elements
        num_cycles = 0
        for killfeed in self.killfeed_group.sprites():
            ret = killfeed.update()
            num_cycles += ret if ret == 1 else 0

            if ret == 1:
                self.num_killfeeds -= 1

            for i in range(num_cycles):
                killfeed.cycle()

        # update clickable elements
        mouse_pos = pygame.mouse.get_pos()
        [clickable.update(events, mouse_pos) for clickable in self.clickables if clickable not in [None]]

        # detect collisions
        self.detectCollisions()


        self.checkBoundaryCircle()

    def checkBoundaryCircle(self):
        '''redraws the bounding boundary_circle if need be'''
        # if self.frames_played % 5 == 0 and self.f_r > 500: self.f_r -= 1
        # return

        # if self.f_r == self.f_r_next: return

        if self.f_r < self.f_r_next and self.frames_played % 5 == 0: 
            self.f_r += 1
        elif self.f_r > self.f_r_next and self.frames_played % 5 == 0: 
            self.f_r -= 1
        elif self.frames_played % 5 != 0: return # don't update if the boundary circle is not changing
        
        # update the color of the boundary circle
        # increment hue 
        self.f_hue += 0.01
        if self.f_hue > 1: self.f_hue -= 1

        # convert HSV color to RGB
        r, g, b = colorsys.hsv_to_rgb(self.f_hue, 1, 1) # S=V=1 for bright colors
        r, g, b = int(r * 255), int(g * 255), int(b * 255)
        self.f_color = (r, g, b, 150)

        # redraw boundary_circle
        boundary_circle_surface = Surface([self.f_r*2, self.f_r*2], pygame.SRCALPHA, 32)
        boundary_circle_rect = boundary_circle_surface.get_rect()
        pygame.draw.ellipse(boundary_circle_surface, self.f_color, boundary_circle_rect, width=5)
        boundary_circle_rect.center = [730, 540]

        # crop the full sized boundary_circle to the max size
        self.boundary_circle_surface = Surface([self.screen_w, self.screen_h], pygame.SRCALPHA, 32)
        self.boundary_circle_surface.blit(boundary_circle_surface, boundary_circle_rect)
        self.boundary_circle_rect = self.boundary_circle_surface.get_rect()
        self.boundary_circle_rect.center = [730, 540]

    def updateBoundaryCircle(self):
        '''updates the next a and b values of the boundary_circle. called when number of shapes changes'''


        # get the number of shapes alive as a percent
        max_shapes = self.shape_1_data.team_size + self.shape_2_data.team_size
        num_alive = sum(1 for shape in itertools.chain(self.team_1_group.sprites(), self.team_2_group.sprites()) if not shape.is_dead)
        percent_alive = num_alive / max_shapes

        # clamp percent to range (0-1)
        clamped_percent = max(0, min(percent_alive, 1))

        self.f_r_next = int(self.f_r_min + clamped_percent * (self.f_r_max - self.f_r_min))

    def spawnRandomPowerups(self):
        '''spawn a random powerup every few seconds'''

        seconds_per_powerup = 3

        if not self.done and self.frames_played % (seconds_per_powerup * self.target_fps) == 0 and self.frames_played > 300:
            powerup_name = self.getRandom(list(self.powerup_data.keys()))
            powerup_image = self.powerup_images_medium[self.powerup_data[powerup_name][1]]

            # select an xy within the bounding circle
            # 1: select angle 0-2pi
            theta = random.uniform(0, 2 * math.pi)
            # 2: generate random radius with uniform distribution within circle
            r = self.f_r * math.sqrt(random.uniform(0, 0.9))
            # 3: convert polar coordinates to cartesian coordinates
            x = r * math.cos(theta) + 730
            y = r * math.sin(theta) + 540

            # # 4: check if xy is outside of the bounds of the arena, if so, place anywhere within
            if x >= self.screen_w-20 or x <= 20 or y >= self.screen_h-20 or y <= 20:
                x = random.randint(20, self.screen_w-20)
                y = random.randint(20, self.screen_h-20)

            self.playSound(self.pop_sound)
            self.powerup_group.add(Powerup(powerup_name, powerup_image, [x, y]))

    def checkForCompletion(self):
        '''check if one team is entirely dead. raises self.done and self.pX_win flag'''
        if self.done: return

        if all(shape.is_dead for shape in self.team_1_group): 
            self.done = True
            self.p2_win = True
        
        elif all(shape.is_dead for shape in self.team_2_group):
            self.done = True
            self.p1_win = True

        if self.done:
            self.playSound(self.win_sound)
            self.player_win_text = Text(f'{self.user_1.username if self.p1_win else self.user_2.username} wins!', 150, 730, 540, color='black')

    def handleInputs(self, events):
        ''' handle all inputs from user'''
        mouse_pos = pygame.mouse.get_pos()

        for event in events:
            if event.type == MOUSEBUTTONDOWN:
                
                if event.button == 1:
                    if self.exit_clickable.rect.collidepoint(mouse_pos):
                        self.running = False

                    if self.stats_window_rect.collidepoint(mouse_pos):
                        self.stats_window_held = True
                        self.stats_window_y_when_clicked = int(self.stats_window_y)
                        self.mouse_y_when_clicked = mouse_pos[1]

            elif event.type == MOUSEBUTTONUP:
                if self.stats_window_held: self.stats_window_held = False

            elif event.type == KEYDOWN:

                if event.key == K_TAB:
                    self.stats_window_shown = not self.stats_window_shown

                    if self.stats_window_shown: self.stats_window_next_x = 1920 - self.stats_window.get_size()[0]
                    else: self.stats_window_next_x = 1920

    def playSound(self, sound):
        if self.player_simulated or self.server_simulated or sound.get_num_channels() > 5: return

        sound.play()
        
        if sound == self.wind_sound:
            pygame.mixer.Sound.fadeout(sound, 1500)
        
        elif sound == self.choir_sound:
            pygame.mixer.Sound.fadeout(sound, 1000)
        
        if sound == self.fuse_sound:
            sound.play(9)

    def addKillfeed(self, left: Shape, action: str, right: Shape = False):
        action_img = self.killfeed_action_imgs['tombstone']
        if action.startswith('pickup_'):
            action_img = self.killfeed_action_imgs[action[7:]]
        if action.startswith('kill_'):
            action_img = self.killfeed_action_imgs[action[5:]]
        if action.startswith('heal'):
            action_img = self.killfeed_action_imgs['cherry']
        if action.startswith('resurrect'):
            action_img = self.killfeed_action_imgs['resurrect']
            
        killfeed = Killfeed(self.num_killfeeds, left, action, action_img, self.killfeed_backgrounds, self.killfeed_tapes, right)
        self.num_killfeeds += 1

        self.killfeed_group.add(killfeed)

        if self.num_killfeeds >= 5:
            self.num_killfeeds -= 1
            for killfeed in self.killfeed_group.sprites(): killfeed.cycle()

    # SHAPE COLLISION FUNCTIONS

    def detectCollisions(self):
        '''simple method for collision detection, will want to be redone in theory, but for now isn't a large impact on performance'''
        # return
        
        for shape_1 in itertools.chain(self.team_1_group, self.team_2_group):
            shape_1: Shape

            if shape_1.stats_to_render != [] and shape_1 not in self.shape_rerender_list:
                self.shape_rerender_queue.put(shape_1)
                self.shape_rerender_list.append(shape_1)

            if shape_1.bomb_timer == 0:
                self.blowupBomb(shape_1)

            if shape_1.is_dead: continue

            for shape_2 in itertools.chain(self.team_1_group, self.team_2_group):
                shape_2: Shape

                if shape_1 == shape_2 or shape_2.is_dead or shape_1.is_dead: continue

                if self.determineCollision(shape_1, shape_2):

                    if shape_2 in shape_1.shapes_touching or shape_1 in shape_2.shapes_touching: continue

                    shape_1.shapes_touching.append(shape_2)
                    shape_2.shapes_touching.append(shape_1)

                    self.collideShapes(shape_1, shape_2)
                
                # keep track of which shapes you are not touching
                else:
                    if shape_2 in shape_1.shapes_touching: shape_1.shapes_touching.remove(shape_2)
                    if shape_1 in shape_2.shapes_touching: shape_2.shapes_touching.remove(shape_1)

            for powerup in self.powerup_group:
                dist = math.sqrt((powerup.x - shape_1.x)**2 + (powerup.y - shape_1.y)**2)
                max_dist = powerup.r + shape_1.r

                if (dist <= max_dist):
                    self.shapeCollectPowerup(shape_1, powerup)

            for laser in self.laser_group:
                if shape_1.collision_mask.overlap(laser.mask, [int(laser.rect.x - shape_1.collision_mask_rect.x), int(laser.rect.y - shape_1.collision_mask_rect.y)]):

                    self.laserHitShape(laser, shape_1)

    def determineCollision(self, shape_1: Shape, shape_2: Shape):
        '''very simple preventative collision detection'''

        v1 = numpy.array(shape_1.getV())
        v2 = numpy.array(shape_2.getV())

        p1 = numpy.array(shape_1.getXY())
        p2 = numpy.array(shape_2.getXY())

        p1f = p1 + v1
        p2f = p2 + v2

        # temp move collision mask
        shape_1.collision_mask_rect.center = p1f
        shape_2.collision_mask_rect.center = p2f

        # 4: determine if collision is taking place
        collision = shape_1.collision_mask.overlap(shape_2.collision_mask, [int(shape_2.collision_mask_rect.x - shape_1.collision_mask_rect.x), int(shape_2.collision_mask_rect.y - shape_1.collision_mask_rect.y)])
        # dist = numpy.linalg.norm(p1f - p2f)
        # max_dist = shape_1.r + shape_2.r
        # collision = dist <= max_dist

        # move collision mask back
        shape_1.collision_mask_rect.center = p1
        shape_2.collision_mask_rect.center = p2

        return bool(collision)

    def collideShapes(self, shape_1: Shape, shape_2: Shape):
        '''main handler for two shapes colliding'''
        choice = self.getRandom(self.collision_sounds)
        self.playSound(choice)
        #print(f'{self.frames_played} collide sound shape1: {shape_1.x, shape_1.y, shape_1.vx, shape_1.vy} shape2: {shape_2.x, shape_2.y, shape_2.vx, shape_2.vy}: ')


        
        self.repositionShapes(shape_1, shape_2)

        if shape_1.team_id == shape_2.team_id: return

        # get roll to determine winner
        roll_1 = random.randint(0, 20) + shape_1.luck
        roll_2 = random.randint(0, 20) + shape_2.luck
         #print(f'rolls: {roll_1, roll_2}')

        if roll_1 == roll_2: return

        self.opponentsCollide(shape_1, shape_2) if roll_1 > roll_2 else self.opponentsCollide(shape_2, shape_1)

    def repositionShapes(self, shape_1: Shape, shape_2: Shape):
        '''rectify the positions and velocities of two shapes which are currently colliding'''

        # STEP 1

        [x2, y2] = shape_2.getXY()
        [x1, y1] = shape_1.getXY()

        [vx1i, vy1i] = shape_1.getV()
        [vx2i, vy2i] = shape_2.getV()

        norm_vec = numpy.array([x2 - x1, y2 - y1])
        if norm_vec[0] == 0 and norm_vec[1] == 0: 
            return

        divisor = math.sqrt(norm_vec[0]**2 + norm_vec[1]**2)
        unit_vec = numpy.array([norm_vec[0] / divisor, norm_vec[1] / divisor])

        unit_tan_vec = numpy.array([-1 * unit_vec[1], unit_vec[0]])

        # STEP 2

        v1 = numpy.array(shape_1.getV())
        m1 = shape_1.getM()

        v2 = numpy.array(shape_2.getV())
        m2 = shape_2.getM()

        # STEP 3

        v1n = numpy.dot(unit_vec, v1)

        v1t = numpy.dot(unit_tan_vec, v1)

        v2n = numpy.dot(unit_vec, v2)

        v2t = numpy.dot(unit_tan_vec, v2)

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
        shape_1.setV(v1p[0], v1p[1])

        v2p = v2np_ + v2tp_
        shape_2.setV(v2p[0], v2p[1])

    # SHAPE HIT FUNCTIONS

    def opponentsCollide(self, winner: Shape, loser: Shape):
        '''handler for if two shapes of opposing teams collide'''

        # if loser has skull, they are the winner
        if 'skull' in loser.powerup_arr:
            winner_copy = winner
            winner = loser
            loser = winner_copy

        self.shapeDamageShape(winner, loser, winner.getDamage())
        self.attemptKillfeed(winner, loser)
        self.activatePowerups(winner, loser)
        self.attemptResurrect(winner, loser)
        
        if loser.is_dead:
            self.clouds_group.add(Clouds(loser, self.cloud_images))
            self.updateBoundaryCircle()

    def laserHitShape(self, laser: Laser, shape: Shape):
        if shape.shape_id in laser.ids_collided_with or shape.team_id == laser.team_id: return

        laser.ids_collided_with.append(shape.shape_id)
        self.playSound(self.laser_hit_sound)
        
        self.shapeDamageShape(laser.shape, shape, laser.damage)

        if shape.is_dead:
            self.addKillfeed(laser.shape, f'kill_{laser.type}', shape)

    def shapeCollectPowerup(self, shape: Shape, powerup: Powerup):
        '''handler for shape collecting a powerup'''

        # shapes can have max 5 powerups
        if len(shape.powerup_arr) == 5 or powerup.name in shape.powerup_arr: return

        # handle everything that the game has to do regarding the pickup
        # (sounds, killfeed...)
        if powerup.name == 'skull': pass
        elif powerup.name == 'resurrect': pass
        elif powerup.name == 'star': self.playSound(self.twinkle_sound)
        elif powerup.name == 'boxing_glove': pass
        elif powerup.name == 'feather': pass
        elif powerup.name == 'cherry': pass
        elif powerup.name == 'bomb': self.fuse_sound.play(10); self.num_active_bombs += 1
        elif powerup.name == 'laser': pass
        elif powerup.name == 'buckshot': pass
        elif powerup.name == 'mushroom': pass

        # let shape handle pickup
        shape.collectPowerup(powerup)

        # add killfeed entry
        if powerup.name == 'bomb': self.addKillfeed(shape, f'pickup_{powerup.name}')
        
        # kill powerup
        powerup.kill()

    def healShape(self, shape: Shape, amount: int):
        
        # limit health to 100%
        if shape.hp + amount > shape.max_hp:
            amount = shape.max_hp - shape.hp
        
        shape.heal(amount)

        # determine if team overview needs to be rendered
        # lower total team hp
        if shape.team_id == 0: self.team_1_total_hp += amount
        else: self.team_2_total_hp += amount
        self.checkTeamOverviewChanges(shape.team_id)

        self.playSound(self.heal_sound)
        self.addKillfeed(shape, ACTION_HEAL)

    def shapeRespawnShape(self, creating_shape: Shape, model_shape: Shape):
        '''create a new shape, on the team as creating_shape, with the attributes of model_shape'''
        
        if creating_shape.team_id == 0:
            shape = Shape(self.team_1_team_size, creating_shape.team_id, resurrected_creator=creating_shape, resurrected_model=model_shape)
            self.team_1_team_size += 1
            self.team_1_max_hp += shape.hp
            self.team_1_total_hp += shape.hp
            self.team_1_group.add(shape)

            # if adding a member to team 1, move team 2 stats surface location
            self.team_2_stats_rect.topleft = [self.team_2_stats_rect.x, 164 + int(20.6 * (self.team_1_team_size))]
        
        else:
            shape = Shape(self.team_2_team_size, creating_shape.team_id, resurrected_creator=creating_shape, resurrected_model=model_shape)
            self.team_2_team_size += 1
            self.team_2_max_hp += shape.hp
            self.team_2_total_hp += shape.hp
            self.team_2_group.add(shape)

        # add clouds
        self.clouds_group.add(Clouds(shape, self.cloud_images))

        # determine if team overview needs to be rendered
        self.checkTeamOverviewChanges(creating_shape.team_id)

        # play sounds, create killfeed
        self.playSound(self.choir_sound)
        self.addKillfeed(creating_shape, ACTION_RESURRECT, shape)

        # add shape to front of stats render queue
        self.shape_rerender_list.append(shape)
        self.shape_rerender_queue.queue.insert(0, shape)

        # update creating shape stats
        creating_shape.stats.resurrectShape()
        creating_shape.stats_to_render.append('resurrects')

        # resize the bounding circle
        self.updateBoundaryCircle()

    def blowupBomb(self, shape: Shape):
        self.num_active_bombs -= 1

        if not self.player_simulated and not self.server_simulated:
            # add to group
            self.clouds_group.add(Clouds(shape, self.explosion_images))

            self.playSound(self.explosion_sound)
            if self.num_active_bombs == 0: self.fuse_sound.stop()

        # reset shape bomb timer
        shape.bomb_timer = -999

        kills = 0
        x, y = shape.getXY()

        for shape_2 in itertools.chain(self.team_1_group, self.team_2_group):
            if shape_2.is_dead: continue

            [x2, y2] = shape_2.getXY()
            dist = math.sqrt( (x2- x)**2 + (y2 - y)** 2)

            if dist <= 200:
                self.shapeDamageShape(shape, shape_2, 200-dist)

            if shape_2.is_dead:
                kills += 1

        if kills >= 2 and 'resurrect' not in shape.powerup_arr:
            self.shapeRespawnShape(shape, shape)

    def shapeDamageShape(self, winner: Shape, loser: Shape, amount: int):
        '''exchange blows between two shapes. handles shape image and stat rendering, and team overview'''

        amount = int(min(loser.hp, amount))

        loser.takeDamage(amount)
        winner.dealDamage(amount)

        if loser.team_id == 0: self.team_1_total_hp -= amount
        else: self.team_2_total_hp -= amount
        self.checkTeamOverviewChanges(loser.team_id)

        if loser.is_dead: 
            winner.killShape()
            choice = self.getRandom(self.death_sounds)
            self.playSound(choice)
             #print(f'death sound: {choice}')

    def attemptKillfeed(self, winner: Shape, loser: Shape):
        '''attempt to make a killfeed entry after two shapes deal damage'''

        if not loser.is_dead: return

        # create killfeed element and play extra sounds
        if 'skull' in winner.powerup_arr:
            self.addKillfeed(winner, KILL_SKULL, loser)
            self.playSound(self.shotgun_sound)

            winner.removePowerup('skull')

        elif 'star' in winner.powerup_arr:
            self.addKillfeed(winner, KILL_STAR, loser)

        elif 'boxing_glove' in winner.powerup_arr:
            self.addKillfeed(winner, KILL_BOXING_GLOVE, loser)
            self.playSound(self.punch_sound)

        else: self.addKillfeed(winner, 'kill', loser)

    def attemptResurrect(self, winner: Shape, loser: Shape):
        '''attempt to resurrect a shape after two shapes deal damage'''

        if not loser.is_dead: return

        # check if any shapes will be resurrected
        if 'resurrect' in loser.powerup_arr:
            self.shapeRespawnShape(loser, loser)
            loser.removePowerup('resurrect')

        elif 'resurrect' in winner.powerup_arr:
            self.shapeRespawnShape(winner, loser)
            winner.removePowerup('resurrect')

    def activatePowerups(self, winner: Shape, loser: Shape):
        # remove any powerups from loser which are lost on incoming damage
        loser.removePowerup('star')
        loser.removePowerup('boxing_glove')

        # activate any powerups from winner which are used on outgoing damage
        if 'cherry' in winner.powerup_arr:
            winner.removePowerup('cherry')
            self.healShape(winner, round(winner.max_hp/3))

        if 'laser' in winner.powerup_arr:
            self.playSound(self.laser_sound)

            winner.removePowerup('laser')
            self.laser_group.add(Laser(winner, self.laser_images))

        if 'buckshot' in winner.powerup_arr:
            self.playSound(self.laser_sound)

            winner.removePowerup('buckshot')

            directions = [
                [0, 30],
                [21, 21], 
                [30, 0],
                [21, -21],
                [0, -30],
                [-21, -21],
                [-30, 0],
                [-21, 21]
            ]
            
            for direction in directions: self.laser_group.add(Buckshot(winner, direction, self.buckshot_images))
    
    # RENDERING HELPERS
    
    def determineNumShapesAlive(self, team_id: int):
        '''returns the number of shapes that are alive for the given team'''
        
        return sum(1 for shape in self.team_1_group.sprites() if not shape.is_dead) if team_id == 0 else sum(1 for shape in self.team_2_group.sprites() if not shape.is_dead)

    def determineTeamOverviewHealthPercent(self, team_id):
        '''return the current health of the given team, rounded to 1 decimal point'''

        hp_p = round((self.team_1_total_hp / self.team_1_max_hp) * 100, 1) if team_id == 0 else round((self.team_2_total_hp / self.team_2_max_hp) * 100, 1)

        # no decimal on 100%
        if hp_p == 100.0: hp_p = 100

        return hp_p

    def determineTeamOverviewFaceId(self, team_id: int):
        '''return the current id of the shape face that should be displayed on the team overview'''

        hp_percent = round((self.team_1_total_hp / self.team_1_max_hp) * 100) if team_id == 0 else round((self.team_2_total_hp / self.team_2_max_hp) * 100)
        
        if hp_percent >= 75: return 0
        elif hp_percent < 75 and hp_percent >= 50: return 1
        elif hp_percent < 50 and hp_percent >= 25: return 2
        else: return 3

    def checkTeamOverviewChanges(self, team_id: int):
        '''determine if any values regarding the team overviews have changed. if so, alter them and flag section to be rendered'''
        
        # check if face id has changed
        current_overview_face = self.determineTeamOverviewFaceId(team_id)
        if current_overview_face != (self.team_1_overview_face_id if team_id == 1 else self.team_2_overview_face_id):

            if team_id == 0: self.team_1_overview_face_id = current_overview_face
            else: self.team_2_overview_face_id = current_overview_face

            self.team_overview_sections_to_render.append(f'shape_{team_id}')

        # check if hp_p has changed
        current_hp_p = self.determineTeamOverviewHealthPercent(team_id)
        if current_hp_p != self.team_1_hp_p if team_id == 0 else self.team_2_hp_p:

            if team_id == 0: self.team_1_hp_p = current_hp_p
            else: self.team_2_hp_p = current_hp_p

            self.team_overview_sections_to_render.append(f'hp_{team_id}')

        # check if team size has changed
        shapes_alive = self.determineNumShapesAlive(team_id)
        if shapes_alive != (self.team_1_shape_count if team_id == 0 else self.team_2_shape_count):

            if team_id == 0: self.team_1_shape_count = shapes_alive
            else: self.team_2_shape_count = shapes_alive

            self.team_overview_sections_to_render.append(f'count_{team_id}')

    def eraseTextFromBackground(self, background: Surface, text: Text):
        '''erase the given text from the given background by setting all pixels beneath the text's rect to transparent '''
        
        if text == None: return

        x_offset, y_offset = text.rect.topleft

        for x in range(text.rect.width):
            for y in range(text.rect.height):
                x_abs, y_abs = x_offset + x, y_offset + y
                background.set_at((x_abs, y_abs), (0, 0, 0, 0))

        del text

    # RENDERING FUNCTIONS (render surfaces on surfaces)

    def renderTeamOverview(self):
        if self.team_overview_sections_to_render == []: return

        team_2_offset = 150

        if 'shape_0' in self.team_overview_sections_to_render or 'all' in self.team_overview_sections_to_render:
            # update image
            self.team_1_overview_image = pygame.transform.smoothscale(self.team_1_overview_images[self.team_1_overview_face_id], [125, 125])
            rect = self.team_1_overview_image.get_rect()
            rect.topleft = [0, 0]

            clearSurfaceBeneath(self.team_overview_surface, rect)
            self.team_overview_surface.blit(self.team_1_overview_image, rect)

        if 'shape_1' in self.team_overview_sections_to_render or 'all' in self.team_overview_sections_to_render:
            # update image
            self.team_2_overview_image = pygame.transform.smoothscale(self.team_2_overview_images[self.team_2_overview_face_id], [125, 125])
            rect = self.team_2_overview_image.get_rect()
            rect.topleft = [team_2_offset, 0]

            clearSurfaceBeneath(self.team_overview_surface, rect)
            self.team_overview_surface.blit(self.team_2_overview_image, rect)
            
        if 'count_0' in self.team_overview_sections_to_render or 'all' in self.team_overview_sections_to_render:
            # erase the previous text, recreate
            self.eraseTextFromBackground(self.team_overview_surface, self.team_1_count_text)
            self.team_1_count_text = Text(f'x{self.team_1_shape_count}', 40, 60, 145, color='black')
            self.team_overview_surface.blit(self.team_1_count_text.surface, self.team_1_count_text.rect)

        if 'count_1' in self.team_overview_sections_to_render or 'all' in self.team_overview_sections_to_render:
            # erase the previous text, recreate
            self.eraseTextFromBackground(self.team_overview_surface, self.team_2_count_text)
            self.team_2_count_text = Text(f'x{self.team_2_shape_count}', 40, 60 + team_2_offset, 145, color='black')
            self.team_overview_surface.blit(self.team_2_count_text.surface, self.team_2_count_text.rect)

        if 'hp_0' in self.team_overview_sections_to_render or 'all' in self.team_overview_sections_to_render:
            # erase the previous text, recreate
            self.eraseTextFromBackground(self.team_overview_surface, self.team_1_hp_text)
            self.team_1_hp_text = Text(f'{self.team_1_hp_p}%', 40, 60, 180, color='black')
            self.team_overview_surface.blit(self.team_1_hp_text.surface, self.team_1_hp_text.rect)

        if 'hp_1' in self.team_overview_sections_to_render or 'all' in self.team_overview_sections_to_render:
            # erase the previous text, recreate
            self.eraseTextFromBackground(self.team_overview_surface, self.team_2_hp_text)
            self.team_2_hp_text = Text(f'{self.team_2_hp_p}%', 40, 60 + team_2_offset, 180, color='black')
            self.team_overview_surface.blit(self.team_2_hp_text.surface, self.team_2_hp_text.rect)

        self.team_overview_sections_to_render = []

    def renderShapeStats(self, shape: Shape):
        '''renders a single shape's stats using shape.stats_to_render attribute. valid stats are 'all', 'hp', 'dmg_dealt', 'dmg_received', 'kills', 'resurrects', 'powerups_collected', '''

        # if this shape isn't new, remove it from the tracking list
        if shape in self.shape_rerender_list: self.shape_rerender_list.remove(shape) 

        surface = self.team_1_stats if shape.team_id == 0 else self.team_2_stats
        
        color = 'black' if shape.is_dead <= 0 else 'red'

        y_offset = 161
        x_offset = 60
        y_pos = int(y_offset + (shape.shape_id * 20.6))
        x_pos = x_offset
        font_size = 20

        if shape.id_stat_text == None or 'all' in shape.stats_to_render:
            # if stats has already been rendered, erase it
            self.eraseTextFromBackground(surface, shape.id_stat_text)

            shape.id_stat_text = Text(f'{shape.shape_id}:', font_size, (2 if shape.shape_id >= 10 else 10) + x_pos, y_pos, color=color)
            surface.blit(shape.id_stat_text.surface, shape.id_stat_text.rect)

        x_pos += 60
        if 'hp' in shape.stats_to_render or 'all' in shape.stats_to_render:
            # if stats has already been rendered, erase it
            self.eraseTextFromBackground(surface, shape.hp_stat_text)

            # replace stat text and blit
            hp_str = str(max(round(shape.hp / shape.max_hp * 100), 0)) + '%'
            shape.hp_stat_text = Text(hp_str, font_size, x_pos, y_pos, color=color)
            surface.blit(shape.hp_stat_text.surface, shape.hp_stat_text.rect)

        x_pos += 60
        if 'kills' in shape.stats_to_render or 'all' in shape.stats_to_render:
            # if stats has already been rendered, erase it
            self.eraseTextFromBackground(surface, shape.kills_stat_text)

            # replace stat text and blit
            shape.kills_stat_text = Text(str(shape.stats.kills), font_size, x_pos, y_pos, color=color)
            surface.blit(shape.kills_stat_text.surface, shape.kills_stat_text.rect)

        x_pos += 70
        if 'resurrects' in shape.stats_to_render or 'all' in shape.stats_to_render:
            # if stats has already been rendered, erase it
            self.eraseTextFromBackground(surface, shape.resurrects_stat_text)

            # replace stat text and blit
            shape.resurrects_stat_text = Text(str(shape.stats.resurrects), font_size, x_pos, y_pos, color=color)
            surface.blit(shape.resurrects_stat_text.surface, shape.resurrects_stat_text.rect)

        x_pos += 70
        if 'dmg_dealt' in shape.stats_to_render or 'all' in shape.stats_to_render:
            # if stats has already been rendered, erase it
            self.eraseTextFromBackground(surface, shape.dmg_dealt_stat_text)

            # replace stat text and blit
            shape.dmg_dealt_stat_text = Text(str(shape.stats.dmg_dealt), font_size, x_pos, y_pos, color=color)
            surface.blit(shape.dmg_dealt_stat_text.surface, shape.dmg_dealt_stat_text.rect)

        x_pos += 70
        if 'dmg_received' in shape.stats_to_render or 'all' in shape.stats_to_render:
            # if stats has already been rendered, erase it
            self.eraseTextFromBackground(surface, shape.dmg_received_stat_text)

            # replace stat text and blit
            shape.dmg_received_stat_text = Text(str(shape.stats.dmg_received), font_size, x_pos, y_pos, color=color)
            surface.blit(shape.dmg_received_stat_text.surface, shape.dmg_received_stat_text.rect)

        x_pos += 70
        if 'powerups_collected' in shape.stats_to_render or 'all' in shape.stats_to_render:
            # if stats has already been rendered, erase it
            self.eraseTextFromBackground(surface, shape.powerups_collected_stat_text)

            # replace stat text and blit
            shape.powerups_collected_stat_text = Text(str(shape.stats.powerups_collected), font_size, x_pos, y_pos, color=color)
            surface.blit(shape.powerups_collected_stat_text.surface, shape.powerups_collected_stat_text.rect)

        # once all stats have been rendered, clear list
        shape.stats_to_render = []
        
    # DRAWING FUNCTIONS (draw surfaces to the screen)

    def drawGameElements(self):
        '''draw all game elements (shapes, powerups, killfeed), separate from updateGameElements for easier simulation'''

        # draw background here since we want shapes on bottom layer
        self.screen.blit(self.background, (0, 0))
        self.screen.blit(self.boundary_circle_surface, self.boundary_circle_rect)

        # draw groups
        self.powerup_group.draw(self.screen)
        self.killfeed_group.draw(self.screen)
        self.laser_group.draw(self.screen)
        for shape in itertools.chain(self.team_1_group, self.team_2_group):
            if not shape.is_dead: self.screen.blit(shape.image, shape.rect)
        self.clouds_group.draw(self.screen)

    def drawStatsWindow(self):
        '''update and draw the stats window if necessary'''

        # rerender exactly one shape's stats per frame
        if self.shape_rerender_queue.qsize() >= 1 and self.frames_played % 10 == 0:
            self.renderShapeStats(self.shape_rerender_queue.get())

        # handle the window positioning
        if self.stats_window_current_x != self.stats_window_next_x:
            # calculate the remaining distance to the target
            distance = abs(self.stats_window_current_x - self.stats_window_next_x)

            # apply acceleration while far from the target, decelerate when close
            if distance > 50:
                self.stats_window_velocity += self.stats_window_acceleration
            else:
                self.stats_window_velocity = max(1, distance * 0.2)

            # move the window towards the target position, snap in place if position is exceeded
            if self.stats_window_current_x > self.stats_window_next_x:
                self.stats_window_current_x -= self.stats_window_velocity

                if self.stats_window_current_x < self.stats_window_next_x:
                    self.stats_window_current_x = self.stats_window_next_x

            elif self.stats_window_current_x < self.stats_window_next_x:
                self.stats_window_current_x += self.stats_window_velocity
                
                if self.stats_window_current_x > self.stats_window_next_x:
                    self.stats_window_current_x = self.stats_window_next_x 

            # reset the velocity when the window reaches its target
            if self.stats_window_current_x == self.stats_window_next_x:
                self.stats_window_velocity = 0

            self.stats_window_rect.topleft = [self.stats_window_current_x, self.stats_window_y]
            self.team_2_stats_rect.topleft = [self.stats_window_current_x, self.stats_window_y + 164 + int(20.6 * (self.team_1_team_size))]

        if self.stats_window_current_x != 1920:
            if self.stats_window_held:
                mouse_pos = pygame.mouse.get_pos()
                
                self.stats_window_y = mouse_pos[1] - self.mouse_y_when_clicked + self.stats_window_y_when_clicked

                if self.stats_window_y > 0: self.stats_window_y = 0

                if self.stats_window_y < self.stats_window_min_y: self.stats_window_y = self.stats_window_min_y

                self.stats_window_rect.topleft = [self.stats_window_current_x, self.stats_window_y]
                self.team_2_stats_rect.topleft = [self.stats_window_current_x, self.stats_window_y + 164 + int(20.6 * (self.team_1_team_size))]

        self.screen.blit(self.stats_window, self.stats_window_rect)
        self.screen.blit(self.team_1_stats, self.stats_window_rect)
        self.screen.blit(self.team_2_stats, self.team_2_stats_rect)

    def drawTeamOverview(self):
        '''update and draw the team overview if necessary'''
        
        # save some resources, do this 4 times per second
        if self.frames_played % 15 == 0: self.renderTeamOverview()

        # slightly rotate the surface to match the sticky note
        rotated_surface = pygame.transform.rotate(self.team_overview_surface, -2)

        self.screen.blit(rotated_surface, self.team_overview_rect)

    def drawScreenElements(self):
        '''update and draw any and all screen elements'''

        mouse_pos = pygame.mouse.get_pos()

        self.drawTeamOverview()

        # handle stats window things
        self.drawStatsWindow()

        # draw clickable elements
        [clickable.draw(self.screen) for clickable in self.clickables if clickable not in [None]]

        # if game is done, show victory text
        if self.done: self.screen.blit(self.player_win_text.surface, self.player_win_text.rect)
        self.title_text.draw(self.screen)


        # update and draw cursor
        self.cursor_rect.center = pygame.mouse.get_pos()
        self.screen.blit(self.cursor, self.cursor_rect)

        # finally flip the display
        pygame.display.flip()

    def drawStatsWindowHeaders(self):
        '''draw all of the header information to the stats window surfaces. only called once in init'''

        # draw all the text

        font_size = 23
        font_size_smaller = 22
        y_offset = 118
        x_offset = 60
        y_pos = y_offset
        y_pos_2_lines = y_pos - font_size_smaller
        x_pos = x_offset
        x_increment = 70
        
        id_text = Text('id', font_size, x_pos+8, y_pos, color='black')

        x_pos += 60
        hp_text = Text('hp', font_size, x_pos, y_pos, color='black')

        x_pos += 60
        kills_text = Text('kills', font_size, x_pos, y_pos, color='black')

        x_pos += x_increment
        resurrects_text = Text(['shapes', 'rez\'d'], font_size_smaller, x_pos, y_pos_2_lines, color='black')

        x_pos += x_increment
        dmg_dealt_text = Text(['dmg', 'out'], font_size_smaller, x_pos, y_pos_2_lines, color='black')

        x_pos += x_increment
        dmg_taken_text = Text(['dmg', 'in'], font_size_smaller, x_pos, y_pos_2_lines, color='black')

        x_pos += x_increment
        powerups_collected_text = Text(['pwrups', 'held'], font_size_smaller, x_pos, y_pos_2_lines, color='black')

        for surface, user, group in zip([self.team_1_stats, self.team_2_stats], [self.user_1, self.user_2], [self.team_1_group, self.team_2_group]):

            shape_image = pygame.transform.smoothscale(group.sprites()[0].shape_images[0], [98, 98])
            team_name_text = Text(f'team {user.username}', 45, 220, 15, 'topleft', 'black')
            
            surface.blit(id_text.surface, id_text.rect)
            surface.blit(hp_text.surface, hp_text.rect)
            surface.blit(kills_text.surface, kills_text.rect)
            surface.blit(resurrects_text.surface, resurrects_text.rect)
            surface.blit(dmg_dealt_text.surface, dmg_dealt_text.rect)
            surface.blit(dmg_taken_text.surface, dmg_taken_text.rect)
            surface.blit(powerups_collected_text.surface, powerups_collected_text.rect)

            surface.blit(team_name_text.surface, team_name_text.rect)
            surface.blit(shape_image, [95, 5])

            # draw team name

    # TESTING FUNCTIONS

    def getRandom(self, selections: list):
        idx = random.randint(0, len(selections)-1)
        
        return selections[idx]

    def testFps(self):
        fps = self.clock.get_fps()
        
        self.sum_fps += fps
        if (fps < self.fps_low and fps > 30): self.fps_low = fps
        if (fps > self.fps_high): self.fps_high = fps

    # GAME LOOPS

    def simulate(self):
        '''game simulation driver''' 

    def play(self):
        '''game play driver'''
        self.prev_time = time.time()

        self.transitionIn()
        
        while self.running:
            events = pygame.event.get()

            self.updateGameState(events)            

            self.checkForCompletion()

            self.handleInputs(events)

            self.drawGameElements()

            self.drawScreenElements()

            self.clock.tick(self.target_fps)

        self.transitionOut()
        # print(f'game played for: {self.frames_played} frames. FPS AVG: {self.sum_fps / self.frames_played} low: {self.fps_low} high: {self.fps_high}')

