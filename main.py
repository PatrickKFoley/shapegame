import pygame, random, math, numpy as np, sys
from pygame.locals import *

orange_images = []
blue_images = []
orange_images_other = []
blue_images_other = []
smoke_images = []
explosion_images = []

for i in range(1, 8):
    image = pygame.image.load("smoke/explosion{}.png".format(i))
    # image = pygame.transform.scale(image, (int(image.get_size()[0] / 2), int(image.get_size()[1] / 2)))
    explosion_images.append(image)

for i in range(1, 6):
    image = pygame.image.load("smoke/smoke{}.png".format(i))
    image = pygame.transform.scale(image, (int(image.get_size()[0] / 2), int(image.get_size()[1] / 2)))
    smoke_images.append(image)

circles = [
    # img                g_id   v   m   r    hp    atk  luck
    # ["redcircle.png",       0,  1,  15, 75,  150,  5, 10],
    ["circles/orangecircle0.png",       0,  3,  7,  35,  100,  10,  10, "orange", orange_images, orange_images_other],
    # ["graycircle.png",      1,  4,  5,  25,  65,   15, 5],
    ["circles/bluecircle0.png",      1,  2,  10, 50,  125,  10,   8, "blue", blue_images, blue_images_other],
]

for i in range(0, 4):
    image = pygame.image.load("circles/bluecircle{}.png".format(i))
    size_multiplier = circles[1][4] / 1024
    size_multiplier_other = circles[0][4] / 1024
    blue_images.append(pygame.transform.scale(image, (int(image.get_size()[0]*size_multiplier), int(image.get_size()[1]*size_multiplier))))
    image = pygame.image.load("circles/bluecircle{}.png".format(i))
    blue_images_other.append(pygame.transform.scale(image, (int(image.get_size()[0]*size_multiplier_other), int(image.get_size()[1]*size_multiplier_other))))
    

    image = pygame.image.load("circles/orangecircle{}.png".format(i))
    size_multiplier = circles[0][4] / 1024
    size_multiplier_other = circles[1][4] / 1024
    orange_images.append(pygame.transform.scale(image, (int(image.get_size()[0]*size_multiplier), int(image.get_size()[1]*size_multiplier))))
    image = pygame.image.load("circles/orangecircle{}.png".format(i))
    orange_images_other.append(pygame.transform.scale(image, (int(image.get_size()[0]*size_multiplier_other), int(image.get_size()[1]*size_multiplier_other))))
    

powerups = [
    ["powerups/skull.png",   0],
    ["powerups/cross.png",   1],
    ["powerups/star.png",    2],
    ["powerups/muscle.png",  3],
    ["powerups/feather.png", 4],
    ["powerups/health.png",  5],
    ["powerups/bomb.png",    6]
]

class Game:
    def __init__(self):
        self.screen_w = 1920
        self.screen_h = 1080
        self.font = pygame.font.Font("freesansbold.ttf", 160)
        self.screen = pygame.display.set_mode((self.screen_w, self.screen_h))
        self.clock = pygame.time.Clock()
        self.background = pygame.image.load("backgrounds/BG1.png")
        self.running = True
        self.frames = 0
        self.done = False

        # for loop for creating circles
        self.groups = []
        self.groups.append(pygame.sprite.Group()) # "RED"
        self.groups.append(pygame.sprite.Group()) # "GRAY"
        self.id_count = 0

        # Something to take care of the "fortnite circle"
        self.fortnite_x = 0
        self.fortnite_y = 0
        self.fortnite_x_counter = 0
        self.fortnite_y_counter = 0
        self.fortnite_x_growing = False
        self.fortnite_y_growing = False

        # Powerups
        self.powerup_counter = 0
        self.powerup_group = pygame.sprite.Group()

        # Clouds & explosions
        self.clouds_group = pygame.sprite.Group()
        self.explosions_group = pygame.sprite.Group()


        self.total_count = 32
        # ----------------------
        for i in range(16):
            # self.groups[0].add(Circle(circles[0], self.id_count, self))
            # self.groups[0].add(Circle(circles[1], self.id_count, self))
            # self.groups[1].add(Circle(circles[2], self.id_count, self))
            # self.groups[1].add(Circle(circles[3], self.id_count, self))

            self.groups[0].add(Circle(circles[0], self.id_count, self))
            self.groups[1].add(Circle(circles[1], self.id_count, self))

            # self.groups[0].add(Circle(circles[0], self.id_count, self))

    def spawnPowerup(self, location, id = -1):
        if id == -1:
            self.powerup_counter += 1

            powerup = self.powerup_counter % len(powerups)
            self.powerup_group.add(Powerup(powerups[powerup], location[0], location[1]))
        else:
            self.powerup_counter += 1
            self.powerup_group.add(Powerup(powerups[id], location[0], location[1]))
    
    def checkPowerupCollect(self):
        members = []
        for group in self.groups:
            for member in group.sprites():
                members.append(member)

        for member in members:
            for powerup in self.powerup_group.sprites():
                [mx, my] = member.getXY()
                [px, py] = powerup.getXY()
                mr = member.getRad()
                pr = powerup.getRad()

                dist = math.sqrt( (px - mx)**2 + (py - my)**2 )
                max_dist = mr + pr

                if dist <= max_dist:
                    # Member has collected powerup
                    member.collectPowerup(powerup.getId())
                    powerup.kill()

    def getSafeSpawn(self, id):
        w = self.screen_w - 400
        h = self.screen_h - 400

        w_int = w/7
        h_int = h/3

        x = id % (self.total_count / 4)
        y = id // (self.total_count / 4)

        return [200 + (w_int * x), 200 + (h_int * y)]

    def collide(self, mem_1, mem_2):
        # check if either member has a feather, if so, remove it
        if 4 in mem_1.powerups: mem_1.removePowerup(4)
        if 4 in mem_2.powerups: mem_2.removePowerup(4)

        # check if both members have insta-kill
        if 0 in mem_1.powerups and 0 in mem_2.powerups:
            xy1 = mem_1.getXY()
            xy2 = mem_2.getXY()
            r1 = mem_1.getRad()
            r2 = mem_2.getRad()
            g2 = mem_1.getG_id()
            g1 = mem_2.getG_id()
            v1 = mem_1.getVel()
            v2 = mem_2.getVel()

            res_1 = mem_1.getHitBy(mem_2)
            res_2 = mem_2.getHitBy(mem_1)

            # mem_2 has a resurrection and has killed mem_1
            if res_1 == 2:
                self.groups[g2].add(Circle(circles[g2], self.id_count, self, xy2, r2, v2, True))
            # mem_1 has a resurrection and has killed mem_2
            if res_2 == 2:
                self.groups[g1].add(Circle(circles[g1], self.id_count, self, xy1, r1, v1, True))
            return 1
        
        # check if one member has an insta-kill
        elif 0 in mem_1.powerups or 0 in mem_2.powerups:
            if 0 in mem_1.powerups:
                winner = mem_1
                loser = mem_2
            else:
                winner = mem_2
                loser = mem_1

        # roll a d20+luck for who damages who
        else:
            roll_1 = random.randint(1, 20) + mem_1.luck + mem_1.bonus_luck
            roll_2 = random.randint(1, 20) + mem_2.luck + mem_2.bonus_luck

            if roll_1 > roll_2:
                winner = mem_1
                loser = mem_2
            else:
                winner = mem_2
                loser = mem_1

        loser_response = loser.getHitBy(winner)
        winner.hitEnemy(loser)
    
        if loser_response != 0:
            # winner has a resurrection and has killed loser
            if loser_response == 2:
                g = winner.getG_id()
                xy = loser.getXY()
                r = loser.getRad()
                v = loser.getVel()

                self.groups[g].add(Circle(circles[g], self.id_count, self, xy, r, v, True))
                winner.removePowerup(1)
                return 1
            # winner has killed loser
            elif loser_response == 1:     
                [x, y] = loser.getXY()
                self.clouds_group.add(Clouds(x, y))
                return 1

    def handle_collision(self, mem_1, mem_2, flag = 0):
        # Magic done by: https://www.vobarian.com/collisions/2dcollisions2.pdf

        mem_1.move(self, -1)
        mem_2.move(self, -1)

        if flag == 1:
            if self.collide(mem_1, mem_2) == 1: return

        # STEP 1

        [x2, y2] = mem_2.getXY()
        [x1, y1] = mem_1.getXY()

        norm_vec = np.array([x2 - x1, y2 - y1])

        divisor = math.sqrt(norm_vec[0]**2 + norm_vec[1]**2)
        unit_vec = np.array([norm_vec[0] / divisor, norm_vec[1] / divisor])

        unit_tan_vec = np.array([-1 * unit_vec[1], unit_vec[0]])

        # STEP 2

        v1 = np.array(mem_1.getVel())
        m1 = mem_1.getMass()

        v2 = np.array(mem_2.getVel())
        m2 = mem_2.getMass()

        # STEP 3

        v1n = np.dot(unit_vec, v1)

        v1t = np.dot(unit_tan_vec, v1)

        v2n = np.dot(unit_vec, v2)

        v2t = np.dot(unit_tan_vec, v2)

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
        mem_1.setVel(v1p[0], v1p[1])
        # mem_1.rotate(mem_1.angle)

        v2p = v2np_ + v2tp_
        mem_2.setVel(v2p[0], v2p[1])
        # mem_2.rotate(mem_2.angle)

    def check_powerups(self, mem_1, mem_2, d1 = False, d2 = False):
        [x1, y1] = mem_1.getXY()
        [x2, y2] = mem_2.getXY()
        r1 = mem_1.getRad()
        r2 = mem_2.getRad()
        g1 = mem_1.getG_id()
        g2 = mem_2.getG_id()
        v1 = mem_1.getVel()
        v2 = mem_2.getVel()

        # Check for powerup 0 (instant-kill)
        # if both have:
        if 0 in mem_1.getPowerups() and 0 in mem_2.getPowerups():
            mem_1.takeDamage(mem_1.max_hp)
            mem_2.takeDamage(mem_2.max_hp)
            d1 = d2 = True
        
        elif 0 in mem_1.getPowerups():
            mem_1.removePowerup(0)
            mem_2.takeDamage(mem_2.max_hp)
            d2 = True
        
        elif 0 in mem_2.getPowerups():
            mem_2.removePowerup(0)
            mem_1.takeDamage(mem_1.max_hp)
            d1 = True
        
        # Check for powerup 1 (resurrection)
        if d1 and 1 in mem_2.getPowerups() and d2 and 1 in mem_1.getPowerups():
            # spawn mem_2 a new teammate at mem_1's death spot and mem_1 a new teammate at mem_2's death spot
            self.groups[g2].add(Circle(circles[g2], self.id_count, self, [x1, y1], r1, v1, True))
            self.groups[g1].add(Circle(circles[g1], self.id_count, self, [x2, y2], r2, v2, True))
        elif d1 and 1 in mem_2.getPowerups():
            # spawn mem_2 a new teammate at mem_1's death spot
            self.groups[g2].add(Circle(circles[g2], self.id_count, self, [x1, y1], r1, v1, True))
            mem_2.removePowerup(1)
        elif d2 and 1 in mem_1.getPowerups():
            # spawn mem_1 a new teammate at mem_1's death spot
            self.groups[g1].add(Circle(circles[g1], self.id_count, self, [x2, y2], r2, v2, True))
            mem_1.removePowerup(1)

    def check_collisions(self):
        members = []
        for group in self.groups:
            for member in group.sprites():
                members.append(member)

        for member_1 in members:
            for member_2 in members:
                if member_1 != member_2:
                    [m1_x, m1_y] = member_1.getXY()
                    [m2_x, m2_y] = member_2.getXY()
                    m1_r = member_1.getRad()
                    m2_r = member_2.getRad()

                    dist = math.sqrt( (m2_x - m1_x)**2 + (m2_y - m1_y)**2 )
                    max_dist = m1_r + m2_r

                    if (dist <= max_dist):
                        self.handle_collision(member_1, member_2, member_1.getG_id() != member_2.getG_id())

    def draw_text(self, text, font, color, surface, x, y):
        text_obj = font.render(text, 1, color)
        text_rect = text_obj.get_rect()
        text_rect.topleft = (x - font.size(text)[0] / 2, y)
        surface.blit(text_obj, text_rect)

    def blowupBomb(self, x, y):
        # Deal damage to everyone close to this point
        self.explosions_group.add(Explosion(x, y))
        
        members = []
        for group in self.groups:
            for member in group.sprites():
                members.append(member)

        for member in members:
            [mx, my] = member.getXY()
            dist = math.sqrt( (mx - x)**2 + (my - y)** 2)

            if dist <= 200:
                member.takeDamage(200 - dist)

    def play_game(self):
        while self.running:
            self.frames += 1
            # poll for events
            for event in pygame.event.get():
                # quit event
                if event.type == pygame.QUIT:
                    self.running = False

                # button click event
                if event.type == MOUSEBUTTONDOWN:
                    if event.button == 1:
                        # if self.total_count % 2 == 1:
                            
                        #     self.groups[0].add(Circle(circles[0], self.id_count, self, pygame.mouse.get_pos()))
                        #     self.id_count += 1
                        #     self.total_count += 1
                        # else:
                        #     self.groups[1].add(Circle(circles[1], self.id_count, self, pygame.mouse.get_pos()))
                        #     self.id_count += 1
                        #     self.total_count += 1

                        self.spawnPowerup(pygame.mouse.get_pos(), 0)

                    if event.button == 3:
                        self.fortnite_x = 0
                        self.fortnite_x_counter = 0
                        self.fortnite_x_growing = False
                        self.fortnite_y = 0
                        self.fortnite_y_counter = 0
                        self.fortnite_y_growing = False
                    
                    if event.button == 2:
                        self.spawnPowerup(pygame.mouse.get_pos(), 6)

            # flip() the display to put your work on screen
            pygame.display.flip()
            self.screen.blit(self.background, (0, 0))

            # Every x seconds spawn a random powerup
            if not self.done and self.frames % (2 * 144) == 0:
                self.spawnPowerup((random.randint(self.fortnite_x + 10, self.screen_w - self.fortnite_x - 10), random.randint(self.fortnite_y + 10, self.screen_h - self.fortnite_y - 10)))

            # draw & update groups
            self.groups[0].draw(self.screen)
            self.groups[1].draw(self.screen)
            self.powerup_group.draw(self.screen)

            self.groups[0].update(self)
            self.check_collisions()
            self.groups[1].update(self)

            self.clouds_group.update()
            self.explosions_group.update()

            self.powerup_group.update(self)
            self.checkPowerupCollect()

            # Do fortnite circle things
            if not self.done and len(self.groups[0].sprites()) + len(self.groups[1].sprites()) <= 10:
                self.fortnite_x_growing = self.fortnite_y_growing = True

            if self.fortnite_x_growing:
                self.fortnite_x_counter += 1
                if self.fortnite_x_counter % 10 == 0:
                    if self.fortnite_x <= 770:
                        self.fortnite_x += 1

            if self.fortnite_y_growing:
                self.fortnite_y_counter += 1
                if self.fortnite_y_counter % 10 == 0:
                    if self.fortnite_y <= 350:
                        self.fortnite_y += 1

            pygame.draw.rect(self.screen, "black", (self.fortnite_x, self.fortnite_y, self.screen_w - self.fortnite_x * 2, self.screen_h - self.fortnite_y * 2), 2)

            if len(self.groups[0].sprites()) == 0:
                self.done = True
                self.fortnite_x_growing = self.fortnite_y_growing = False
                self.draw_text("Blue Wins!", self.font, "black", self.screen, self.screen_w / 2, self.screen_h / 6)

            elif len(self.groups[1].sprites()) == 0:
                self.done = True
                self.fortnite_x_growing = self.fortnite_y_growing = False
                self.draw_text("Orange Wins!", self.font, "black", self.screen, self.screen_w / 2, self.screen_h / 6)

            # limits FPS to 60
            self.clock.tick(144)

class Circle(pygame.sprite.Sprite):
    def __init__(self, attributes, id, game, XY = 0, R = 0, VEL = 0, NEW = False):
        super().__init__()
        self.g_id = attributes[1]
        self.id = id
        game.id_count += 1
        self.frames = 0
        self.new = NEW
        self.alive = True
        self.luck = attributes[7]
        self.bonus_luck = 0
        self.color = attributes[8]
        self.bomb_timer = -1

        if self.new:
            self.images = attributes[10]
        else:
            self.images = attributes[9]
        self.image = self.images[0]
        
        if VEL == 0:
            # Want a constant speed, but random direction to start
            speed = attributes[2]
            # Speed in x direction random, 0 - 100% max speed
            self.v_x = random.uniform(0, speed)
            # Speed in y direction determined according to the equation of a circle, where r = speed
            self.v_y = math.sqrt(speed**2 - self.v_x**2)
        else:
            [self.v_x, self.v_y] = VEL 

        #flip some coins for changing direction
        if random.randint(0, 1) == 0:
            self.v_x = self.v_x * -1

        if random.randint(0, 1) == 0:
            self.v_y = self.v_y * -1

        # self.angle = 0
        
        self.m = attributes[3]
        if R == 0:
            self.r = attributes[4]
        else:
            self.r = R


        self.hp = self.max_hp = attributes[5]
        self.attack = attributes[6]

        if XY == 0:
            # Need some sort of smart spawning so that they can't overlap 
            [self.x, self.y] = game.getSafeSpawn(id)
        else:
            [self.x, self.y] = XY


        self.rect = self.image.get_rect()

        self.rect.center = [self.x, self.y]

        # self.rotate()

        self.dmg_counter = 0

        # Powerups array
        self.powerups = []

    def getPowerups(self):
        return self.powerups
    
    def removePowerup(self, id):
        if len(self.powerups) == 1:
            self.powerups = []
        else:
            self.powerups.remove(id)

        # If removing star, subtract luck
        if id == 2:
            self.bonus_luck -= 5
        # if removing muscle, divide attack
        if id == 3:
            self.attack /= 5
        # if removing feather, divide attack
        if id == 4:
            self.attack /= 2
        # if removing health, gain health
        if id == 5:
            self.hp = min(self.hp + self.max_hp / 2, self.max_hp)
            self.checkImageChange()

    def collectPowerup(self, id):
        self.powerups.append(id)

        # check if picked up star (+5 luck)
        if id == 2:
            self.bonus_luck += 5
        # check if picked up muscle (5x damage)
        if id == 3:
            self.attack *= 5
        # check if picked up muscle (double speed + damage)
        if id == 4:
            self.attack *= 2
            self.v_x *= 2
            self.v_y *= 2
        # check if picked up bomb (explode in some time)
        if id == 6:
            self.bomb_timer = 500

    def update(self, game):
        self.move(game)

        if self.bomb_timer >= 0:
            self.bomb_timer -= 1

            if self.bomb_timer == 0:
                game.blowupBomb(self.x, self.y)
                self.bomb_timer = -1
                self.removePowerup(6)

        # puff of smoke animation
        self.frames += 1
        if self.frames <= 50 and self.new:
            if self.frames <= 10:
                game.screen.blit(smoke_images[0], (self.x - smoke_images[0].get_size()[0] / 2, self.y - smoke_images[0].get_size()[1] / 2))
            elif self.frames <= 20:
                game.screen.blit(smoke_images[1], (self.x - smoke_images[1].get_size()[0] / 2, self.y - smoke_images[1].get_size()[1] / 2))
            elif self.frames <= 30:
                game.screen.blit(smoke_images[2], (self.x - smoke_images[2].get_size()[0] / 2, self.y - smoke_images[2].get_size()[1] / 2))
            elif self.frames <= 40:
                game.screen.blit(smoke_images[3], (self.x - smoke_images[3].get_size()[0] / 2, self.y - smoke_images[3].get_size()[1] / 2))
            elif self.frames <= 50:
                game.screen.blit(smoke_images[4], (self.x - smoke_images[4].get_size()[0] / 2, self.y - smoke_images[4].get_size()[1] / 2))

        if self.dmg_counter != 0:
            self.dmg_counter -= 1
            pygame.draw.circle(game.screen, "red", (self.x - self.max_hp / 2 - 10, self.y - self.r + 3), 3)

        if type(self.powerups) == type(None):
            self.powerups = []

        p_counter = 0
        if self.powerups != []:
            for powerup in self.powerups:
                p_counter += 1

                image = pygame.transform.scale(pygame.image.load(powerups[powerup][0]), (10, 10))
                game.screen.blit(image, (self.x + self.max_hp / 2 + 5 + p_counter * 10, self.y - self.r))

        pygame.draw.rect(game.screen, "red", (self.x - self.max_hp / 2, self.y - self.r * 1, self.max_hp, 5))
        pygame.draw.rect(game.screen, "green", (self.x - self.max_hp / 2, self.y - self.r * 1, self.hp, 5))

    def rotate(self):
        new_angle = math.degrees(math.atan2(self.v_y, self.v_x))


        difference = abs(new_angle - self.angle)

        print("ROTATING {} DEGREES".format(difference))

        self.image = pygame.transform.rotate(self.image, difference)
        self.angle = new_angle

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
        self.rect.center = [self.x, self.y]

    def setVel(self, v_x, v_y):
        self.v_x = v_x
        self.v_y = v_y
        self.angle = math.degrees(math.atan2(self.v_y, self.v_x)) - 45

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
        return self.attack

    def checkImageChange(self):
        if self.hp <= self.max_hp / 4:
            self.image = self.images[3]

        elif self.hp <= self.max_hp * 2 / 4:
            self.image = self.images[2]

        elif self.hp <= self.max_hp * 3 / 4:
            self.image = self.images[1]

        else:
            self.image = self.images[0]

    def takeDamage(self, amount):
        if self.hp - amount <= 0:
            self.kill()
            return 2

        self.hp -= amount
        self.checkImageChange()

    # return something on own death
    def getHitBy(self, enemy):
        self.hp = self.hp - enemy.attack
        self.dmg_counter = 144
        
        self.checkImageChange()
        
        # Check if enemy had insta-kill
        if 0 in enemy.powerups:
            self.hp = 0
            enemy.removePowerup(0)
        
        # Check if you had a star, if so remove it
        if 2 in self.powerups: self.removePowerup(2)

        if self.hp <= 0:
            if 1 in enemy.powerups:
                self.kill()
                return 2
            else:
                self.kill()
                return 1
        else:
            return 0

    def hitEnemy(self, enemy):
        if 3 in self.powerups:
            self.removePowerup(3)

        if 5 in self.powerups:
            self.removePowerup(5)
    
    def getHp(self):
        return self.hp

    def getG_id(self):
        return self.g_id

class Powerup(pygame.sprite.Sprite):
    def __init__(self, attributes, x, y):
        super().__init__()
        self.id = attributes[1]
        self.x = x
        self.y = y
        self.frames = 0

        self.image = pygame.transform.scale(pygame.image.load(attributes[0]), (40, 40))
        self.rect = self.image.get_rect()

        # keeping pickup radius the same after increasing image dimensions 20 -> 40
        self.r = 10

        self.rect.center = [self.x, self.y]

    def getXY(self):
        return [self.x, self.y]
    
    def getRad(self):
        return self.r
    
    def getId(self):
        return self.id

    def update(self, game):
        self.frames += 1

        if self.frames >= (20 * 144) or (self.x < game.fortnite_x) or (self.x > game.screen_w - game.fortnite_x) or (self.y < game.fortnite_y) or (self.y > game.screen_h - game.fortnite_y):
            self.kill()

class Clouds(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.x = x
        self.y = y
        self.frames = 0

    def update(self):
        # puff of smoke animation
        self.frames += 1
        if self.frames <= 50:
            if self.frames <= 10:
                game.screen.blit(smoke_images[0], (self.x - smoke_images[0].get_size()[0] / 2, self.y - smoke_images[0].get_size()[1] / 2))
            elif self.frames <= 20:
                game.screen.blit(smoke_images[1], (self.x - smoke_images[1].get_size()[0] / 2, self.y - smoke_images[1].get_size()[1] / 2))
            elif self.frames <= 30:
                game.screen.blit(smoke_images[2], (self.x - smoke_images[2].get_size()[0] / 2, self.y - smoke_images[2].get_size()[1] / 2))
            elif self.frames <= 40:
                game.screen.blit(smoke_images[3], (self.x - smoke_images[3].get_size()[0] / 2, self.y - smoke_images[3].get_size()[1] / 2))
            elif self.frames <= 50:
                game.screen.blit(smoke_images[4], (self.x - smoke_images[4].get_size()[0] / 2, self.y - smoke_images[4].get_size()[1] / 2))
        else:
            self.kill()

class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.x = x
        self.y = y
        self.frames = 0

    def update(self):
        # explosion animation
        self.frames += 1
        if self.frames <= 50:
            if self.frames <= 10:
                game.screen.blit(explosion_images[0], (self.x - explosion_images[0].get_size()[0] / 2, self.y - explosion_images[0].get_size()[1] / 2))
            elif self.frames <= 20:
                game.screen.blit(explosion_images[1], (self.x - explosion_images[1].get_size()[0] / 2, self.y - explosion_images[1].get_size()[1] / 2))
            elif self.frames <= 30:
                game.screen.blit(explosion_images[2], (self.x - explosion_images[2].get_size()[0] / 2, self.y - explosion_images[2].get_size()[1] / 2))
            elif self.frames <= 40:
                game.screen.blit(explosion_images[3], (self.x - explosion_images[3].get_size()[0] / 2, self.y - explosion_images[3].get_size()[1] / 2))
            elif self.frames <= 50:
                game.screen.blit(explosion_images[4], (self.x - explosion_images[4].get_size()[0] / 2, self.y - explosion_images[4].get_size()[1] / 2))
            elif self.frames <= 60:
                game.screen.blit(explosion_images[5], (self.x - explosion_images[5].get_size()[0] / 2, self.y - explosion_images[5].get_size()[1] / 2))
            elif self.frames <= 70:
                game.screen.blit(explosion_images[6], (self.x - explosion_images[6].get_size()[0] / 2, self.y - explosion_images[6].get_size()[1] / 2))
        else:
            self.kill()

pygame.init()

game = Game()
game.play_game()

pygame.quit()

