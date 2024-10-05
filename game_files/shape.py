import  pygame, random, math, numpy as np
import pygame.surface
from game_files.circlestats import CircleStats
from game_files.clouds import Clouds
from game_files.laser import Laser
from game_files.powerup2 import Powerup
from createdb import User, Shape as ShapeData
from game_files.circledata import powerup_data

class Shape(pygame.sprite.Sprite):
    def __init__(self, shape_data: ShapeData, shape_id, team_id, shape_images, hud_images, healthbar_img, new = False, simulated = False):
        super().__init__()

        # attributes passed from game
        self.shape_data = shape_data
        self.shape_id = shape_id
        self.team_id = team_id
        self.shape_images = shape_images
        self.hud_images = hud_images
        self.healthbar_img_full_big = healthbar_img

        # keep a record of all possible spawn locations
        self.screen_w = 1720
        self.screen_h = 1080
        self.spawn_locations = [
            [
                (self.screen_w - 150, self.screen_h / 6),  (self.screen_w - 150, 2 * self.screen_h / 6), (self.screen_w - 150, 3 * self.screen_h / 6), (self.screen_w - 150, 4 * self.screen_h / 6), (self.screen_w - 150, 5 * self.screen_h / 6),
                (self.screen_w - 300, self.screen_h / 6),  (self.screen_w - 300, 2 * self.screen_h / 6), (self.screen_w - 300, 3 * self.screen_h / 6), (self.screen_w - 300, 4 * self.screen_h / 6), (self.screen_w - 300, 5 * self.screen_h / 6),
                (self.screen_w - 450, self.screen_h / 6),  (self.screen_w - 450, 2 * self.screen_h / 6), (self.screen_w - 450, 3 * self.screen_h / 6), (self.screen_w - 450, 4 * self.screen_h / 6), (self.screen_w - 450, 5 * self.screen_h / 6),
                (self.screen_w - 600, self.screen_h / 6),  (self.screen_w - 600, 2 * self.screen_h / 6), (self.screen_w - 600, 3 * self.screen_h / 6), (self.screen_w - 600, 4 * self.screen_h / 6), (self.screen_w - 600, 5 * self.screen_h / 6),
            ], [
                (150, self.screen_h / 6),  (150, 2 * self.screen_h / 6), (150, 3 * self.screen_h / 6), (150, 4 * self.screen_h / 6), (150, 5 * self.screen_h / 6),
                (300, self.screen_h / 6),  (300, 2 * self.screen_h / 6), (300, 3 * self.screen_h / 6), (300, 4 * self.screen_h / 6), (300, 5 * self.screen_h / 6),
                (450, self.screen_h / 6),  (450, 2 * self.screen_h / 6), (450, 3 * self.screen_h / 6), (450, 4 * self.screen_h / 6), (450, 5 * self.screen_h / 6),
                (600, self.screen_h / 6),  (600, 2 * self.screen_h / 6), (600, 3 * self.screen_h / 6), (600, 4 * self.screen_h / 6), (600, 5 * self.screen_h / 6),
            ], 
        ]

        # check if this is a resurrected shape
        if new == False:
            # if not new, generate some random values
            self.r = random.randint(shape_data.radius_min, shape_data.radius_max)
            self.vx = shape_data.velocity * (-1 ** (team_id + 1))
            # self.vy = random.randint(-1, 1)
            self.vy = 0 # FOR TESTING

            # determine how large the background surface has to be
            self.necessary_surface_size = self.r + 200
        
            # determine spawn location
            self.x = self.spawn_locations[team_id][shape_id][0]
            self.y = self.spawn_locations[team_id][shape_id][1]

            # if you aren't spawning in a full row, move vertically
            num_remainders = shape_data.team_size % 5
            if num_remainders != 0 and shape_id - 1 >= shape_data.team_size - num_remainders:
                self.y = (shape_id % 5) * self.screen_h / (num_remainders + 1)

        # do healthbar things
        # 1.28 value came from difference in radius of circles drawn on original images
        self.healthbar_max_w = 2 * int(1.28 * self.r)
        self.healthbar_max_h = int(1.28 * self.r)
        self.healthbar_img = pygame.transform.smoothscale(self.healthbar_img_full_big, [self.healthbar_max_w, self.healthbar_max_h])
        self.healthbar_img_full = pygame.transform.smoothscale(self.healthbar_img_full_big, [self.healthbar_max_w, self.healthbar_max_h])
        self.healthbar_rect = self.healthbar_img.get_rect()

        # all other necessary shape attributes
        self.hp = shape_data.health
        self.max_hp = shape_data.health
        self.current_shape_image_id = 0
        
        # store powerup data
        self.powerup_data = powerup_data
        
        # collection for powerup names
        self.powerup_arr: list[str] = []

        # construct your surface
        self.current_shape_image = pygame.transform.smoothscale(shape_images[0], (self.r*2, self.r*2))
        self.sections_to_render: list[str] = ["all"]     # used by render call, add sections to list during loop, cleared at beginning of next loop
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

    def takeDamage(self, amount):
        """reduce shapes health by amount, and check if image needs to be updated"""
        
        # take damage, die if it kills you
        self.hp -= amount
        if self.hp <= 0:
            self.kill()
            return
        
        # rerender shape's health
        self.sections_to_render.append("health")

        # check to see if shape image needs to be changed
        post_dmg_img_id = self.determineShapeImageId()
        if self.current_shape_image_id != post_dmg_img_id:
            self.current_shape_image_id = post_dmg_img_id
            self.sections_to_render.append("face")

        # rerender healthbar
        self.sections_to_render.append("healthbar")

    def renderSelf(self):
        """renders shapes image using sections_to_render attribute. only renders what is needed. valid sections are "all", "face", "powerups" """
       
        # this function is called every frame, but rerendering isn't always needed
        if self.sections_to_render == []: return   

        # draw the face in the center of the surface
        if "face" in self.sections_to_render or "all" in self.sections_to_render:
            # TODO handle changing faces
            self.current_shape_image = pygame.transform.smoothscale(self.shape_images[self.current_shape_image_id], (self.r*2, self.r*2))

        # draw all powerups to appear in an arc beneath the shape
        if "powerups" in self.sections_to_render or "all" in self.sections_to_render:
            # calculate distance all powerups should appear
            distance_to_center = self.r + 15
            powerup_positions: list[list[int]] = []

            # if only one powerup, position in the center
            if len(self.powerup_arr) == 1:
                powerup_positions = [[0, distance_to_center]]

            # if more than one powerup, calculate positions 
            else:
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

            # refresh the powerups surface
            self.powerups_surface = pygame.Surface((self.necessary_surface_size, self.necessary_surface_size), pygame.SRCALPHA, 32)

            # draw all the powerups to the surface
            for i in range(len(self.powerup_arr)):
                # pull corresponding powerup image from collection
                powerup_img = self.hud_images[self.powerup_data[self.powerup_arr[i]][1]]

                # draw the powerup centered on the proper coordinates
                self.powerups_surface.blit(powerup_img, [self.powerups_surface.get_size()[0]/2 + powerup_positions[i][0] - powerup_img.get_size()[0]/2, self.powerups_surface.get_size()[1]/2 + powerup_positions[i][1] - powerup_img.get_size()[1]/2])

        if "healthbar" in self.sections_to_render or "all" in self.sections_to_render:
            # crop the image to the proper size
            health_percent = self.hp / self.max_hp

            # map percent (0-100) to angle (270° to 180°)
            angle = math.radians(270 - (270 - 180) * health_percent)

            # calculate the 2 coordinates of the two endpoints of the arc (both share y)
            radius = self.r + 50
            x_l = radius - (radius * math.cos(angle)) *-1
            x_r = 2 * radius - x_l
            y = radius + (radius * math.sin(angle))

            # determine difference between new and max size
            new_h = max(y, int(self.healthbar_max_h * 0.5))
            new_w = x_r - x_l
            d_w = self.healthbar_max_w - new_w


            # # crop the image to the proper size
            # health_percent = self.hp / self.max_hp
            # new_h = max(int(self.healthbar_max_h * health_percent), int(self.healthbar_max_h * 0.5))
            # new_w = int(self.healthbar_max_w * (health_percent))
            # d_w = self.healthbar_max_w - new_w

            region = (int(d_w/2), 0, new_w, new_h)
            self.healthbar_img = pygame.Surface((self.healthbar_max_w, self.healthbar_max_h), pygame.SRCALPHA, 32)
            self.healthbar_img.blit(self.healthbar_img_full, (int(d_w/2), 0), region)
            self.healthbar_rect = self.healthbar_img.get_rect()


            # # position the healthbar in the middle of the shape
            self.healthbar_rect.topleft = [self.image.get_size()[0]/2 - self.healthbar_img.get_size()[0]/2, self.image.get_size()[1]/2 - self.healthbar_img.get_size()[1]]
    
        # once all sections are rerendered, clear sections array
        self.sections_to_render = []

        # refresh the main surface
        self.image = pygame.Surface((self.necessary_surface_size, self.necessary_surface_size), pygame.SRCALPHA, 32)
        # self.image.fill((255, 255, 255))
        self.rect = self.image.get_rect()
        self.rect.center = [self.x, self.y]

        # draw all surfaces to main surface
        self.image.blit(self.healthbar_img, self.healthbar_rect)
        self.image.blit(self.current_shape_image, [self.image.get_size()[0]/2 - self.r, self.image.get_size()[1]/2 - self.r])
        self.image.blit(self.powerups_surface, [0, 0])

    def move(self):
        """take a single step forward"""
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

        self.rect.center = [self.x, self.y]

    def collectPowerup(self, powerup: Powerup):
        """shape's handler of picking up a powerup. everything required to be done by game is done before this function is called"""
        # game already does this check, but to be safe
        if len(self.powerup_arr) == 5: return

        self.powerup_arr.append(powerup.name)
        self.sections_to_render.append("powerups")

    def update(self):
        """update shape object"""

        # check what sections of shape's sprite needs to be rerendered
        self.renderSelf()

        self.move()
            

