import pygame, random, math, numpy as np
from circledata import *

SHRINK_AMOUNT = 0.025

class PowerupDisplayShape(pygame.sprite.Sprite):
    def __init__(self, shape, image_full, powerup_images_hud, xy, v_xy):
        super().__init__()

        self.shape = shape
        self.r = self.shape.radius_max
        self.m = round(shape.density * (3/4) * 3.14 * self.r**3)
        self.hp = self.max_hp = shape.health * 2
        self.luck = shape.luck
        self.bonus_luck = 0
        self.dmg_multiplier = shape.dmg_multiplier
        self.density = shape.density
        self.powerups = []

        self.on_screen = False
        self.growing = False
        self.frames_held_mushroom = 0
        self.bomb_timer = 0

        self.image = pygame.Surface((4*self.r, 4*self.r), pygame.SRCALPHA, 32)
        self.image_full =  image_full
        self.circle_image = pygame.transform.smoothscale(self.image_full, (int(2048 * self.r / 1024), int(2048 * self.r / 1024)))
        self.circle_image_rect = self.circle_image.get_rect()
        self.circle_image_rect.center = (self.image.get_size()[0] / 2, self.image.get_size()[1] / 2)

        self.x = xy[0]
        self.y = xy[1]

        self.v_x = v_xy[0]
        self.v_y = v_xy[1]

        self.powerup_images_hud = powerup_images_hud

        self.constructSurface()
        self.rect = self.image.get_rect()
        self.rect.center = [self.x, self.y]

    def constructSurface(self):
        # show powerups
        self.image = pygame.Surface((4*self.r, 4*self.r), pygame.SRCALPHA, 32)

        num_powerups = len(self.powerups)
        surface = pygame.Surface((24 * num_powerups, 20), pygame.SRCALPHA, 32)

        p_counter = 0
        if self.powerups != []:
            for powerup in self.powerups:
                image = self.powerup_images_hud[powerup]
                surface.blit(image, (24 * p_counter, 0))
                p_counter += 1

        self.image.blit(surface, (self.image.get_size()[0] / 2 - surface.get_size()[0] / 2 + 2,  4 * self.image.get_size()[1] / 4.75 - surface.get_size()[1] / 2))

        self.circle_image = pygame.transform.smoothscale(self.image_full, (int(2048 * self.r / 1024), int(2048 * self.r / 1024)))
        self.circle_image_rect = self.circle_image.get_rect()
        self.circle_image_rect.center = (self.image.get_size()[0] / 2, self.image.get_size()[1] / 2)

        self.image.blit(self.circle_image, self.circle_image_rect)

        hp_p = round(round(self.hp) / self.max_hp * 100)
        if hp_p <= 33:
            color = (255, 0, 0, 100)
        elif 34 < hp_p <= 66:
            color = (255, 255, 0, 100)
        else:
            color = (0, 255, 0, 100)

        hp_circle_r = min(self.r/2, 16)

        offset = math.sqrt((self.r + hp_circle_r)**2 / 2)

        pygame.draw.circle(self.image, color, (self.image.get_size()[0] / 2 + offset, self.image.get_size()[1] / 2 - offset), hp_circle_r)
        
        
        if hp_p == 100:
            size = int(hp_circle_r * 1.1)
        else:
            size = int(hp_circle_r * 1.4)

        text = str(hp_p)
        

        font = pygame.font.SysFont("bahnschrift", size)
        text_obj = font.render(text, 1, "black")
        text_rect = text_obj.get_rect()
        text_rect.topleft = (self.image.get_size()[0] / 2 + offset - font.size(text)[0] / 2, self.image.get_size()[1] / 2 - offset - font.size(text)[1] / 2)
        self.image.blit(text_obj, text_rect)
    
    def select(self):
        self.selected = True
        self.growing = True
        self.shrinking = False

    def deselect(self):
        self.selected = False
        self.growing = False
        self.shrinking = True

    def update(self):
        if self.bomb_timer > 0:
            self.bomb_timer -= 1

            if self.bomb_timer == 0:
                self.bomb_timer = -1
                self.removePowerup(6)

        self.move()

        if self.growing:
            if self.r < self.next_r:
                self.r += 1
                self.m = round(self.density * (3/4) * 3.14 * self.r**3)
                self.constructSurface()
                self.circle_image_rect = self.circle_image.get_rect()
                self.circle_image_rect.center = (self.image.get_size()[0] / 2, self.image.get_size()[1] / 2)
                self.rect = self.image.get_rect()
                self.rect.center = [self.x, self.y]
            elif self.r > self.next_r:
                self.r -= 1
                self.m = round(self.density * (3/4) * 3.14 * self.r**3)
                self.constructSurface()
                self.circle_image_rect = self.circle_image.get_rect()
                self.circle_image_rect.center = (self.image.get_size()[0] / 2, self.image.get_size()[1] / 2)
                self.rect = self.image.get_rect()
                self.rect.center = [self.x, self.y]
            else:
                self.growing = False

        if 9 in self.powerups:
            self.frames_held_mushroom += 1
            
            if self.frames_held_mushroom == 60 * 10:
                self.frames_held_mushroom = 0
                self.removePowerup(9)

    def move(self):
        self.x += self.v_x
        self.y += self.v_y

        if 0 < self.x - self.r < 1920 and 500 < self.y + self.r < 1080:
            self.on_screen = True

        if self.on_screen:
            if self.x + self.r > 1920:
                self.x = 1920 - self.r
                self.v_x = -1 * self.v_x

            if self.x - self.r < 0:
                self.x = 0 + self.r
                self.v_x = -1 * self.v_x
            
            if self.y + self.r > 1080:
                self.y = 1080 - self.r
                self.v_y = -1 * self.v_y

            if self.y - self.r < 500:
                self.y = 500 + self.r
                self.v_y = -1 * self.v_y

        self.rect.center = [self.x, self.y]

    def setVel(self, vel):
        self.v_x = vel[0]
        self.v_y = vel[1]

    def collectPowerup(self, id):
        self.powerups.append(id)

        # check if picked up star (+5 luck)
        if id == 2:
            self.bonus_luck += 5
        # check if picked up muscle (3x dmg_multiplier)
        if id == 3:
            self.dmg_multiplier *= 3
        # check if picked up speed (double speed + dmg_multiplier)
        if id == 4:
            self.dmg_multiplier *= 1.5
            self.v_x *= 2
            self.v_y *= 2
        # check if picked up bomb (explode in some time)
        if id == 6:
            self.bomb_timer = 3 * 60
        if id == 9:
            # start growing
            self.growing = True
            self.next_r = self.r + 50

            # heal some amount + killfeed and shit
            self.hp += 100

            # get increased damage multiplier
            self.dmg_multiplier *= 5

        self.constructSurface()

    def removePowerup(self, id):
        if id in self.powerups:
            if len(self.powerups) == 1:
                self.powerups = []
            else:
                self.powerups.remove(id)
        else:
            return
        
        # If removing star, subtract luck
        if id == 2:
            self.bonus_luck -= 5
        # if removing muscle, divide dmg_multiplier
        if id == 3:
            self.dmg_multiplier /= 3
        # if removing speed, divide dmg_multiplier
        if id == 4:
            self.dmg_multiplier /= 1.5
        # if removing health, gain health
        if id == 5:
            new_hp = min(self.hp + self.max_hp / 2, self.max_hp)
            self.hp = new_hp
        # if removing laser, spawn laser in same direction as circle
        if id == 7:
            # want to limit the speed of laser to 10
            desired_speed = 8
            current_speed = math.sqrt(self.v_x**2 + self.v_y**2)
            multiplier = desired_speed / current_speed

            # self.game.laser_group.add(Laser(self, self.getG_id(), self.x, self.y, self.v_x * multiplier, self.v_y * multiplier, self.game.powerup_images_screen[7]))
        if id == 9:
            self.growTo(self.r - 50)
            self.dmg_multiplier /= 5

        self.constructSurface()

    def takeDamage(self, amount):
        self.hp -= amount
        self.constructSurface()

        if self.hp <= 0:
            self.kill()
            return True
        else:
            return False

    def getAttack(self):
        velocity = math.sqrt(self.v_x**2 + self.v_y**2)

        if velocity == np.nan or self.dmg_multiplier == np.nan:
            velocity = 0

        # print("attacking for: {} after changes: {}".format(self.attack, self.dmg_multiplier * velocity))
        return round(self.dmg_multiplier * velocity * self.m / 100000)
    
    def growTo(self, radius):
        self.growing = True
        self.next_r = radius

    def killShape(self):
        self.kill()