import  pygame, random, math, numpy as np
from game_files.circlestats import CircleStats
from game_files.clouds import Clouds
from game_files.laser import Laser

class Circle(pygame.sprite.Sprite):
    def __init__(self, attributes, id, images, hud_images, XY = 0, R = 0, VEL = 0, NEW = False, smoke_images = [], real = True):
        super().__init__()

        self.real = real
        self.fps = 60

        self.g_id = attributes["group_id"]
        self.id = id
        self.frames = 0
        self.new = NEW
        self.alive = True
        self.luck = attributes["luck"]
        self.bonus_luck = 0
        self.color = attributes["color"][0]
        self.bomb_timer = -1
        self.hud_images = hud_images
        self.smoke_images = smoke_images
        self.stats = CircleStats()
        self.stats_changed = False
        self.old_stats = CircleStats(True)
        self.colliding_with = []
        self.took_dmg = False
        self.powerups_changed = False
        self.hp_mode = True     # True for value, False for percent
        
        self.growth_amount = 50
        self.frames_held_mushroom = 0
        self.growing = False
        self.next_r = -1
        
        if VEL == 0:
            self.v_x = attributes["velocity"] * (-1 ** (self.g_id + 1))
            self.v_y = random.randint(-1, 1)
        else:
            [self.v_x, self.v_y] = VEL 

        self.density = attributes["density"]
        
        if R == 0:
            self.r = random.randint(attributes["radius_min"], attributes["radius_max"])
        else:
            self.r = R
        self.next_r = self.r

        self.m = round(attributes["density"] * (3/4) * 3.14 * self.r**3)


        self.hp = self.max_hp = attributes["health"]
        self.dmg_multiplier = attributes["dmg_multiplier"]


        [self.x, self.y] = XY

        # Powerups array
        self.powerups = []
        self.dmg_counter = 0

        if not self.real:
            return

        self.image = pygame.Surface((4*self.r, 4*self.r), pygame.SRCALPHA, 32)
        self.images = images
        self.circle_image = self.getNextImage(0)
        self.circle_image_rect = self.circle_image.get_rect()
        self.circle_image_rect.center = (self.image.get_size()[0] / 2, self.image.get_size()[1] / 2)

        self.constructSurface(True)
        self.rect = self.image.get_rect()
        self.rect.center = [self.x, self.y]

    def growTo(self, radius):
        self.growing = True
        self.next_r = radius

    def constructSurface(self, powerups = False):
        if not self.real: return
        
        if powerups:
            # show powerups
            self.image = pygame.Surface((4*self.r, 4*self.r), pygame.SRCALPHA, 32)

            num_powerups = len(self.powerups)
            surface = pygame.Surface((24 * num_powerups, 20), pygame.SRCALPHA, 32)

            p_counter = 0
            if self.powerups != []:
                for powerup in self.powerups:
                    image = self.hud_images[powerup]
                    surface.blit(image, (24 * p_counter, 0))
                    p_counter += 1

            self.image.blit(surface, (self.image.get_size()[0] / 2 - surface.get_size()[0] / 2 + 2,  4 * self.image.get_size()[1] / 4.75 - surface.get_size()[1] / 2))

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
        
        if self.hp_mode:
            if hp_p == 100:
                size = int(hp_circle_r * 1.1)
            else:
                size = int(hp_circle_r * 1.4)

            text = str(hp_p)
        else:
            if self.hp >= 100:
                size = int(hp_circle_r * 1.1)
            else:
                size = int(hp_circle_r * 1.4)

            text = str(round(self.hp))

        font = pygame.font.SysFont("bahnschrift", size)
        text_obj = font.render(text, 1, "black")
        text_rect = text_obj.get_rect()
        text_rect.topleft = (self.image.get_size()[0] / 2 + offset - font.size(text)[0] / 2, self.image.get_size()[1] / 2 - offset - font.size(text)[1] / 2)
        self.image.blit(text_obj, text_rect)

        hp_circle_r = min(self.r/2, 16)
        offset = math.sqrt((self.r + hp_circle_r)**2 / 2)
        pygame.draw.circle(self.image, (64, 64, 64, 100), (self.image.get_size()[0] / 2 - offset, self.image.get_size()[1] / 2 - offset), hp_circle_r)
        
        font = pygame.font.SysFont("bahnschrift", int(hp_circle_r * 1.4))
        text_obj = font.render(str(self.id), 1, "black")
        text_rect = text_obj.get_rect()
        text_rect.topleft = (self.image.get_size()[0] / 2 - offset - font.size(str(self.id))[0] / 2, self.image.get_size()[1] / 2 - offset - font.size(str(self.id))[1] / 2)
        self.image.blit(text_obj, text_rect)

    def killSelf(self):
        self.kill()

    def getNextImage(self, index):
        if not self.real:
            return None

        multiplier = self.getRad() / 1024
        return pygame.transform.scale(self.images[index], (int(2048 * multiplier), int(2048 * multiplier)))

    def getPowerups(self):
        return self.powerups
    
    def collectStar(self):
        self.bonus_luck += 5

    def removeStar(self):
        self.bonus_luck -= 5

    def collectMuscle(self):
        self.dmg_multiplier *= 3

    def removeMuscle(self):
        self.dmg_multiplier /= 3
        self.stats.useMuscle()

    def collectSpeed(self):
        self.dmg_multiplier *= 1.5
        self.v_x *= 2
        self.v_y *= 2

    def removeSpeed(self):
        self.dmg_multiplier /= 1.5
        self.stats.useSpeed()

    def removeHealth(self):
        new_hp = min(self.hp + self.max_hp / 2, self.max_hp)
        self.stats.heal(new_hp - self.hp)
        self.hp = new_hp
        self.checkImageChange()

    def collectBomb(self):
        self.bomb_timer = 3 * self.fps

    def removeBomb(self):
        self.powerups.remove(6)
        self.powerups_changed = True

    def collectMushroom(self):
        # start growing
        self.growing = True
        self.next_r = self.r + self.growth_amount

        self.stats.heal(100)
        self.hp += 100
        self.checkImageChange()

        # get increased damage multiplier
        self.dmg_multiplier *= 5

    def removeMushroom(self):
        self.growTo(self.r - self.growth_amount)
        self.dmg_multiplier /= 5
        self.powerups.remove(9)
       
    def update(self, game):
        if self.bomb_timer >= 0:
            self.bomb_timer -= 1

            if self.bomb_timer == 0:
                game.blowupBomb(self, self.x, self.y)
                self.bomb_timer = -1
                self.removeBomb()

        # puff of smoke animation
        self.frames += 2
        if self.frames <= 50 and self.new and False:
            if self.frames <= 10:
                self.image.blit(self.smoke_images[0], (self.x - self.smoke_images[0].get_size()[0] / 2, self.y - self.smoke_images[0].get_size()[1] / 2))
            elif self.frames <= 20:
                self.image.blit(self.smoke_images[1], (self.x - self.smoke_images[1].get_size()[0] / 2, self.y - self.smoke_images[1].get_size()[1] / 2))
            elif self.frames <= 30:
                self.image.blit(self.smoke_images[2], (self.x - self.smoke_images[2].get_size()[0] / 2, self.y - self.smoke_images[2].get_size()[1] / 2))
            elif self.frames <= 40:
                self.image.blit(self.smoke_images[3], (self.x - self.smoke_images[3].get_size()[0] / 2, self.y - self.smoke_images[3].get_size()[1] / 2))
            elif self.frames <= 50:
                self.image.blit(self.smoke_images[4], (self.x - self.smoke_images[4].get_size()[0] / 2, self.y - self.smoke_images[4].get_size()[1] / 2))

        if self.growing:
            if self.r < self.next_r:
                self.r += 1
                self.m = round(self.density * (3/4) * 3.14 * self.r**3)

                if self.real:
                    self.checkImageChange()
                    self.constructSurface(True)
                    self.circle_image_rect = self.circle_image.get_rect()
                    self.circle_image_rect.center = (self.image.get_size()[0] / 2, self.image.get_size()[1] / 2)
                    self.rect = self.image.get_rect()
                    self.rect.center = [self.x, self.y]
            elif self.r > self.next_r:
                self.r -= 1
                self.m = round(self.density * (3/4) * 3.14 * self.r**3)

                if self.real:
                    self.checkImageChange()
                    self.constructSurface(True)
                    self.circle_image_rect = self.circle_image.get_rect()
                    self.circle_image_rect.center = (self.image.get_size()[0] / 2, self.image.get_size()[1] / 2)
                    self.rect = self.image.get_rect()
                    self.rect.center = [self.x, self.y]
            else:
                self.growing = False

        if 9 in self.powerups:
            self.frames_held_mushroom += 1
            
            if self.frames_held_mushroom == self.fps * 10:
                self.frames_held_mushroom = 0
                self.removeMushroom()



        if type(self.powerups) == type(None):
            self.powerups = []

        # show damage indicator
        flag = False
        if self.dmg_counter > 0:
            self.dmg_counter -= 1

            if self.real:
                hp_circle_r = min(self.r/2, 16)
                offset = math.sqrt((self.r + hp_circle_r)**2 / 2)
                self.image.blit(game.blood_image_small, (self.image.get_size()[0] / 2 + self.r, self.image.get_size()[1] / 2 - game.blood_image_small.get_size()[0] - 5))

                if self.dmg_counter == 0:
                    flag = True
                    self.constructSurface(True)
        
        if self.took_dmg or flag:
            hp_p = round(round(self.hp) / self.max_hp * 100)

            if hp_p <= 33:
                color = (255, 0, 0, 100)
            elif 34 < hp_p <= 66:
                color = (255, 255, 0, 100)
            else:
                color = (0, 255, 0, 100)

            hp_circle_r = min(self.r/2, 16)

            offset = math.sqrt((self.r + hp_circle_r)**2 / 2)

            if self.real: pygame.draw.circle(self.image, color, (self.image.get_size()[0] / 2 + offset, self.image.get_size()[1] / 2 - offset), hp_circle_r)
            
            if self.hp_mode:
                if hp_p == 100:
                    size = int(hp_circle_r * 1.1)
                else:
                    size = int(hp_circle_r * 1.4)

                text = str(hp_p)
            else:
                if self.hp >= 100:
                    size = int(hp_circle_r * 1.1)
                else:
                    size = int(hp_circle_r * 1.4)

                text = str(round(self.hp))

            if self.real:

                font = pygame.font.SysFont("bahnschrift", size)
                text_obj = font.render(text, 1, "black")
                text_rect = text_obj.get_rect()
                text_rect.topleft = (self.image.get_size()[0] / 2 + offset - font.size(text)[0] / 2, self.image.get_size()[1] / 2 - offset - font.size(text)[1] / 2)
                self.image.blit(text_obj, text_rect)

            self.took_dmg = False

        if self.powerups_changed:
            self.constructSurface(True)
            self.powerups_changed = False

        self.move(game)

    def resetDmgCounter(self):
        self.dmg_counter = 0

    def move(self, game, reverse = 0):
        # move
        if (reverse == 0):
            self.x += self.v_x
            self.y += self.v_y
        else:
            self.x -= self.v_x
            self.y -= self.v_y

        # ensure circle stays within bounds
        if self.x > game.screen_w - self.r - game.fortnite_x:
            self.x = game.screen_w - self.r - game.fortnite_x
            self.v_x = -1 * self.v_x
            # self.rotate()

        if self.x < self.r + game.fortnite_x:
            self.x = self.r + game.fortnite_x
            self.v_x = -1 * self.v_x
            # self.rotate()

        if self.y > game.screen_h - self.r - game.fortnite_y:
            self.y = game.screen_h - self.r - game.fortnite_y
            self.v_y = -1 * self.v_y
            # self.rotate()

        if self.y < self.r + game.fortnite_y:
            self.y = self.r + game.fortnite_y
            self.v_y = -1 * self.v_y
            # self.rotate()

        # update position
        # self.rect = self.image.get_rect()
        if self.real:
            self.rect.center = [self.x, self.y]

    def setVel(self, v_x, v_y):
        self.v_x = v_x
        self.v_y = v_y

    def getVel(self):
        return [self.v_x, self.v_y]

    def setXY(self, x, y):
        self.x = x
        self.y = y

    def getXY(self):
        return [self.x, self.y]
    
    def getRad(self):
        return self.r
    
    def getMass(self):
        return self.m
    
    def getAttack(self):
        velocity = math.sqrt(self.getVel()[0]**2 + self.getVel()[1]**2)

        if velocity == np.nan:
            velocity = 0

        # print("attacking for: {} after changes: {}".format(self.attack, self.dmg_multiplier * velocity))
        return round(self.dmg_multiplier * velocity * self.m / 100000)

    def checkImageChange(self):
        if not self.real: return

        if self.hp <= self.max_hp / 4:
            self.circle_image = self.getNextImage(3)
            # self.circle_image_rect = self.circle_image.get_rect()
            # self.circle_image_rect.center = (self.image.get_size()[0] / 2, self.image.get_size()[1] / 2)
            self.constructSurface()

        elif self.hp <= self.max_hp * 2 / 4:
            self.circle_image = self.getNextImage(2)
            # self.circle_image_rect = self.circle_image.get_rect()
            # self.circle_image_rect.center = (self.image.get_size()[0] / 2, self.image.get_size()[1] / 2)
            self.constructSurface()

        elif self.hp <= self.max_hp * 3 / 4:
            self.circle_image = self.getNextImage(1)
            # self.circle_image_rect = self.circle_image.get_rect()
            # self.circle_image_rect.center = (self.image.get_size()[0] / 2, self.image.get_size()[1] / 2)
            self.constructSurface()

        else:
            self.circle_image = self.getNextImage(0)
            # self.circle_image_rect = self.circle_image.get_rect()
            # self.circle_image_rect.center = (self.image.get_size()[0] / 2, self.image.get_size()[1] / 2)
            self.constructSurface()
        
    def dealDamage(self, amount):
        self.stats.dealDamage(amount)

    def takeDamage(self, amount):
        self.hp -= amount

        self.stats.receiveDamage(amount)
        self.took_dmg = True
        self.checkImageChange()
        self.dmg_counter = 144

    def checkStatsChange(self):
        if self.stats.report() != self.old_stats.report():
            self.stats_changed = True
        else:
            self.stats_changed = False
    
    def getHp(self):
        return self.hp

    def getG_id(self):
        return self.g_id
    
    def getId(self):
        return self.id
