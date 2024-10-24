import  pygame, random, math, numpy as np
import pygame.surface
from game_files.shapestats import ShapeStats
from game_files.clouds import Clouds
from game_files.gamedata import ColorData
from game_files.laser import Laser
from game_files.powerup2 import Powerup
from createdb import User, Shape as ShapeData
from game_files.circledata import powerup_data
from screen_elements.text import Text 

RENDER_W = 854
RENDER_H = 480

class Shape(pygame.sprite.Sprite):
    def __init__(self, shape_data: ShapeData, color_data: ColorData, shape_id, team_id, face_images, hud_images, healthbar_imgs, resurrected = False, simulated = False):
        super().__init__()

        # attributes passed from game
        self.shape_data = shape_data
        self.type = shape_data.type
        self.color_data = color_data
        self.shape_id = shape_id
        self.team_id = team_id
        self.face_images = face_images
        self.hud_images = hud_images
        self.healthbar_imgs_full = healthbar_imgs

        # range of motion
        self.screen_w = RENDER_W - int(RENDER_W * 0.174)
        self.screen_h = RENDER_H 
        
        # check if this is a resurrected shape
        if resurrected == False:
            self.r = random.randint(shape_data.radius_min, shape_data.radius_max)
            self.m = round((3/4) * 3.14 * self.r**3)
            self.vx = shape_data.velocity if team_id == 1 else shape_data.velocity * -1
            self.vy = random.randint(-1, 1)
        
            # determine spawn location
            self.spawn_locations = [
                [
                    (self.screen_w - 150, self.screen_h / 6),  (self.screen_w - 150, 2 * self.screen_h / 6), (self.screen_w - 150, 3 * self.screen_h / 6), (self.screen_w - 150, 4 * self.screen_h / 6), (self.screen_w - 150, 5 * self.screen_h / 6),
                    (self.screen_w - 300, self.screen_h / 6),  (self.screen_w - 300, 2 * self.screen_h / 6), (self.screen_w - 300, 3 * self.screen_h / 6), (self.screen_w - 300, 4 * self.screen_h / 6), (self.screen_w - 300, 5 * self.screen_h / 6),
                    (self.screen_w - 450, self.screen_h / 6),  (self.screen_w - 450, 2 * self.screen_h / 6), (self.screen_w - 450, 3 * self.screen_h / 6), (self.screen_w - 450, 4 * self.screen_h / 6), (self.screen_w - 450, 5 * self.screen_h / 6),
                    (self.screen_w - 600, self.screen_h / 6),  (self.screen_w - 600, 2 * self.screen_h / 6), (self.screen_w - 600, 3 * self.screen_h / 6), (self.screen_w - 600, 4 * self.screen_h / 6), (self.screen_w - 600, 5 * self.screen_h / 6),
                    (self.screen_w - 700, self.screen_h / 6),  (self.screen_w - 700, 2 * self.screen_h / 6), (self.screen_w - 700, 3 * self.screen_h / 6), (self.screen_w - 700, 4 * self.screen_h / 6), (self.screen_w - 700, 5 * self.screen_h / 6),
                ], [
                    (150, self.screen_h / 6),  (150, 2 * self.screen_h / 6), (150, 3 * self.screen_h / 6), (150, 4 * self.screen_h / 6), (150, 5 * self.screen_h / 6),
                    (300, self.screen_h / 6),  (300, 2 * self.screen_h / 6), (300, 3 * self.screen_h / 6), (300, 4 * self.screen_h / 6), (300, 5 * self.screen_h / 6),
                    (450, self.screen_h / 6),  (450, 2 * self.screen_h / 6), (450, 3 * self.screen_h / 6), (450, 4 * self.screen_h / 6), (450, 5 * self.screen_h / 6),
                    (600, self.screen_h / 6),  (600, 2 * self.screen_h / 6), (600, 3 * self.screen_h / 6), (600, 4 * self.screen_h / 6), (600, 5 * self.screen_h / 6),
                    (700, self.screen_h / 6),  (700, 2 * self.screen_h / 6), (700, 3 * self.screen_h / 6), (700, 4 * self.screen_h / 6), (700, 5 * self.screen_h / 6),
                ], 
            ]

            self.x = self.spawn_locations[team_id][shape_id][0]
            self.y = self.spawn_locations[team_id][shape_id][1]

            # if you aren't spawning in a full row, move vertically
            num_remainders = shape_data.team_size % 5
            # print(num_remainders)
            if num_remainders != 0 and shape_id >= shape_data.team_size - num_remainders:
                self.y = ((shape_id+1) % 5) * self.screen_h / (num_remainders + 1)

        # healthbar things
        self.current_healthbar_image_id = 0
        self.healthbar_img = self.healthbar_imgs_full[self.current_healthbar_image_id]

        # all other necessary shape attributes
        self.luck = shape_data.luck
        self.dmg_x = shape_data.dmg_multiplier
        self.hp = shape_data.health
        self.max_hp = shape_data.health
        self.current_shape_image_id = 0
        self.necessary_surface_size = int(self.r*2) + 50 # 50 should be plenty for healthbar and powerups
        self.is_dead = False
        self.shapes_touching: list[Shape] = []
        '''list of shapes a shape is touching. used to prevent tunneled shapes from chunking each other'''
        
        # all stats related attributes
        self.stats = ShapeStats(self.shape_id)
        self.stats_surface = pygame.Surface((500, 20), pygame.SRCALPHA, 32)
        self.stats_to_render: list[str] = ['all'] # used in same way as shape_sections_to_render
        
        # define stat text attributes (created during first game.renderShapeStats call)
        self.id_stat_text = None
        self.hp_stat_text = None
        self.dmg_dealt_stat_text = None
        self.dmg_received_stat_text = None
        self.kills_stat_text = None
        self.resurrects_stat_text = None
        self.powerups_collected_stat_text = None

        # variables for growth state
        self.initial_r = self.r
        self.target_r = self.r + 100
        self.hold_counter = 0
        self.state = 'rest'
        """options are 'rest', 'holding', 'growing', 'shrinking'"""
        
        # store powerup data
        self.powerup_data = powerup_data
        
        # collection for powerup names
        self.powerup_arr: list[str] = []

        # get your body image from color data (default for circle)
        self.body_image = color_data.circle_image
        if self.type == 'square':
            self.body_image = color_data.square_image
        elif self.type == 'triangle':
            self.body_image = color_data.triangle_image

        # construct shape images (full sized)
        self.shape_images = []
        for i, face in enumerate(self.face_images):
            body_copy = self.body_image.convert_alpha()
            body_copy.blit(face, [0, 0])
            self.shape_images.append(body_copy)

        # render the shape
        self.shape_sections_to_render: list[str] = ["all"]     # used by render call, add sections to list during loop, cleared at beginning of next loop
        self.current_shape_image = pygame.transform.smoothscale(self.shape_images[0], (self.r*2, self.r*2))
        self.collision_mask = pygame.mask.from_surface(self.current_shape_image)
        self.collision_mask_rect = self.current_shape_image.get_rect()
        self.image = pygame.Surface((self.necessary_surface_size, self.necessary_surface_size), pygame.SRCALPHA, 32)
        self.powerups_surface = pygame.Surface((self.necessary_surface_size, self.necessary_surface_size), pygame.SRCALPHA, 32)
        self.rect = self.image.get_rect()
        self.renderSelf()

    def determineShapeImageId(self):
        """determines which image id a shape should use (based on health). returns id as int"""
        
        hp_percent = round((self.hp / self.max_hp) * 100)

        if hp_percent >= 75: return 0
        elif hp_percent < 75 and hp_percent >= 50: return 1
        elif hp_percent < 50 and hp_percent >= 25: return 2
        else: return 3

    def determineHealthbarImageId(self):
        """determines which healthbar image id a shape should use (based on health). returns id as int"""

        hp_percent = int((self.hp / self.max_hp) * 100)
        hp_percent_inverse = 100 - hp_percent

        # apply linear transformation formula: (hp - out-min) * (out_max - out_min) / (in_max - in_min) + out_min
        return min(int(hp_percent_inverse * (len(self.healthbar_imgs_full) - 1) / 100), len(self.healthbar_imgs_full)-1)

    def getDamage(self):
        velocity = math.sqrt(self.getV()[0]**2 + self.getV()[1]**2)

        if velocity == np.nan:
            velocity = 0

        return round(self.dmg_x * velocity * self.m / 10000)

    def takeDamage(self, amount):
        """reduce shapes health by amount, and check if image needs to be updated"""

        # update stats
        self.stats.receiveDamage(amount)
        self.stats_to_render = ['dmg_received']
        
        # take damage, die if it kills you
        self.hp -= amount
        if self.hp <= 0:
            self.is_dead = True
            self.stats_to_render.append('all')
        
        # check to see if healthbar image needs to be changed
        post_dmg_health_id = self.determineHealthbarImageId()
        if self.current_healthbar_image_id != post_dmg_health_id:
            self.current_healthbar_image_id = post_dmg_health_id
            self.shape_sections_to_render.append("healthbar")

        # check to see if shape image needs to be changed
        post_dmg_img_id = self.determineShapeImageId()
        if self.current_shape_image_id != post_dmg_img_id:
            self.current_shape_image_id = post_dmg_img_id
            self.shape_sections_to_render.append("shape")

        self.stats_to_render.append('hp')

    def dealDamage(self, amount):
        self.stats.dealDamage(amount)
        self.stats_to_render.append('dmg_dealt')

    def killShape(self):
        self.stats.killShape()
        self.stats_to_render.append('kills')

    def renderSelf(self):
        """renders shapes image using sections_to_render attribute. only renders what is needed. valid sections are "all", "face", "powerups" """
        # this function is called every frame, but rerendering isn't always needed
        if self.shape_sections_to_render == []: return   

        # variables for scaling healthbar images (defaults for circles)
        healthbar_scale_up = 1.10
        healthbar_y_translate = 0
        
        if self.type == 'square':
            healthbar_scale_up = 1.15
            healthbar_y_translate = 0.05

        # draw the face in the center of the surface
        if "shape" in self.shape_sections_to_render or "all" in self.shape_sections_to_render:
            # redetermine surface size incase of growth
            self.necessary_surface_size = int(self.r*2) + 50
            self.current_shape_image = pygame.transform.smoothscale(self.shape_images[self.current_shape_image_id], (self.r*2, self.r*2))

        # draw all powerups to appear in an arc beneath the shape
        if ("powerups" in self.shape_sections_to_render or "all" in self.shape_sections_to_render) and self.powerup_arr != []:

            # calculate distance all powerups should appear
            distance_to_center = self.r + 15
            powerup_positions: list[list[int]] = []

            # if only one powerup, position in the center
            if len(self.powerup_arr) == 1:
                powerup_positions = [[0, distance_to_center]]

            # if more than one powerup, calculate positions
            else:
                # circles have their powerups in an arc beneath them
                if self.type == 'circle':
                    # some calculations
                    arc_r = distance_to_center
                    start_angle = math.pi / 3
                    end_angle = 2 * math.pi / 3

                    # if 4 or 5 powerups, give powerups more space
                    if len(self.powerup_arr) > 3:
                        start_angle = math.pi / 4
                        end_angle = 3 * math.pi / 4


                    # angular spacing between powerups
                    angle_increment = (end_angle - start_angle) / (len(self.powerup_arr) - 1)

                    # calculate all positions using polar coordinates
                    for i in range(len(self.powerup_arr)):
                        angle = start_angle + i * angle_increment
                        x = arc_r * math.cos(angle)
                        y = arc_r * math.sin(angle)
                        powerup_positions.append([x, y])

                # triangles and squares have their powerups in a line beneath them
                if self.type == 'square' or self.type == 'triangle':
                    num_powerups = len(self.powerup_arr)
                    spacing = self.current_shape_image.get_size()[0] / (num_powerups + 1 / 5)
                    start_x = -((num_powerups - 1) / 2) * (spacing)
                    end_x = ((num_powerups - 1) / 2) * spacing
                    increment = (end_x - start_x) / (num_powerups - 1)

                    for i in range(num_powerups):
                        x = start_x + (i * increment)
                        powerup_positions.append((x, distance_to_center))

            # refresh the powerups surface
            self.powerups_surface = pygame.Surface((self.necessary_surface_size, self.necessary_surface_size), pygame.SRCALPHA, 32)

            # draw all the powerups to the surface
            for i in range(len(self.powerup_arr)):
                # pull corresponding powerup image from collection
                powerup_img = self.hud_images[self.powerup_data[self.powerup_arr[i]][1]]

                # draw the powerup centered on the proper coordinates
                self.powerups_surface.blit(powerup_img, [self.powerups_surface.get_size()[0]/2 + powerup_positions[i][0] - powerup_img.get_size()[0]/2, self.powerups_surface.get_size()[1]/2 + powerup_positions[i][1] - powerup_img.get_size()[1]/2])

        if "healthbar" in self.shape_sections_to_render or "all" in self.shape_sections_to_render:
            healthbar_img_copy = self.healthbar_imgs_full[self.current_healthbar_image_id].convert_alpha()
            self.healthbar_img = pygame.transform.smoothscale(healthbar_img_copy, (2 * int(healthbar_scale_up * self.r), 2 * int(healthbar_scale_up * self.r)))
            
            
        # once all sections are rerendered, clear sections array
        self.shape_sections_to_render = []

        # refresh the main surface
        self.image = pygame.Surface((self.necessary_surface_size, self.necessary_surface_size), pygame.SRCALPHA, 32)
        self.rect = self.image.get_rect()
        self.rect.center = [self.x, self.y]

        # draw all surfaces to main surface
        self.image.blit(self.healthbar_img, [self.image.get_size()[0]/2 - self.healthbar_img.get_size()[0]/2, self.image.get_size()[1]/2 - ((healthbar_scale_up) * self.r) + (healthbar_y_translate * self.r)])
        self.image.blit(self.current_shape_image, [self.image.get_size()[0]/2 - self.r, self.image.get_size()[1]/2 - self.r])
        self.image.blit(self.powerups_surface, [0, 0])

    def move(self, reverse = False):
        """move one step forwards or backwards"""
        
        self.x += self.vx
        self.y += self.vy

        # ensure shape stays within bounds
        if self.x > self.screen_w - self.r:
            self.x = self.screen_w - self.r
            self.vx = -1 * self.vx

        if self.x < self.r:
            self.x = self.r
            self.vx = -1 * self.vx

        if self.y > self.screen_h - self.r:
            self.y = self.screen_h - self.r
            self.vy = -1 * self.vy

        if self.y < self.r:
            self.y = self.r
            self.vy = -1 * self.vy

        self.rect.center = self.collision_mask_rect.center = [self.x, self.y]
        
    def getM(self):
        return self.m
    
    def getXY(self):
        return [self.x, self.y]
    
    def getV(self):
        return [self.vx, self.vy]
    
    def setV(self, vx, vy):
        self.vx = vx
        self.vy = vy

    def collectPowerup(self, powerup: Powerup):
        """shape's handler of picking up a powerup. everything required to be done by game is done before this function is called"""
        
        # game already does this check, but to be safe
        if len(self.powerup_arr) == 5: return

        # update stats
        self.stats.collectPowerup()
        self.stats_to_render.append('powerups_collected')

        self.powerup_arr.append(powerup.name)
        self.shape_sections_to_render.append("powerups")

    def handleGrowth(self):
        if self.state == 'growing':
            # grow until target radius is reached
            if self.r < self.target_r: self.r += 1
            else:
                self.r = self.target_r
                self.state = 'holding'

            self.shape_sections_to_render.append('all')

        elif self.state == 'holding':
            # hold for the desired length of time
            if self.hold_counter < 60*10: self.hold_counter += 1
            else:
                self.hold_counter = 0
                self.state = 'shrinking'

        elif self.state == 'shrinking':
            # shrink until initial radius is reached
            if self.r > self.initial_r: self.r -= 1
            else:
                self.r = self.initial_r
                self.state = 'holding'
                
            self.shape_sections_to_render.append('all')

    def update(self):
        """update shape object"""

        # don't die until your stats are updated for the last time
        if self.is_dead:
            return

        # if random.choice([0, 1, 2, 3]) == 0: self.takeDamage(0.25)

        self.handleGrowth()

        self.renderSelf()

        self.move()
            