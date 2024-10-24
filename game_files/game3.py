import pygame, random, os, numpy, math, time, itertools
from queue import Queue
from pygame import Surface
from pygame.locals import *
from pygame.sprite import Group
import pygame.sprite

from screen_elements.clickabletext import ClickableText
from screen_elements.doublecheckbox import DoubleCheckbox
from screen_elements.text import Text

from createdb import User, Shape as ShapeData

from game_files.shape2 import Shape
from game_files.powerup2 import Powerup
from game_files.circledata import *
from game_files.circledata import colors as color_data
from game_files.gamedata import color_data

RENDER_W = 854
RENDER_H = 480

class Game3:
    def __init__(self, screen: Surface, shape_1_data: ShapeData, shape_2_data: ShapeData, user_1: User, user_2: User, seed = False, player_simulated = False, server_simulated = False):
        # seed randomness
        if seed != False: random.seed(seed)
        
        # parameters from menu
        self.screen = screen
        self.render_surface = pygame.Surface([RENDER_W, RENDER_H], pygame.SRCALPHA, 32)
        self.shape_1_data = shape_1_data
        self.shape_2_data = shape_2_data
        self.user_1 = user_1
        self.user_2 = user_2
        self.seed = seed

        # necessary variables for simulating game
        self.running = True
        self.done = False
        self.p1_win = False
        self.p2_win = False
        self.player_win_text = None
        self.screen_w = RENDER_W
        self.screen_h = RENDER_H
        self.fps = 60
        self.frames = 0

        self.powerup_data = powerup_data

        # flags for simulation efficiency
        self.player_simulated = player_simulated
        self.server_simulated = server_simulated

        # variables for all data on shapes and teams
        self.team_1_team_size = shape_1_data.team_size
        self.team_2_team_size = shape_2_data.team_size
        self.team_1_shape_count = shape_1_data.team_size
        self.team_2_shape_count = shape_2_data.team_size
        self.total_shape_count = self.team_1_shape_count + self.team_2_shape_count

        self.team_1_max_hp = shape_1_data.health * shape_1_data.team_size
        self.team_2_max_hp = shape_2_data.health * shape_2_data.team_size

        self.team_1_total_hp = shape_1_data.health * shape_1_data.team_size
        self.team_2_total_hp = shape_2_data.health * shape_2_data.team_size

        self.team_1_group = Group()
        self.team_2_group = Group()

        # additional groups
        self.powerup_group = Group()
        self.laser_group = Group()
        self.buckshot_group = Group()
        self.clouds_group = Group()
        self.explosions_group = Group()
        self.killfeed_group = Group()

        # define containers for images
        self.shape_1_face_images = []
        self.shape_2_face_images = []

        self.smoke_images = []
        self.powerup_images_small = []
        self.powerup_images_medium = []

        # ALL SIMULATION NECESSARY THINGS ABOVE THIS POINT
        if self.server_simulated: return

        # TODO load necessary images for stats screen
        if self.player_simulated: 
            return
        
        # load background and update display
        self.background = pygame.image.load('backgrounds/grid_paper_w_sides_small.png').convert_alpha()
        self.title_text = Text('shapegame', 125, RENDER_W/2, RENDER_H/5)
        self.render_surface.blit(self.background, (0, 0))
        self.render_surface.blit(self.title_text.surface, self.title_text.rect)
        pygame.display.update()

        # all stats screen variables
        self.shape_rerender_queue = Queue()
        self.shape_rerender_list = []
        self.stats_window_shown = False
        self.stats_window: Surface = pygame.image.load('backgrounds/side_window_long_small.png').convert_alpha()
        # self.stats_window.set_alpha(200)
        
        self.team_1_stats: Surface = pygame.Surface((self.stats_window.get_size()[0], self.stats_window.get_size()[1]), pygame.SRCALPHA, 32)
        self.team_2_stats: Surface = pygame.Surface((self.stats_window.get_size()[0], self.stats_window.get_size()[1]), pygame.SRCALPHA, 32)
        self.team_2_stats_rect = self.team_2_stats.get_rect() # no need for team_1_stats_rect as the stats_window_rect will be identical
        self.stats_window_rect = self.stats_window.get_rect()
        self.stats_window_rect.topleft = [RENDER_W, 0]
        self.team_2_stats_rect.topleft = [RENDER_W, 72 + int(9.1 * (self.team_1_team_size))]
        self.stats_window_current_x = RENDER_W
        self.stats_window_next_x = RENDER_W
        
        self.stats_window_velocity = 0
        self.stats_window_acceleration = 1.5
        
        self.stats_window_held = False
        self.stats_window_y_when_clicked = 0
        self.mouse_y_when_clicked = 0
        self.stats_window_y = 0
        self.stats_window_min_y = (int((72 * 2) + (self.team_1_team_size * 9.1) + (self.team_1_team_size * 9.1)) - RENDER_W) / 2

        # necessary variables for playing game
        self.clock = pygame.time.Clock()

        # load powerup images
        for powerup in self.powerup_data:
            image = pygame.image.load(self.powerup_data[powerup][0])
            self.powerup_images_small.append(pygame.transform.smoothscale(image, (20, 20)))
            self.powerup_images_medium.append(pygame.transform.smoothscale(image, (40, 40)))

        # load healthbar images for each shape
        self.shape_1_healthbar_images = self.getHealthbarImages(shape_1_data)
        # worth checking if shapes share images to save resources
        if shape_1_data.type == shape_2_data.type: self.shape_2_healthbar_images = self.shape_1_healthbar_images
        else: self.shape_2_healthbar_images = self.getHealthbarImages(shape_2_data)

        # load face images for each shape
        self.shape_1_face_images = self.getFaceImages(shape_1_data)
        self.shape_2_face_images = self.getFaceImages(shape_2_data)

        # load sounds

        # Sounds
        self.death_sounds = []
        self.death_sounds.append(pygame.mixer.Sound("sounds/death/1.wav"))
        self.death_sounds.append(pygame.mixer.Sound("sounds/death/2.wav"))
        self.death_sounds.append(pygame.mixer.Sound("sounds/death/3.wav"))
        self.death_sounds.append(pygame.mixer.Sound("sounds/death/4.wav"))

        self.collision_sounds = []
        self.collision_sounds.append(pygame.mixer.Sound("sounds/collisions/clink1.wav"))
        self.collision_sounds.append(pygame.mixer.Sound("sounds/collisions/clink2.wav"))
        self.collision_sounds.append(pygame.mixer.Sound("sounds/collisions/thud2.wav"))

        self.game_sounds = []
        self.game_sounds.append(pygame.mixer.Sound("sounds/game/1.wav"))

        self.choir_sound = pygame.mixer.Sound("sounds/choir.wav")
        self.explosion_sound = pygame.mixer.Sound("sounds/explosion.flac")
        self.fuse_sound = pygame.mixer.Sound("sounds/fuse.wav")
        self.heal_sound = pygame.mixer.Sound("sounds/heal.wav")
        self.laser_hit_sound = pygame.mixer.Sound("sounds/laser_hit.wav")
        self.laser_sound = pygame.mixer.Sound("sounds/laser.wav")
        self.pop_sound = pygame.mixer.Sound("sounds/pop.wav")
        self.punch_sound = pygame.mixer.Sound("sounds/punch.wav")
        self.shotgun_sound = pygame.mixer.Sound("sounds/shotgun.wav")
        self.twinkle_sound = pygame.mixer.Sound("sounds/twinkle.wav")
        self.win_sound = pygame.mixer.Sound("sounds/win.wav")
        self.wind_sound = pygame.mixer.Sound("sounds/wind.wav")
        self.click_sound = pygame.mixer.Sound("sounds/click.wav")
        self.close_sound = pygame.mixer.Sound("sounds/close.wav")

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


        # create screen elements
        self.exit_clickable = ClickableText('back', 25, RENDER_W-30, RENDER_H-15)
        self.clickables = [self.exit_clickable]

        # load and center cursor
        self.cursor = pygame.transform.smoothscale(pygame.image.load('backgrounds/cursor.png'), (8, 8))
        self.cursor_rect = self.cursor.get_rect()
        self.cursor_rect.center = pygame.mouse.get_pos()

        # create shapes
        for i in range(0, shape_1_data.team_size):
            shape = Shape(shape_1_data, color_data[shape_1_data.color_id], i, 0, self.shape_1_face_images, self.powerup_images_small, self.shape_1_healthbar_images)
            
            self.team_1_group.add(shape)
            self.renderShapeStats(shape)

        for i in range(0, shape_2_data.team_size):
            shape = Shape(shape_2_data, color_data[shape_2_data.color_id], i, 1, self.shape_2_face_images, self.powerup_images_small, self.shape_2_healthbar_images)

            self.team_2_group.add(shape)
            self.renderShapeStats(shape)

        # create stats window headers now that shape images have been loaded
        self.drawStatsWindowHeaders()

        # team overview variables now that shape images have been loaded
        self.team_overview_surface = pygame.Surface((145, 145), pygame.SRCALPHA, 32)
        self.team_overview_rect = self.team_overview_surface.get_rect()
        self.team_overview_rect.topleft = [RENDER_W-140, 55]
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

    def renderTeamOverview(self):
        if self.team_overview_sections_to_render == []: return

        shape_size = 60
        team_2_offset = 65
        x = 30
        font_size = 20
        count_y = 70
        hp_y = 90

        if 'shape_0' in self.team_overview_sections_to_render or 'all' in self.team_overview_sections_to_render:
            # update image
            self.team_1_overview_image = pygame.transform.smoothscale(self.team_1_overview_images[self.team_1_overview_face_id], [shape_size, shape_size])
            self.team_overview_surface.blit(self.team_1_overview_image, [0, 0])

        if 'shape_1' in self.team_overview_sections_to_render or 'all' in self.team_overview_sections_to_render:
            # update image
            self.team_2_overview_image = pygame.transform.smoothscale(self.team_2_overview_images[self.team_2_overview_face_id], [shape_size, shape_size])
            self.team_overview_surface.blit(self.team_2_overview_image, [team_2_offset, 0])

        if 'count_0' in self.team_overview_sections_to_render or 'all' in self.team_overview_sections_to_render:
            # erase the previous text, recreate
            self.eraseTextFromBackground(self.team_overview_surface, self.team_1_count_text)
            self.team_1_count_text = Text(f'x{self.team_1_shape_count}', font_size, x, count_y, color='black')
            self.team_overview_surface.blit(self.team_1_count_text.surface, self.team_1_count_text.rect)

        if 'count_1' in self.team_overview_sections_to_render or 'all' in self.team_overview_sections_to_render:
            # erase the previous text, recreate
            self.eraseTextFromBackground(self.team_overview_surface, self.team_2_count_text)
            self.team_2_count_text = Text(f'x{self.team_2_shape_count}', font_size, x + team_2_offset, count_y, color='black')
            self.team_overview_surface.blit(self.team_2_count_text.surface, self.team_2_count_text.rect)

        if 'hp_0' in self.team_overview_sections_to_render or 'all' in self.team_overview_sections_to_render:
            # erase the previous text, recreate
            self.eraseTextFromBackground(self.team_overview_surface, self.team_1_hp_text)
            self.team_1_hp_text = Text(f'{self.team_1_hp_p}%', font_size, x, hp_y, color='black')
            self.team_overview_surface.blit(self.team_1_hp_text.surface, self.team_1_hp_text.rect)

        if 'hp_1' in self.team_overview_sections_to_render or 'all' in self.team_overview_sections_to_render:
            # erase the previous text, recreate
            self.eraseTextFromBackground(self.team_overview_surface, self.team_2_hp_text)
            self.team_2_hp_text = Text(f'{self.team_2_hp_p}%', font_size, x + team_2_offset, hp_y, color='black')
            self.team_overview_surface.blit(self.team_2_hp_text.surface, self.team_2_hp_text.rect)

        self.team_overview_sections_to_render = []

    def getHealthbarImages(self, shape_data: ShapeData):
        '''load and return an array of healthbar images for the given shape'''

        # default to number of images for circle health bar
        num_images = 17

        if shape_data.type == 'square':
            num_images = 19

        elif shape_data.type == 'triangle':
            num_images = 18

        images = []
        for i in range(num_images):
            images.append(pygame.image.load(f'shape_images/healthbars/{shape_data.type}/{i}.png'))

        return images

    def getFaceImages(self, shape_data: ShapeData):
        '''load and return an array of shape faces for the given shape'''
        images = []
        for i in range(4):
            images.append(pygame.image.load(f'shape_images/faces/{shape_data.type}/{shape_data.face_id}/{i}.png'))

        return images

    def handleInputs(self):
        ''' handle all inputs from user'''
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
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

                    if self.stats_window_shown: self.stats_window_next_x = RENDER_W - self.stats_window.get_size()[0]
                    else: self.stats_window_next_x = RENDER_W

    def spawnRandomPowerups(self):
        '''spawn a random powerup every few seconds'''

        if not self.done and self.frames % (10 * self.fps) == 0:
            powerup_name = random.choice(list(self.powerup_data.keys()))
            powerup_image = self.powerup_images_medium[self.powerup_data[powerup_name][1]]
            xy = [random.randint(20, self.screen_w - 20), random.randint(20, self.screen_h - 20)]

            self.playSound(self.pop_sound)
            self.powerup_group.add(Powerup(powerup_name, powerup_image, xy))

    def eraseTextFromBackground(self, background: Surface, text: Text):
        '''erase the given text from the given background by setting all pixels beneath the text's rect to transparent '''
        
        
        if text == None: return

        x_offset, y_offset = text.rect.topleft

        for x in range(text.rect.width):
            for y in range(text.rect.height):
                x_abs, y_abs = x_offset + x, y_offset + y
                background.set_at((x_abs, y_abs), (0, 0, 0, 0))

        del text

    def drawStatsWindowHeaders(self):
        '''draw all of the header information to the stats window surfaces. only called once in init'''

        # draw all the text

        font_size = 11
        font_size_smaller = 10
        y_offset = 55
        x_offset = 22
        y_pos = y_offset
        y_pos_2_lines = y_pos - font_size_smaller
        x_pos = x_offset
        x_increment = 30
        
        id_text = Text('id', font_size, x_pos+8, y_pos, color='black')

        x_pos += 30
        hp_text = Text('hp', font_size, x_pos, y_pos, color='black')

        x_pos += 33
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

            shape_image = pygame.transform.smoothscale(group.sprites()[0].shape_images[0], [43, 43])
            team_name_text = Text(f'team {user.username}', 20, 100, 8, 'topleft', 'black')
            
            surface.blit(id_text.surface, id_text.rect)
            surface.blit(hp_text.surface, hp_text.rect)
            surface.blit(kills_text.surface, kills_text.rect)
            surface.blit(resurrects_text.surface, resurrects_text.rect)
            surface.blit(dmg_dealt_text.surface, dmg_dealt_text.rect)
            surface.blit(dmg_taken_text.surface, dmg_taken_text.rect)
            surface.blit(powerups_collected_text.surface, powerups_collected_text.rect)

            surface.blit(team_name_text.surface, team_name_text.rect)
            surface.blit(shape_image, [42, 5])

            # draw team name

    def renderShapeStats(self, shape: Shape):
        '''renders a single shape's stats using shape.stats_to_render attribute. valid stats are 'all', 'hp', 'dmg_dealt', 'dmg_received', 'kills', 'resurrects', 'powerups_collected', '''

        # if this shape isn't new, remove it from the tracking list
        if shape.id_stat_text != None: self.shape_rerender_list.remove(shape) 

        surface = self.team_1_stats if shape.team_id == 0 else self.team_2_stats
        
        color = 'black' if shape.is_dead <= 0 else 'red'

        y_offset = 74
        x_offset = 25
        y_pos = int(y_offset + (shape.shape_id * 9.1))
        x_pos = x_offset
        font_size = 9
        x_increment = 30

        if shape.id_stat_text == None or 'all' in shape.stats_to_render:
            # if stats has already been rendered, erase it
            if shape.id_stat_text != None:
                self.eraseTextFromBackground(surface, shape.id_stat_text)

            shape.id_stat_text = Text(f'{shape.shape_id}:', font_size, (2 if shape.shape_id >= 10 else 5) + x_pos, y_pos, color=color)
            surface.blit(shape.id_stat_text.surface, shape.id_stat_text.rect)

        x_pos += 30
        if 'hp' in shape.stats_to_render or 'all' in shape.stats_to_render:
            # if stats has already been rendered, erase it
            if shape.hp_stat_text != None:
                self.eraseTextFromBackground(surface, shape.hp_stat_text)

            # replace stat text and blit
            hp_str = str(max(round(shape.hp / shape.max_hp * 100), 0)) + '%'
            shape.hp_stat_text = Text(hp_str, font_size, x_pos, y_pos, color=color)
            surface.blit(shape.hp_stat_text.surface, shape.hp_stat_text.rect)

        x_pos += 30
        if 'kills' in shape.stats_to_render or 'all' in shape.stats_to_render:
            # if stats has already been rendered, erase it
            if shape.kills_stat_text != None:
                self.eraseTextFromBackground(surface, shape.kills_stat_text)

            # replace stat text and blit
            shape.kills_stat_text = Text(str(shape.stats.kills), font_size, x_pos, y_pos, color=color)
            surface.blit(shape.kills_stat_text.surface, shape.kills_stat_text.rect)

        x_pos += x_increment
        if 'resurrects' in shape.stats_to_render or 'all' in shape.stats_to_render:
            # if stats has already been rendered, erase it
            if shape.resurrects_stat_text != None:
                self.eraseTextFromBackground(surface, shape.resurrects_stat_text)

            # replace stat text and blit
            shape.resurrects_stat_text = Text(str(shape.stats.resurrects), font_size, x_pos, y_pos, color=color)
            surface.blit(shape.resurrects_stat_text.surface, shape.resurrects_stat_text.rect)

        x_pos += x_increment
        if 'dmg_dealt' in shape.stats_to_render or 'all' in shape.stats_to_render:
            # if stats has already been rendered, erase it
            if shape.dmg_dealt_stat_text != None:
                self.eraseTextFromBackground(surface, shape.dmg_dealt_stat_text)

            # replace stat text and blit
            shape.dmg_dealt_stat_text = Text(str(shape.stats.dmg_dealt), font_size, x_pos, y_pos, color=color)
            surface.blit(shape.dmg_dealt_stat_text.surface, shape.dmg_dealt_stat_text.rect)

        x_pos += x_increment
        if 'dmg_received' in shape.stats_to_render or 'all' in shape.stats_to_render:
            # if stats has already been rendered, erase it
            if shape.dmg_received_stat_text != None:
                self.eraseTextFromBackground(surface, shape.dmg_received_stat_text)

            # replace stat text and blit
            shape.dmg_received_stat_text = Text(str(shape.stats.dmg_received), font_size, x_pos, y_pos, color=color)
            surface.blit(shape.dmg_received_stat_text.surface, shape.dmg_received_stat_text.rect)

        x_pos += x_increment
        if 'powerups_collected' in shape.stats_to_render or 'all' in shape.stats_to_render:
            # if stats has already been rendered, erase it
            if shape.powerups_collected_stat_text != None:
                self.eraseTextFromBackground(surface, shape.powerups_collected_stat_text)

            # replace stat text and blit
            shape.powerups_collected_stat_text = Text(str(shape.stats.powerups_collected), font_size, x_pos, y_pos, color=color)
            surface.blit(shape.powerups_collected_stat_text.surface, shape.powerups_collected_stat_text.rect)

        # once all stats have been rendered, clear list
        shape.stats_to_render = []
        
    def drawStatsWindow(self):
        '''update and draw the stats window if necessary'''

        # rerender exactly one shape's stats per frame
        if self.shape_rerender_queue.qsize() >= 1 and self.frames % 10 == 0:
            self.renderShapeStats(self.shape_rerender_queue.get())

        # handle the window positioning
        if self.stats_window_current_x != self.stats_window_next_x:
            # calculate the remaining distance to the target
            distance = abs(self.stats_window_current_x - self.stats_window_next_x)

            # apply acceleration while far from the target, decelerate when close
            if distance > 20:
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
            self.team_2_stats_rect.topleft = [self.stats_window_current_x, self.stats_window_y + 72 + int(9.1 * (self.team_1_team_size))]

        if self.stats_window_current_x != RENDER_W:
            if self.stats_window_held:
                mouse_pos = pygame.mouse.get_pos()
                
                self.stats_window_y = mouse_pos[1] - self.mouse_y_when_clicked + self.stats_window_y_when_clicked

                if self.stats_window_y > 0: self.stats_window_y = 0

                if self.stats_window_y < self.stats_window_min_y: self.stats_window_y = self.stats_window_min_y

                self.stats_window_rect.topleft = [self.stats_window_current_x, self.stats_window_y]
                self.team_2_stats_rect.topleft = [self.stats_window_current_x, self.stats_window_y + 72 + int(9.1 * (self.team_1_team_size))]

        self.render_surface.blit(self.stats_window, self.stats_window_rect)
        self.render_surface.blit(self.team_1_stats, self.stats_window_rect)
        self.render_surface.blit(self.team_2_stats, self.team_2_stats_rect)

    def drawTeamOverview(self):
        '''update and draw the team overview if necessary'''
        
        # save some resources, do this 4 times per second
        if self.frames % 15 == 0: self.renderTeamOverview()

        # slightly rotate the surface to match the sticky note
        rotated_surface = pygame.transform.rotate(self.team_overview_surface, -2).convert_alpha()

        self.render_surface.blit(rotated_surface, self.team_overview_rect)

    def drawScreenElements(self):
        '''update and draw any and all screen elements'''

        mouse_pos = pygame.mouse.get_pos()

        self.drawTeamOverview()

        # handle stats window things
        self.drawStatsWindow()


        # update and draw clickable elements
        for clickable in self.clickables:
            clickable.update(mouse_pos)
            self.render_surface.blit(clickable.surface, clickable.rect)

        # if game is done, show victory text
        if self.done: self.render_surface.blit(self.player_win_text.surface, self.player_win_text.rect)

        # update and draw cursor
        self.cursor_rect.center = pygame.mouse.get_pos()
        self.render_surface.blit(self.cursor, self.cursor_rect)

        # finally flip the display
        pygame.display.flip()

    def shapeCollectPowerup(self, shape: Shape, powerup: Powerup):
        '''handler for shape collecting a powerup'''

        # shapes can have max 5 powerups
        if len(shape.powerup_arr) == 5: return

        # handle everything that the game has to do regarding the pickup
        # (sounds, killfeed...)
        # if powerup.name == 'insta-kill':
        # elif powerup.name == 'resurrect':
        # elif powerup.name == 'star':
        # elif powerup.name == 'muscle':
        # elif powerup.name == 'speed':
        # elif powerup.name == 'health':
        # elif powerup.name == 'bomb':
        # elif powerup.name == 'laser':
        # elif powerup.name == 'buckshot':
        # elif powerup.name == 'mushroom':

        # let shape handle pickup
        shape.collectPowerup(powerup)
        
        # kill powerup
        powerup.kill()

    def repositionShapes(self, shape_1: Shape, shape_2: Shape):
        '''rectify the positions and velocities of two shapes which are currently colliding'''

        # STEP 0: move back a step
        # shape_1.move(True)
        # shape_2.move(True)

        # STEP 1

        [x2, y2] = shape_2.getXY()
        [x1, y1] = shape_1.getXY()

        [vx1i, vy1i] = shape_1.getV()
        [vx2i, vy2i] = shape_2.getV()

        norm_vec = numpy.array([x2 - x1, y2 - y1])

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

        [vx1f, vy1f] = shape_1.getV()
        [vx2f, vy2f] = shape_2.getV()

        # print(f'{vx1i}->{vx1f}')
        # print(f'{vy1i}->{vy1f}')
        # print(f'{vx2i}->{vx2f}')
        # print(f'{vy2i}->{vy2f}')

    def shapeDamageShape(self, winner: Shape, loser: Shape):
        '''handler for if two shapes of opposing teams collide and deal damage'''

        # limit amount of damage being done to losers current health
        dmg_amount = min(winner.getDamage(), loser.hp)

        winner.dealDamage(dmg_amount)
        loser.takeDamage(dmg_amount)

        # determine if team overview needs to be rendered
        # lower total team hp
        if loser.team_id == 0: self.team_1_total_hp -= dmg_amount
        else: self.team_2_total_hp -= dmg_amount
        self.checkTeamOverviewChanges(loser.team_id)
        
        if loser.is_dead:
            self.playSound(random.choice(self.death_sounds))
            winner.killShape()

    def determineNumShapesAlive(self, team_id: int):
        '''returns the number of shapes that are alive for the given team'''
        
        return sum(1 for shape in self.team_1_group.sprites() if not shape.is_dead) if team_id == 0 else sum(1 for shape in self.team_2_group.sprites() if not shape.is_dead)

    def checkTeamOverviewChanges(self, team_id: int):
        '''determine if any values regarding the team overviews have changed. if so, alter them and flag section to be rendered'''
        
        # check if face id has changed
        current_overview_face = self.determineTeamOverviewFaceId(team_id)
        if current_overview_face != self.team_1_overview_face_id if team_id == 0 else self.team_2_overview_face_id:

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

        # move collision mask back
        shape_1.collision_mask_rect.center = p1
        shape_2.collision_mask_rect.center = p2

        return bool(collision)

    def collideShapes(self, shape_1: Shape, shape_2: Shape):
        '''main handler for two shapes colliding'''
        self.playSound(random.choice(self.collision_sounds))

        # keep track of which shapes are touching this frame
        shape_1.shapes_touching.append(shape_2)
        
        self.repositionShapes(shape_1, shape_2)

        if shape_1.team_id == shape_2.team_id: return

        # get roll to determine winner
        roll_1 = random.randint(0, 20) + shape_1.luck
        roll_2 = random.randint(0, 20) + shape_2.luck

        if roll_1 == roll_2: return

        self.shapeDamageShape(shape_1, shape_2) if roll_1 > roll_2 else self.shapeDamageShape(shape_2, shape_1)
        
    def detectCollisions(self):
        '''simple method for collision detection, will want to be redone in theory, but for now isn't a large impact on performance'''
        # return
        
        for shape_1 in itertools.chain(self.team_1_group, self.team_2_group):

            if shape_1.stats_to_render != [] and shape_1 not in self.shape_rerender_list:
                self.shape_rerender_queue.put(shape_1)
                self.shape_rerender_list.append(shape_1)

            if shape_1.is_dead: continue

            for shape_2 in itertools.chain(self.team_1_group, self.team_2_group):
                if shape_1 == shape_2 or shape_2.is_dead: continue

                if self.determineCollision(shape_1, shape_2) and shape_2 not in shape_1.shapes_touching:
                    self.collideShapes(shape_1, shape_2)
                
                # keep track of which shapes you are not touching
                else:
                    if shape_2 in shape_1.shapes_touching: shape_1.shapes_touching.remove(shape_2)


            for powerup in self.powerup_group:
                dist = math.sqrt((powerup.x - shape_1.x)**2 + (powerup.y - shape_1.y)**2)
                max_dist = powerup.r + shape_1.r

                if (dist <= max_dist):
                    self.shapeCollectPowerup(shape_1, powerup)

    def updateGameElements(self):
        '''update all game elements (shapes, powerups, killfeed), separate from drawGameElements for easier simulation'''

        # spawn powerups
        self.spawnRandomPowerups()

        # update groups
        self.powerup_group.update()
        self.team_1_group.update()
        self.team_2_group.update()

        # detect collisions
        self.detectCollisions()

    def drawGameElements(self):
        '''draw all game elements (shapes, powerups, killfeed), separate from updateGameElements for easier simulation'''

        # draw background here since we want shapes on bottom layer
        self.render_surface.blit(self.background, (0, 0))

        # draw groups
        self.powerup_group.draw(self.render_surface)
        for shape in itertools.chain(self.team_1_group, self.team_2_group):
            if not shape.is_dead: self.render_surface.blit(shape.image, shape.rect)

    def playSound(self, sound):
        if self.player_simulated or self.server_simulated or sound.get_num_channels() > 3: return

        sound.play()
        
        if sound == self.wind_sound:
            pygame.mixer.Sound.fadeout(sound, 1500)
        
        elif sound == self.choir_sound:
            pygame.mixer.Sound.fadeout(sound, 1000)
        
        if sound == self.fuse_sound:
            sound.play(9)

    def checkForCompletion(self):
        '''check if one team is entirely dead. raises self.done and self.pX_win flag'''
        if self.done: return

        if all(shape.is_dead for shape in self.team_1_group): 
            self.done = True
            self.p2_win = True
        
        elif all(shape.is_dead for shape in self.team_2_group):
            self.done = True
            self.p2_win = True

        if self.done:
            # self.running = False

            self.playSound(self.win_sound)
            self.player_win_text = Text(f'{self.user_1.username if self.p1_win else self.user_2.username} wins!', 150, 1220/2, 1080/2, color='black')
        
    def play(self):
        '''game play driver'''
        total_fps = 0
        frames = 0
        fps_low = 300
        fps_high = 0

        while self.running:
            self.frames += 1

            self.checkForCompletion()

            self.handleInputs()

            self.updateGameElements()

            self.drawGameElements()

            self.drawScreenElements()

            self.screen.blit(pygame.transform.scale(self.render_surface, [1920, 1080]).convert(), [0, 0])

            # self.clock.tick(self.fps)
            
            self.clock.tick()
            fps = self.clock.get_fps()
            frames += 1
            total_fps += fps
            if (fps < fps_low and fps > 30): fps_low = fps
            if (fps > fps_high): fps_high = fps
            print(fps)

        print(f'smaller game played for: {frames} frames. FPS AVG: {total_fps / frames} low: {fps_low} high: {fps_high}')
