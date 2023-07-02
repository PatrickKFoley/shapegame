import pygame, random, math, numpy as np, sys
from pygame.locals import *

circles = [
    # color         g_id    v       m       r       hp      atk     luck
    ["orange",      0,      6,      7,      10,     100,    3,     10],
    ["blue",        1,      4,      10,     20,     110,    5,     8],
]

class Game:
    def __init__(self, c0, c1):
        self.c0 = c0
        self.c1 = c1
        self.circles = [c0, c1]

        # Preprocess images
        self.c0_images = []
        self.c1_images = []
        self.smoke_images = []
        self.explosion_images = []
        self.powerup_images_hud = []
        self.powerup_images_screen = []

        # Explosion
        for i in range(1, 8):
            image = pygame.image.load("smoke/explosion{}.png".format(i))
            # image = pygame.transform.scale(image, (int(image.get_size()[0] / 2), int(image.get_size()[1] / 2)))
            self.explosion_images.append(image)

        # Smoke
        for i in range(1, 6):
            image = pygame.image.load("smoke/smoke{}.png".format(i))
            image = pygame.transform.scale(image, (int(image.get_size()[0] / 2), int(image.get_size()[1] / 2)))
            self.smoke_images.append(image)

        # Circles
        for i in range(0, 4):
            image = pygame.image.load("circles/{}/{}.png".format(c1[0], i))
            self.c1_images.append(image)

            image = pygame.image.load("circles/{}/{}.png".format(c0[0], i))
            self.c0_images.append(image)
     
        self.powerups = [
            ["powerups/skull.png",   0],
            ["powerups/cross.png",   1],
            ["powerups/star.png",    2],
            ["powerups/muscle.png",  3],
            ["powerups/speed.png",   4],
            ["powerups/health.png",  5],
            ["powerups/bomb.png",    6],
            ["powerups/laser.png",   7]
        ]

        for powerup in self.powerups:
            image = pygame.image.load(powerup[0])
            self.powerup_images_screen.append(pygame.transform.scale(image, (40, 40)))
            self.powerup_images_hud.append(pygame.transform.scale(image, (20, 20)))

        self.images = [self.c0_images, self.c1_images]

        self.screen_w = 1920
        self.screen_h = 980
        self.fps = 60
        self.font = pygame.font.Font("freesansbold.ttf", 160)
        self.screen = pygame.display.set_mode((self.screen_w, self.screen_h + 100))
        self.clock = pygame.time.Clock()
        self.background = pygame.image.load("backgrounds/BG1.png")
        self.running = True
        self.frames = 0
        self.done = False

        # for loop for creating circles
        self.groups = []
        self.groups.append(pygame.sprite.Group()) # "ORANGE"
        self.groups.append(pygame.sprite.Group()) # "BLUE"
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
        self.laser_group = pygame.sprite.Group()

        # Clouds & explosions
        self.clouds_group = pygame.sprite.Group()
        self.explosions_group = pygame.sprite.Group()

        # Max hp of each group
        self.max_hps = [0, 0]
        self.hps = []

        members_per_team = 16
        self.total_count = members_per_team * 2
        # ----------------------
        for i in range(members_per_team):
            # self.groups[0].add(Circle(circles[0], self.id_count, self))
            # self.groups[0].add(Circle(circles[1], self.id_count, self))
            # self.groups[1].add(Circle(circles[2], self.id_count, self))
            # self.groups[1].add(Circle(circles[3], self.id_count, self))

            self.groups[0].add(Circle(c0, self.id_count, self, self.c0_images, self.powerup_images_hud))
            self.max_hps[0] += c0[5]
            self.groups[1].add(Circle(c1, self.id_count, self, self.c1_images, self.powerup_images_hud))
            self.max_hps[1] += c1[5]

            # self.groups[0].add(Circle(circles[0], self.id_count, self))
        self.hps = [self.max_hps[0], self.max_hps[1]]

    def spawnPowerup(self, location, id = -1):
        if id == -1:
            self.powerup_counter += 1
            powerup = self.powerup_counter % len(self.powerups)
            self.powerup_group.add(Powerup(self.powerups[powerup], location[0], location[1]))
        elif id >= len(self.powerups) or id < 0:
            return
        else:
            self.powerup_group.add(Powerup(self.powerups[id], location[0], location[1]))
    
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
        w = self.screen_w - 200
        h = self.screen_h - 200

        rows = 4
        cols = 8

        w_int = w/cols-1
        h_int = h/rows-1

        x = id % (self.total_count / rows)
        y = id // (self.total_count / rows)

        return [100 + (w_int * x), 100 + (h_int * y)]

    def collide(self, mem_1, mem_2):
        # check if either member has a speed, if so, remove it
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
                self.groups[g2].add(Circle(self.circles[g2], self.id_count, self, self.images[g2], self.powerup_images_hud, xy2, r2, v2, True, self.smoke_images))
            # mem_1 has a resurrection and has killed mem_2
            if res_2 == 2:
                self.groups[g1].add(Circle(self.circles[g1], self.id_count, self, self.images[g1], self.powerup_images_hud, xy1, r1, v1, True, self.smoke_images))
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

                self.groups[g].add(Circle(self.circles[g], self.id_count, self, self.images[g], self.powerup_images_hud, xy, r, v, True, self.smoke_images))
                winner.removePowerup(1)
                return 1
            # winner has killed loser
            elif loser_response == 1:     
                [x, y] = loser.getXY()
                self.clouds_group.add(Clouds(x, y, self.smoke_images))
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
            self.groups[g2].add(Circle(self.circles[g2], self.id_count, self, self.images[g2], self.powerup_images_hud, [x1, y1], r1, v1, True, self.smoke_images))
            self.groups[g1].add(Circle(self.circles[g1], self.id_count, self, self.images[g1], self.powerup_images_hud, [x2, y2], r2, v2, True, self.smoke_images))
        elif d1 and 1 in mem_2.getPowerups():
            # spawn mem_2 a new teammate at mem_1's death spot
            self.groups[g2].add(Circle(self.circles[g2], self.id_count, self, self.images[g2], self.powerup_images_hud, [x1, y1], r1, v1, True, self.smoke_images))
            mem_2.removePowerup(1)
        elif d2 and 1 in mem_1.getPowerups():
            # spawn mem_1 a new teammate at mem_1's death spot
            self.groups[g1].add(Circle(self.circles[g1], self.id_count, self, self.images[g1], self.powerup_images_hud, [x2, y2], r2, v2, True, self.smoke_images))
            mem_1.removePowerup(1)

    def check_collisions(self):
        members = []
        for group in self.groups:
            for member in group.sprites():
                members.append(member)

        self.hps = [0, 0]
        for member_1 in members:
            self.hps[member_1.getG_id()] += member_1.getHp()
            self.powerups[member_1.getG_id()].append(member_1.getPowerups())

            [m1_x, m1_y] = member_1.getXY()
            m1_r = member_1.getRad()
            for member_2 in members:
                if member_1 != member_2:
                    [m2_x, m2_y] = member_2.getXY()
                    m2_r = member_2.getRad()

                    dist = math.sqrt( (m2_x - m1_x)**2 + (m2_y - m1_y)**2 )
                    max_dist = m1_r + m2_r

                    if (dist <= max_dist):
                        self.handle_collision(member_1, member_2, member_1.getG_id() != member_2.getG_id())

            for laser in self.laser_group.sprites():
                [lx, ly] = [laser.x, laser.y]
                lr = laser.r

                dist = math.sqrt( (m1_x - lx)**2 + (m1_y - ly)**2 )
                max_dist = lr + m1_r

                if dist <= max_dist:
                    if not member_1.getId() in laser.ids_collided_with:
                        laser.ids_collided_with.append(member_1.getId())
                        if member_1.getG_id() != laser.g_id:
                            if member_1.takeDamage(25) == -1:
                                [x, y] = member_1.getXY()
                                self.clouds_group.add(Clouds(x, y, self.smoke_images))

    def draw_text(self, text, font, color, surface, x, y):
        text_obj = font.render(text, 1, color)
        text_rect = text_obj.get_rect()
        text_rect.topleft = (x - font.size(text)[0] / 2, y)
        surface.blit(text_obj, text_rect)

    def blowupBomb(self, x, y, g_id):
        # Deal damage to everyone close to this point
        self.explosions_group.add(Explosion(x, y, self.explosion_images))
        kill_counter = 0
        
        members = []
        for group in self.groups:
            for member in group.sprites():
                members.append(member)

        for member in members:
            [mx, my] = member.getXY()
            dist = math.sqrt( (mx - x)**2 + (my - y)** 2)

            if dist == 0:
                member.takeDamage(200 - dist)
            elif dist <= 200:
                if member.takeDamage(200 - dist) == -1:
                    self.clouds_group.add(Clouds(member.x, member.y, self.smoke_images))
                    kill_counter += 1

        if kill_counter >= 2:
            if g_id == 0:
                self.groups[0].add(Circle(self.c0, self.id_count, self, self.c0_images, self.powerup_images_hud, [x, y]))
            else:
                self.groups[1].add(Circle(self.c1, self.id_count, self, self.c1_images, self.powerup_images_hud, [x, y]))

    def checkLaserCollision(self):
        members = []
        for group in self.groups:
            for member in group.sprites():
                members.append(member)

        for laser in self.laser_group.sprites():
            for member in members:
                [lx, ly] = [laser.x, laser.y]
                [mx, my] = member.getXY()
                lr = laser.r
                mr = member.getRad()

                dist = math.sqrt( (mx - lx)**2 + (my - ly)**2 )
                max_dist = lr + mr

                if dist <= max_dist:
                    if not member.getId() in laser.ids_collided_with:
                        laser.ids_collided_with.append(member.getId())
                        if member.getG_id() != laser.g_id:
                            if member.takeDamage(50) == -1:
                                [x, y] = member.getXY()
                                self.clouds_group.add(Clouds(x, y, self.smoke_images))
                    
    def drawStats(self):
        if self.hps[0] <= self.max_hps[0] / 4:
            image = self.c0_images[3]
        elif self.hps[0] <= self.max_hps[0] * 2 / 4:
            image = self.c0_images[2]
        elif self.hps[0] <= self.max_hps[0] * 3 / 4:
            image = self.c0_images[1]
        else:
            image = self.c0_images[0]
        image = pygame.transform.scale(image, (75, 75))

        self.screen.blit(image, (image.get_size()[0] / 2 + 10, self.screen_h + 50 - image.get_size()[1] / 2 ))
        self.draw_text("x{}".format(len(self.groups[0])), pygame.font.Font("freesansbold.ttf", 35), "black", self.screen, image.get_size()[0] * 2, self.screen_h + 60)

        pygame.draw.rect(game.screen, "red", ((image.get_size()[0] * 2 + 10, self.screen_h + 25, self.max_hps[0] / 2.5, 5)))
        pygame.draw.rect(game.screen, "green", (image.get_size()[0] * 2 + 10, self.screen_h + 25, self.hps[0] / 2.5, 5))


        if self.hps[1] <= self.max_hps[1] / 4:
            image = self.c1_images[3]
        elif self.hps[1] <= self.max_hps[1] * 2 / 4:
            image = self.c1_images[2]
        elif self.hps[1] <= self.max_hps[1] * 3 / 4:
            image = self.c1_images[1]
        else:
            image = self.c1_images[0]
        image = pygame.transform.scale(image, (75, 75))

        offset = self.screen_w / 2 - 100
        self.screen.blit(image, (image.get_size()[0] / 2 + 10 + offset, self.screen_h + 50 - image.get_size()[1] / 2 ))
        self.draw_text("x{}".format(len(self.groups[1])), pygame.font.Font("freesansbold.ttf", 35), "black", self.screen, image.get_size()[0] * 2 + offset, self.screen_h + 60)

        pygame.draw.rect(game.screen, "red", ((image.get_size()[0] * 2 + 10 + offset, self.screen_h + 25, self.max_hps[1] / 2.5, 5)))
        pygame.draw.rect(game.screen, "green", (image.get_size()[0] * 2 + 10 + offset, self.screen_h + 25, self.hps[1] / 2.5, 5))


        for i in range(len(self.groups)):
            powerup_counter = 0
            for member in self.groups[i]:
                for powerup in member.getPowerups():
                    if i == 0:
                        image = self.powerup_images_screen[powerup]
                        game.screen.blit(image, ((image.get_size()[0] * 2 + 110) + (powerup_counter * 40) + (i * offset), self.screen_h + 40))
                        powerup_counter += 1
                    else:
                        image = self.powerup_images_screen[powerup]
                        game.screen.blit(image, ((image.get_size()[0] * 2 + 110) + (powerup_counter * 40) + (i * offset), self.screen_h + 40))
                        powerup_counter += 1

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
                        if self.total_count % 2 == 1:
                            self.groups[0].add(Circle(self.c0, self.id_count, self, self.c0_images, self.powerup_images_hud, pygame.mouse.get_pos(), 0, 0, True, self.smoke_images))
                        else:
                            self.groups[1].add(Circle(self.c1, self.id_count, self, self.c1_images, self.powerup_images_hud, pygame.mouse.get_pos(), 0, 0, True, self.smoke_images))
                        self.total_count += 1

                    if event.button == 3:
                        self.fortnite_x = 0
                        self.fortnite_x_counter = 0
                        self.fortnite_x_growing = False
                        self.fortnite_y = 0
                        self.fortnite_y_counter = 0
                        self.fortnite_y_growing = False

                # keyboard click event
                if event.type == KEYDOWN:
                    self.spawnPowerup(pygame.mouse.get_pos(), event.key - 49)

            # flip() the display to put your work on screen
            pygame.display.flip()
            self.screen.blit(self.background, (0, 0))

            # Every x seconds spawn a random powerup
            if not self.done and self.frames % (1 * self.fps) == 0:
                self.spawnPowerup((random.randint(self.fortnite_x + 10, self.screen_w - self.fortnite_x - 10), random.randint(self.fortnite_y + 10, self.screen_h - self.fortnite_y - 10)))

            # draw & update groups
            self.groups[0].draw(self.screen)
            self.groups[1].draw(self.screen)
            self.powerup_group.draw(self.screen)

            self.groups[0].update(self)
            self.laser_group.update(self)
            self.check_collisions()
            self.groups[1].update(self)

            self.clouds_group.update()
            self.explosions_group.update()

            self.powerup_group.update(self)
            self.checkPowerupCollect()
            
            self.drawStats()

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
                self.draw_text("{} Wins!".format(self.c1[0].capitalize()), self.font, "black", self.screen, self.screen_w / 2, self.screen_h / 6)

            elif len(self.groups[1].sprites()) == 0:
                self.done = True
                self.fortnite_x_growing = self.fortnite_y_growing = False
                self.draw_text("{} Wins!".format(self.c0[0].capitalize()), self.font, "black", self.screen, self.screen_w / 2, self.screen_h / 6)

            # limits FPS to 60
            self.clock.tick(self.fps)

class Circle(pygame.sprite.Sprite):
    def __init__(self, attributes, id, game, images, hud_images, XY = 0, R = 0, VEL = 0, NEW = False, smoke_images = []):
        super().__init__()
        self.g_id = attributes[1]
        self.id = id
        self.game = game
        game.id_count += 1
        self.frames = 0
        self.new = NEW
        self.alive = True
        self.luck = attributes[7]
        self.bonus_luck = 0
        self.color = attributes[0]
        self.bomb_timer = -1
        self.hud_images = hud_images
        self.smoke_images = smoke_images

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
            self.r = 30 + random.randint(0, attributes[4])
        else:
            self.r = R

        self.images = images
        self.image = self.getNextImage(0)

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

    def getNextImage(self, index):
        print(index)
        multiplier = self.getRad() / 1024
        return pygame.transform.scale(self.images[index], (int(2048 * multiplier), int(2048 * multiplier)))

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
        # if removing speed, divide attack
        if id == 4:
            self.attack /= 2
        # if removing health, gain health
        if id == 5:
            self.hp = min(self.hp + self.max_hp / 2, self.max_hp)
            self.checkImageChange()
        # if removing laser, spawn laser in same direction as circle
        if id == 7:
            self.game.laser_group.add(Laser(self.getG_id(), self.x, self.y, self.v_x, self.v_y, self.game.powerup_images_screen[7]))

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
            self.bomb_timer = 3 * self.game.fps

    def update(self, game):
        if self.bomb_timer >= 0:
            self.bomb_timer -= 1

            if self.bomb_timer == 0:
                game.blowupBomb(self.x, self.y, self.getG_id())
                self.bomb_timer = -1
                self.removePowerup(6)

        # puff of smoke animation
        self.frames += 2
        if self.frames <= 50 and self.new:
            if self.frames <= 10:
                game.screen.blit(self.smoke_images[0], (self.x - self.smoke_images[0].get_size()[0] / 2, self.y - self.smoke_images[0].get_size()[1] / 2))
            elif self.frames <= 20:
                game.screen.blit(self.smoke_images[1], (self.x - self.smoke_images[1].get_size()[0] / 2, self.y - self.smoke_images[1].get_size()[1] / 2))
            elif self.frames <= 30:
                game.screen.blit(self.smoke_images[2], (self.x - self.smoke_images[2].get_size()[0] / 2, self.y - self.smoke_images[2].get_size()[1] / 2))
            elif self.frames <= 40:
                game.screen.blit(self.smoke_images[3], (self.x - self.smoke_images[3].get_size()[0] / 2, self.y - self.smoke_images[3].get_size()[1] / 2))
            elif self.frames <= 50:
                game.screen.blit(self.smoke_images[4], (self.x - self.smoke_images[4].get_size()[0] / 2, self.y - self.smoke_images[4].get_size()[1] / 2))

        if self.dmg_counter != 0:
            self.dmg_counter -= 1
            pygame.draw.circle(game.screen, "red", (self.x - self.r, self.y - self.r + 10), 3)

        if type(self.powerups) == type(None):
            self.powerups = []

        p_counter = 0
        if self.powerups != []:
            for powerup in self.powerups:
                image = self.hud_images[powerup]
                game.screen.blit(image, (self.x - self.max_hp / 2 + p_counter * 20, self.y - self.r - 25))
                p_counter += 1

        pygame.draw.rect(game.screen, "red", (self.x - self.max_hp / 2, self.y - self.r * 1, self.max_hp, 5))
        pygame.draw.rect(game.screen, "green", (self.x - self.max_hp / 2, self.y - self.r * 1, self.hp, 5))

        self.move(game)

    def rotate(self):
        new_angle = math.degrees(math.atan2(self.v_y, self.v_x))


        difference = abs(new_angle - self.angle)

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
            self.image = self.getNextImage(3)

        elif self.hp <= self.max_hp * 2 / 4:
            self.image = self.getNextImage(2)

        elif self.hp <= self.max_hp * 3 / 4:
            self.image = self.getNextImage(1)

        else:
            self.image = self.getNextImage(0)

    def takeDamage(self, amount):
        if self.hp - amount <= 0:
            self.kill()
            return -1

        self.hp -= amount
        self.checkImageChange()
        self.dmg_counter = 144

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

        if 7 in self.powerups:
            self.removePowerup(7)
    
    def getHp(self):
        return self.hp

    def getG_id(self):
        return self.g_id
    
    def getId(self):
        return self.id

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
    def __init__(self, x, y, images):
        super().__init__()
        self.x = x
        self.y = y
        self.frames = 0
        self.images = images

    def update(self):
        # puff of smoke animation
        self.frames += 2
        if self.frames <= 50:
            if self.frames <= 10:
                game.screen.blit(self.images[0], (self.x - self.images[0].get_size()[0] / 2, self.y - self.images[0].get_size()[1] / 2))
            elif self.frames <= 20:
                game.screen.blit(self.images[1], (self.x - self.images[1].get_size()[0] / 2, self.y - self.images[1].get_size()[1] / 2))
            elif self.frames <= 30:
                game.screen.blit(self.images[0], (self.x - self.images[0].get_size()[0] / 2, self.y - self.images[0].get_size()[1] / 2))
            elif self.frames <= 40:
                game.screen.blit(self.images[1], (self.x - self.images[1].get_size()[0] / 2, self.y - self.images[1].get_size()[1] / 2))
            elif self.frames <= 50:
                game.screen.blit(self.images[4], (self.x - self.images[4].get_size()[0] / 2, self.y - self.images[4].get_size()[1] / 2))
        else:
            self.kill()

class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y, images):
        super().__init__()
        self.x = x
        self.y = y
        self.frames = 0
        self.images = images

    def update(self):
        # explosion animation
        self.frames += 2
        if self.frames <= 70:
            if self.frames <= 10:
                game.screen.blit(self.images[0], (self.x - self.images[0].get_size()[0] / 2, self.y - self.images[0].get_size()[1] / 2))
            elif self.frames <= 20:
                game.screen.blit(self.images[1], (self.x - self.images[1].get_size()[0] / 2, self.y - self.images[1].get_size()[1] / 2))
            elif self.frames <= 30:
                game.screen.blit(self.images[0], (self.x - self.images[0].get_size()[0] / 2, self.y - self.images[0].get_size()[1] / 2))
            elif self.frames <= 40:
                game.screen.blit(self.images[1], (self.x - self.images[1].get_size()[0] / 2, self.y - self.images[1].get_size()[1] / 2))
            elif self.frames <= 50:
                game.screen.blit(self.images[4], (self.x - self.images[4].get_size()[0] / 2, self.y - self.images[4].get_size()[1] / 2))
            elif self.frames <= 60:
                game.screen.blit(self.images[5], (self.x - self.images[5].get_size()[0] / 2, self.y - self.images[5].get_size()[1] / 2))
            elif self.frames <= 70:
                game.screen.blit(self.images[6], (self.x - self.images[6].get_size()[0] / 2, self.y - self.images[6].get_size()[1] / 2))
        else:
            self.kill()

class Laser(pygame.sprite.Sprite):
    def __init__(self, g_id, x, y, vx, vy, image):
        super().__init__()
        self.g_id = g_id
        self.x = x
        self.y = y
        self.vx = vx *3
        self.vy = vy *3
        self.image = image
        self.r = image.get_size()[0]/2
        self.frames = 0
        self.ids_collided_with = []

    def update(self, game):
        self.x += self.vx
        self.y += self.vy

        # ensure laser stays within bounds
        if self.x > game.screen_w - self.r - game.fortnite_x:
            self.x = game.screen_w - self.r - game.fortnite_x
            self.vx = -1 * self.vx

        if self.x < self.r + game.fortnite_x:
            self.x = self.r + game.fortnite_x
            self.vx = -1 * self.vx

        if self.y > game.screen_h - self.r - game.fortnite_y:
            self.y = game.screen_h - self.r - game.fortnite_y
            self.vy = -1 * self.vy

        if self.y < self.r + game.fortnite_y:
            self.y = self.r + game.fortnite_y
            self.vy = -1 * self.vy

        game.screen.blit(self.image, (int(self.x - self.image.get_size()[0]/2), int(self.y - self.image.get_size()[1]/2)))
        
        # game.screen.blit(self.image, self.x, self.y)

        self.frames += 1
        if self.frames >= game.fps * 5:
            self.kill()

pygame.init()

game = Game(circles[0], circles[1])
game.play_game()

pygame.quit()

