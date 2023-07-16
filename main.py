import pygame, random, math, numpy as np, os, copy
from pygame.locals import *

colors = [
    # REGULAR LIGHT DARK
    # ["red", (255, 0, 0), (255, 102, 102), (102, 0, 0)],
    # ["orange", (255, 128, 0), (255, 178, 102), (153, 76, 0)],
    # ["yellow", (255, 255, 0), (255, 255, 102), (153, 153, 0)],
    # ["green", (0, 204, 0), (51, 255, 51), (0, 153, 0)],
    # ["blue", (0, 0, 204), (51, 51, 255), (0, 0, 102)],
    # ["purple", (102, 0, 204), (153, 51, 255), (51, 0, 102)],
    # ["pink", (255, 0, 127), (255, 102, 178), (153, 0, 76)],
    # ["gray", (96, 96, 96), (160, 160, 160), (64, 64, 64)],
    # SPECIAL COLORS - TAKE CARE
    ["rainbow", "gradient1.png", (255, 180, 180)],
    ["grayscale", "gradient2.png", (100, 100, 100)],
    ["rose", "gradient3.png", (255, 51, 153)],
    ["lavender", "gradient4.png", (153, 153, 255)],
    ["mint", "gradient5.png", (0, 255, 128)],
]

one = random.randint(0, len(colors)-1)
two = random.randint(0, len(colors)-1)

while one == two:
    two = random.randint(0, len(colors)-2)

circles = [
    {
        "color": colors[one],
        "face_id": 1,
        "group_id": 0,
        "density": 10,
        "velocity": 3,
        "mass": 10,
        "radius_min": 0,
        "radius_max": 15,
        "health": 110,
        "dmg_multiplier": 1.5,
        "attack": 5,
        "luck": 8,
    },
    {
        "color": colors[two],
        "face_id": 1,
        "group_id": 1,
        "density": 10,
        "velocity": 4,
        "mass": 15,
        "radius_min": 10,
        "radius_max": 25,
        "health": 170,
        "dmg_multiplier": 1,
        "attack": 2,
        "luck": 10,
    },
]

class Game: 
    def __init__(self, c0, c1, seed = False):
        if seed != False:
            random.seed(seed)
        
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
        if os.path.isdir("circles/{}/{}".format(circles[1]["face_id"], circles[1]["color"][0])):
            for i in range(0, 4):
                self.c1_images.append(pygame.image.load("circles/{}/{}/{}.png".format(circles[1]["face_id"], circles[1]["color"][0], i)))
        else:
            print("\nJust a moment! New circles being drawn!")
            os.mkdir("circles/{}/{}".format(circles[1]["face_id"], circles[1]["color"][0]))
            for n in range(0, 4):
                path = "circles/{}/{}.png".format(circles[1]["face_id"], n)
                image = pygame.image.load(path)

                # loop through image, replace green pixels
                for j in range(0, image.get_size()[0]):
                    for k in range(0, image.get_size()[1]):
                        pixel = image.get_at((j, k))
                        if pixel[0] <= 100 and pixel[1] >= 150 and pixel[2] <= 100:
                            image.set_at((j, k), circles[1]["color"][1])
                        elif pixel[0] <= 100 and 100 <= pixel[1] <= 150 and pixel[2] <= 100:
                            image.set_at((j, k), circles[1]["color"][3])
                        elif 100 <= pixel[0] <= 150 and pixel[1] >= 200 and 100 <= pixel[2] <= 150:
                            image.set_at((j, k), circles[1]["color"][2])

                pygame.image.save(image, "circles/{}/{}/{}.png".format(circles[1]["face_id"], circles[1]["color"][0], n))
                self.c1_images.append(image)

        if os.path.isdir("circles/{}/{}".format(circles[0]["face_id"], circles[0]["color"][0])):
            for i in range(0, 4):
                self.c0_images.append(pygame.image.load("circles/{}/{}/{}.png".format(circles[0]["face_id"], circles[0]["color"][0], i)))
        else:
            print("\nJust a moment! New circles being drawn!")
            os.mkdir("circles/{}/{}".format(circles[0]["face_id"], circles[0]["color"][0]))
            for n in range(0, 4):
                path = "circles/{}/{}.png".format(circles[0]["face_id"], n)
                image = pygame.image.load(path)

                for j in range(0, image.get_size()[0]):
                    for k in range(0, image.get_size()[1]):
                        pixel = image.get_at((j, k))
                        if pixel[0] <= 100 and pixel[1] >= 150 and pixel[2] <= 100:
                            image.set_at((j, k), circles[0]["color"][1])
                        elif pixel[0] <= 100 and 100 <= pixel[1] <= 150 and pixel[2] <= 100:
                            image.set_at((j, k), circles[0]["color"][3])
                        elif 100 <= pixel[0] <= 150 and pixel[1] >= 200 and 100 <= pixel[2] <= 150:
                            image.set_at((j, k), circles[0]["color"][2])

                pygame.image.save(image, "circles/{}/{}/{}.png".format(circles[0]["face_id"], circles[0]["color"][0], n))
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

        self.coffin_img = pygame.transform.scale(pygame.image.load("powerups/coffin.png"), (40, 40))

        for powerup in self.powerups:
            image = pygame.image.load(powerup[0])
            self.powerup_images_screen.append(pygame.transform.scale(image, (40, 40)))
            self.powerup_images_hud.append(pygame.transform.scale(image, (20, 20)))

        self.blood_image = pygame.transform.scale(pygame.image.load("powerups/blood.png"), (40, 40))
        self.sword_image = pygame.transform.scale(pygame.image.load("powerups/sword.png"), (40, 40))
        self.blood_image_small = pygame.transform.scale(pygame.image.load("powerups/blood.png"), (30, 30))

        self.images = [self.c0_images, self.c1_images]

        # Sounds
        self.death_sounds = []
        self.death_sounds.append(pygame.mixer.Sound("sounds/death/1.wav"))
        self.death_sounds.append(pygame.mixer.Sound("sounds/death/2.wav"))
        self.death_sounds.append(pygame.mixer.Sound("sounds/death/3.wav"))
        self.death_sounds.append(pygame.mixer.Sound("sounds/death/4.wav"))

        self.collision_sounds = []
        self.collision_sounds.append(pygame.mixer.Sound("sounds/collisions/clink1.wav"))
        self.collision_sounds.append(pygame.mixer.Sound("sounds/collisions/clink2.wav"))
        # self.collision_sounds.append(pygame.mixer.Sound("sounds/collisions/clink3.wav"))
        # self.collision_sounds.append(pygame.mixer.Sound("sounds/collisions/bing1.wav"))
        # self.collision_sounds.append(pygame.mixer.Sound("sounds/collisions/thud1.wav"))
        self.collision_sounds.append(pygame.mixer.Sound("sounds/collisions/thud2.wav"))

        self.choir_sound = pygame.mixer.Sound("sounds/choir.wav")
        self.explosion_sound = pygame.mixer.Sound("sounds/explosion.flac")
        self.fuse_sound = pygame.mixer.Sound("sounds/fuse.wav")
        self.heal_sound = pygame.mixer.Sound("sounds/heal.wav")
        self.laser_hit_sound = pygame.mixer.Sound("sounds/laser_hit.wav")
        self.laser_sound = pygame.mixer.Sound("sounds/laser.wav")
        self.pop_sound = pygame.mixer.Sound("sounds/pop.wav")
        self.pop_sound = pygame.mixer.Sound("sounds/pop.wav")
        self.punch_sound = pygame.mixer.Sound("sounds/punch.wav")
        self.shotgun_sound = pygame.mixer.Sound("sounds/shotgun.wav")
        self.twinkle_sound = pygame.mixer.Sound("sounds/twinkle.wav")
        self.win_sound = pygame.mixer.Sound("sounds/win.wav")
        self.wind_sound = pygame.mixer.Sound("sounds/wind.wav")

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

        self.screen_w = 1720
        self.screen_h = 1070
        self.fps = 60
        self.font = pygame.font.Font("freesansbold.ttf", 160)
        self.screen = pygame.display.set_mode((self.screen_w + 200, self.screen_h))
        self.clock = pygame.time.Clock()
        self.background = pygame.image.load("backgrounds/BG1.png")
        self.running = True
        self.frames = 0
        self.done = False
        self.frames_done = 0
        self.play_sound = True
        self.spawned_counter = 0
        self.mode = "GAME"
        self.stats_screen = False
        self.dead_circle = True
        self.hp_mode = False

        # for loop for creating circles
        self.groups = []
        self.groups.append(pygame.sprite.Group()) # "ORANGE"
        self.groups.append(pygame.sprite.Group()) # "BLUE"
        self.id_count = [1, 1]
        self.spawn_count = 0

        self.dead_stats = [[], []]
        self.stats = [[], []]

        # Something to take care of the "fortnite circle"
        self.fortnite_x = 0
        self.fortnite_y = 0
        self.fortnite_x_counter = 0
        self.fortnite_y_counter = 0
        self.fortnite_x_growing = False
        self.fortnite_y_growing = False

        # Powerups
        self.powerup_group = pygame.sprite.Group()
        self.laser_group = pygame.sprite.Group()

        # Clouds & explosions
        self.clouds_group = pygame.sprite.Group()
        self.explosions_group = pygame.sprite.Group()

        # Killfeed
        self.killfeed_group = pygame.sprite.Group()

        # Max hp of each group
        self.max_hps = [0, 0]
        self.hps = []

        self.members_per_team = 5
        self.max_hps[0] += circles[0]["health"] * self.members_per_team
        self.max_hps[1] += circles[1]["health"] * self.members_per_team
        self.hps = [self.max_hps[0], self.max_hps[1]]

        self.total_count = self.members_per_team * 2
        # ----------------------
        for i in range(self.members_per_team):
            self.addCircle(0)
            self.addCircle(1)

        self.createStatsScreen(True)

    def spawnPowerup(self, id = -1, location = False):
        if location == False:
            location = (random.randint(self.fortnite_x + 10, self.screen_w - self.fortnite_x - 10), random.randint(self.fortnite_y + 10, self.screen_h - self.fortnite_y - 10))

        if id == -1:
            powerup = random.randint(0, len(self.powerups) - 1)
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
                    self.pop_sound.play()
                    member.collectPowerup(powerup.getId())

                    if powerup.getId() == 6:
                        self.fuse_sound.play(10)
                    elif powerup.getId() == 4:
                        self.wind_sound.play()
                        pygame.mixer.Sound.fadeout(self.wind_sound, 1500)
                    elif powerup.getId() == 2:
                        self.twinkle_sound.play()
                    
                    powerup.kill()

    def getSafeSpawn(self):
        w = self.screen_w
        h = self.screen_h

        rows = 4
        cols = 8

        w_int = w/cols
        h_int = h/rows

        x = self.spawn_count % (self.total_count / rows)
        y = self.spawn_count // (self.total_count / rows)

        self.spawn_count += 1
        return [100 + (w_int * x), 100 + (h_int * y)]

    def collide_v2(self, mem_1, mem_2):
        self.collision_sounds[random.randint(0, len(self.collision_sounds)-1)].play()

        if 0 in mem_1.powerups or 0 in mem_2.powerups:
            if 0 in mem_1.powerups: self.memberHitMember(mem_1, mem_2)
            if 0 in mem_2.powerups: self.memberHitMember(mem_2, mem_1)
            return 1

        else:
            roll_1 = random.randint(1, 20) + mem_1.luck + mem_1.bonus_luck
            roll_2 = random.randint(1, 20) + mem_2.luck + mem_2.bonus_luck

            if roll_1 > roll_2:
                return self.memberHitMember(mem_1, mem_2)
            else:
                return self.memberHitMember(mem_2, mem_1)
                
    def memberHitMember(self, winner, loser):
        loser_copy = loser
        loser_resurrect = False

        # Handle if winner has insta kill
        if 0 in winner.powerups:
            # Check if loser had resurrect, if so, they get to res a teammate
            loser_resurrect = self.memberInstaKillMember(winner, loser)

            if 1 in winner.powerups and not loser_resurrect:
                self.memberResurrectMember(winner, loser)
            return
        
        # Collide like normal
        dmg_amount = winner.getAttack()

        loser.takeDamage(dmg_amount)
        winner.dealDamage(dmg_amount)

        if loser.hp <= 0:
            # default action (coffin) for killfeed)
            action = -1

            # Determine if any powerups were used for killfeed
            if 3 in winner.powerups:
                action = 3
            if 4 in winner.powerups:
                action = 4

            loser_resurrect = self.memberKillMember(winner, loser, action)

            # determine if winner can use resurrect if they have it
            if 1 in winner.powerups and not loser_resurrect:
                self.memberResurrectMember(winner, loser)

        # Determine if any powerups were used for stats
        if 2 in winner.powerups:
            winner.stats.useStar()
        if 3 in winner.powerups:
            winner.stats.useMuscle()
        if 4 in winner.powerups:
            winner.stats.useSpeed()

        # Clear winner of any powerups they should lose
        if 2 in winner.powerups:
            winner.removePowerup(2)
        if 3 in winner.powerups:
            winner.removePowerup(3)
        if 4 in winner.powerups:
            winner.removePowerup(4)

        if loser.hp <= 0:
            return 1
        else:
            return 0
        
    def memberKillMember(self, winner, loser, action = -1):
        loser_resurrect = False

        # Create killfeed, play sound
        self.addKillfeed(winner, loser, action)
        self.death_sounds[len(self.death_sounds)-1].play()

        # check if dead loser has resurrect
        if 1 in loser.powerups:
            self.memberResurrectMember(loser)
            loser_resurrect = True

        # remove powerup % update stats, kill circle
        winner.stats.killPlayer(loser.id)
        loser.killCircle()

        return loser_resurrect

    def memberInstaKillMember(self, winner, loser):
        loser_resurrect = False

        # Create killfeed, play sound
        self.addKillfeed(winner, loser, 0)
        self.shotgun_sound.play()

        # check if dead loser has resurrect
        if 1 in loser.powerups:
            self.memberResurrectMember(loser)
            loser_resurrect = True

        # remove powerup % update stats, kill circle
        winner.removePowerup(0)
        winner.stats.useInstakill()
        winner.stats.dealDamage(loser.hp)
        winner.stats.killPlayer(loser.id)
        loser.killCircle()

        return loser_resurrect

    def memberResurrectMember(self, god, dead_circle = False):
        # determine if new circle is modeled after god or dead circle
        if dead_circle == False:
            new_circle_before = god
        else:
            new_circle_before = dead_circle

        # create circle
        new_circle = self.addCircle(god.g_id, new_circle_before.getXY(), new_circle_before.r, new_circle_before.getVel(), True)

        # killfeed and stats
        self.addKillfeed(god, new_circle, 1)
        god.stats.resurrectPlayer()

        # sounds
        self.choir_sound.play()
        pygame.mixer.Sound.fadeout(self.choir_sound, 1000)

        # remove powerup
        god.removePowerup(1)

    def collide(self, mem_1, mem_2):
        self.collision_sounds[random.randint(0, len(self.collision_sounds)-1)].play()

        # check if either member has a speed, if so, remove it
        # if 4 in mem_1.powerups: mem_1.removePowerup(4)
        # if 4 in mem_2.powerups: mem_2.removePowerup(4)

        # check if both members have insta-kill
        if 0 in mem_1.powerups and 0 in mem_2.powerups:
            self.addKillfeed(mem_1, mem_2, 0)
            self.addKillfeed(mem_2, mem_1, 0)
            mem_1.stats.useInstakill()
            mem_2.stats.useInstakill()

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

            self.shotgun_sound.play()

            # mem_2 has a resurrection and has killed mem_1
            if res_1 == 2:
                new_circle = self.addCircle(g2, xy2, r2, v2, True)
                self.addKillfeed(mem_2, new_circle, 1)
                mem_2.stats.resurrectPlayer()
                self.choir_sound.play()
                pygame.mixer.Sound.fadeout(self.choir_sound, 1000)
            # mem_1 has a resurrection and has killed mem_2
            if res_2 == 2:
                new_circle = self.addCircle(g1, xy1, r1, v1, True)
                self.addKillfeed(mem_1, new_circle, 1)
                mem_1.stats.resurrectPlayer()
                self.choir_sound.play()
                pygame.mixer.Sound.fadeout(self.choir_sound, 1000)
            return 1
        
        # check if one member has an insta-kill
        elif 0 in mem_1.powerups or 0 in mem_2.powerups:
            if 0 in mem_1.powerups:
                winner = mem_1
                loser = mem_2
            else:
                winner = mem_2
                loser = mem_1   
            winner.stats.useInstakill()  


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
        
        # check for any powerups to update stats
        # winner has star
        if 2 in winner.powerups:
            # self.addKillfeed(winner, loser, 2)
            winner.stats.useStar()
        # winner has muscle
        if 3 in winner.powerups:
            winner.stats.useMuscle()
        # winner has speed
        if 4 in winner.powerups:
            winner.stats.useSpeed()

        loser_response = loser.getHitBy(winner)
        winner.hitEnemy(loser)
    
        if loser_response != [0]:
            # winner has a resurrection and has killed loser
            if 2 in loser_response:
                g = winner.getG_id()
                xy = loser.getXY()
                r = loser.getRad()
                v = loser.getVel()

                new_circle = self.addCircle(g, xy, r, v, True)
                winner.stats.resurrectPlayer()
                # self.groups[g].add(new_circle)
                self.addKillfeed(winner, new_circle, 1)
                self.choir_sound.play()
                pygame.mixer.Sound.fadeout(self.choir_sound, 1000)
                winner.removePowerup(1)
                if 0 in winner.powerups: winner.removePowerup(0)
                return 1
            # winner has killed loser with insta kill
            elif 6 in loser_response:     
                [x, y] = loser.getXY()
                if self.mode == "GAME":
                    self.clouds_group.add(Clouds(x, y, self.smoke_images, self.screen))
                winner.stats.killPlayer(loser.id)
                self.death_sounds[random.randint(0, len(self.death_sounds)-1)].play()
                self.shotgun_sound.play()   
                self.addKillfeed(winner, loser, 0)
                return 1
            # winner has killed loser with muscle
            elif 3 in loser_response:     
                [x, y] = loser.getXY()
                if self.mode == "GAME":
                    self.clouds_group.add(Clouds(x, y, self.smoke_images, self.screen))
                winner.stats.killPlayer(loser.id)
                self.death_sounds[random.randint(0, len(self.death_sounds)-1)].play()
                self.addKillfeed(winner, loser, 3)
                return 1
            # winner has killed loser with speed
            elif 5 in loser_response:
                [x, y] = loser.getXY()
                if self.mode == "GAME":
                    self.clouds_group.add(Clouds(x, y, self.smoke_images, self.screen))
                winner.stats.killPlayer(loser.id)
                self.death_sounds[random.randint(0, len(self.death_sounds)-1)].play()
                self.addKillfeed(winner, loser, 4)
                return 1
            # winner has killed loser
            elif 1 in loser_response:     
                [x, y] = loser.getXY()
                if self.mode == "GAME":
                    self.clouds_group.add(Clouds(x, y, self.smoke_images, self.screen))
                winner.stats.killPlayer(loser.id)
                self.death_sounds[random.randint(0, len(self.death_sounds)-1)].play()
                self.addKillfeed(winner, loser, -1)
                return 1
            
    def handle_collision(self, mem_1, mem_2, flag = 0):
        # Magic done by: https://www.vobarian.com/collisions/2dcollisions2.pdf

        mem_1.move(self, -1)
        mem_2.move(self, -1)

        if flag == 1:
            if self.collide_v2(mem_1, mem_2) == 1: return

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
                        if member_2.getId() in member_1.colliding_with or member_1.getId() in member_2.colliding_with:
                            pass
                        else:
                            self.handle_collision(member_1, member_2, member_1.getG_id() != member_2.getG_id())
                    else:
                        if member_2.getId() in member_1.colliding_with:
                            member_1.colliding_with.remove(member_2.getId())
                        if member_1.getId() in member_2.colliding_with:
                            member_2.colliding_with.remove(member_1.getId())

            for laser in self.laser_group.sprites():
                [lx, ly] = [laser.x, laser.y]
                lr = laser.r

                dist = math.sqrt( (m1_x - lx)**2 + (m1_y - ly)**2 )
                max_dist = lr + m1_r

                if dist <= max_dist:
                    if not member_1.getId() in laser.ids_collided_with:
                        laser.ids_collided_with.append(member_1.getId())
                        if member_1.getG_id() != laser.g_id:
                            self.laser_hit_sound.play()
                            laser_damage = 25
                            laser.circle.stats.laserHit()
                            laser.circle.stats.dealDamage(laser_damage)
                            if member_1.takeDamage(laser_damage) == -1:
                                [x, y] = member_1.getXY()
                                if self.mode == "GAME":
                                    self.clouds_group.add(Clouds(x, y, self.smoke_images, self.screen))
                                laser.circle.stats.killPlayer(member_1.id)
                                self.death_sounds[random.randint(0, len(self.death_sounds)-1)].play()
                                self.addKillfeed(laser.circle, member_1, 7)
                                
    def draw_text(self, text, font, color, x, y, center = True, screen = False):
        text_obj = font.render(text, 1, color)
        text_rect = text_obj.get_rect()
        if center:
            text_rect.topleft = (x - font.size(text)[0] / 2, y)
        else:
            text_rect.topleft = (x, y)

        if not screen:
            self.screen.blit(text_obj, text_rect)
        else:
            screen.blit(text_obj, text_rect)

    def blowupBomb(self, circle, x, y, g_id):
        self.fuse_sound.stop()

        # Deal damage to everyone close to this point
        if self.mode == "GAME":
            self.explosions_group.add(Explosion(x, y, self.explosion_images, self.screen))
        self.explosion_sound.play()
        circle.stats.useBomb()
        kill_counter = 0
        
        members = []
        for group in self.groups:
            for member in group.sprites():
                members.append(member)

        for member in members:
            [mx, my] = member.getXY()
            dist = math.sqrt( (mx - x)**2 + (my - y)** 2)

            if dist <= 200:
                member.takeDamage(200 - dist)

            if member.hp <= 0:
                self.bombKillMember(circle, member)
                kill_counter += 1

        if kill_counter >= 2 and 1 not in circle.powerups:
            self.memberResurrectMember(circle)

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
                                if self.mode == "GAME":
                                    self.clouds_group.add(Clouds(x, y, self.smoke_images, self.screen))
                                laser.circle.stats.killPlayer(member.id)
                                self.death_sounds[random.randint(0, len(self.death_sounds-1))].play()

    def bombKillMember(self, bomb_holder, killed):
        self.clouds_group.add(Clouds(killed.x, killed.y, self.smoke_images, self.screen))
        bomb_holder.stats.killPlayer(killed.id)

        self.death_sounds[random.randint(0, len(self.death_sounds)-1)].play()
        self.addKillfeed(bomb_holder, killed, 6)

        killed.killCircle()

        if 1 in killed.powerups:
            self.memberResurrectMember(killed)

    def drawStats(self):
        if self.hps[0] <= self.max_hps[0] / 4:
            image = self.images[0][3]
        elif self.hps[0] <= self.max_hps[0] * 2 / 4:
            image = self.images[0][2]
        elif self.hps[0] <= self.max_hps[0] * 3 / 4:
            image = self.images[0][1]
        else:
            image = self.images[0][0]
        image = pygame.transform.scale(image, (85, 85))

        self.screen.blit(image, (self.screen_w + 10, 10))
        self.draw_text("x{}".format(len(self.groups[0])), pygame.font.Font("freesansbold.ttf", 25), "black", self.screen_w + 52, 105)
        self.draw_text("{}%".format(round((self.hps[0] / self.max_hps[0]) * 100, 1)), pygame.font.Font("freesansbold.ttf", 25), "black", self.screen_w + 60, 130)

        # pygame.draw.rect(self.screen, "red", ((image.get_size()[0] * 2 + 10, self.screen_h + 25, self.max_hps[0] / 2.5, 5)))
        # pygame.draw.rect(self.screen, "green", (image.get_size()[0] * 2 + 10, self.screen_h + 25, self.hps[0] / 2.5, 5))


        if self.hps[1] <= self.max_hps[1] / 4:
            image = self.images[1][3]
        elif self.hps[1] <= self.max_hps[1] * 2 / 4:
            image = self.images[1][2]
        elif self.hps[1] <= self.max_hps[1] * 3 / 4:
            image = self.images[1][1]
        else:
            image = self.images[1][0]
        image = pygame.transform.scale(image, (85, 85))

        offset = self.screen_w / 2 - 100
        self.screen.blit(image, (self.screen_w + 105, 10))
        self.draw_text("x{}".format(len(self.groups[1])), pygame.font.Font("freesansbold.ttf", 25), "black", self.screen_w + 147, 105)
        self.draw_text("{}%".format(round((self.hps[1] / self.max_hps[1]) * 100, 1)), pygame.font.Font("freesansbold.ttf", 25), "black", self.screen_w + 155, 130)

    def addKillfeed(self, right_circle, left_circle, action_id):
        if len(self.killfeed_group) == 12:
            self.killfeed_group.update(True)

        if action_id == -1:
            image = self.coffin_img
        else:
            image = self.powerup_images_screen[action_id]

        new = Killfeed(right_circle, left_circle, image, self.screen_w, len(self.killfeed_group), self.screen)
        
        if new not in self.killfeed_group:
            self.killfeed_group.add(new)

    def addCircle(self, g_id, xy = 0, r = 0, v = 0, new = False):
        if new:
            self.total_count += 1

        new_circle = Circle(self.circles[g_id], self.id_count[g_id], self, self.images[g_id], self.powerup_images_hud, xy, r, v, new, self.smoke_images)
        self.id_count[g_id] += 1
        self.groups[g_id].add(new_circle)

        return new_circle

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
                        self.spawn_count += 1
                        if self.spawn_count % 2 == 1:
                            self.addCircle(0, pygame.mouse.get_pos(), 0, 0, True)
                        else:
                            self.addCircle(1, pygame.mouse.get_pos(), 0, 0, True)
            
                    if event.button == 3:
                        self.fortnite_x = 0
                        self.fortnite_x_counter = 0
                        self.fortnite_x_growing = False
                        self.fortnite_y = 0
                        self.fortnite_y_counter = 0
                        self.fortnite_y_growing = False

                # keyboard click event
                if event.type == KEYDOWN:
                    if event.key == 104:
                        self.hp_mode = not self.hp_mode
                        for group in self.groups:
                            for member in group:
                                member.took_dmg = True
                    if event.key == 9:
                        self.stats_screen = not self.stats_screen
                    else:
                        self.spawnPowerup(event.key - 49, pygame.mouse.get_pos())

            num_rows = max(len(self.groups[0].sprites()) + len(self.dead_stats[0]), len(self.groups[1].sprites()) + len(self.dead_stats[1]))
            if self.cur_rows != num_rows:
                self.createStatsScreen()

            # flip() the display to put your work on screen
            pygame.display.flip()
            self.screen.blit(self.background, (0, 0))

            # Every x seconds spawn a random powerup
            if not self.done and self.frames % (5 * self.fps) == 0:
                self.spawnPowerup()

            # Every x seconds there there is less than 10 circles spawn a speed powerup
            if not self.done and self.frames % (10 * self.fps) == 0 and len(self.groups[0].sprites()) + len(self.groups[1].sprites()) < 10:
                self.spawnPowerup(4)

            # self.dead_circle = False

            # draw & update groups
            self.groups[0].draw(self.screen)
            self.groups[1].draw(self.screen)
            self.powerup_group.draw(self.screen)

            self.groups[0].update(self)
            self.laser_group.update(self)
            self.check_collisions()
            self.groups[1].update(self)
            self.check_collisions()

            self.clouds_group.update()
            self.explosions_group.update()
            for killfeed in self.killfeed_group.sprites():
                if killfeed.update() == 1:
                    self.killfeed_group.update(True)

            self.powerup_group.update(self)
            self.checkPowerupCollect()
            
            self.drawStats()

            # Do fortnite circle things
            if not self.done and len(self.groups[0].sprites()) + len(self.groups[1].sprites()) <= 10:
                self.fortnite_x_growing = self.fortnite_y_growing = True

            if self.fortnite_x_growing:
                self.fortnite_x_counter += 1
                if self.fortnite_x_counter % 3 == 0:
                    if self.fortnite_x <= 350:
                        self.fortnite_x += 1

            if self.fortnite_y_growing:
                self.fortnite_y_counter += 1
                if self.fortnite_y_counter % 3 == 0:
                    if self.fortnite_y <= 250:
                        self.fortnite_y += 1

            # print("fortnite_x: {} fortnite_y: {}".format(self.fortnite_x, self.fortnite_y))

            pygame.draw.rect(self.screen, "black", (self.fortnite_x, self.fortnite_y, self.screen_w - self.fortnite_x * 2, self.screen_h - self.fortnite_y * 2), 2)

            if len(self.groups[0].sprites()) == 0:
                self.done = True
                self.fortnite_x_growing = self.fortnite_y_growing = False

                if type(self.circles[1]["color"][1]) == type("string"):
                    color = self.circles[1]["color"][2]
                else:
                    color = self.circles[1]["color"][1]
                self.draw_text("{} Wins!".format(self.circles[1]["color"][0].capitalize()), self.font, color, self.screen_w / 2, self.screen_h / 6)

            elif len(self.groups[1].sprites()) == 0:
                self.done = True
                self.fortnite_x_growing = self.fortnite_y_growing = False

                if type(self.circles[0]["color"][1]) == type("string"):
                    color = self.circles[0]["color"][2]
                else:
                    color = self.circles[0]["color"][1]
                self.draw_text("{} Wins!".format(self.circles[0]["color"][0].capitalize()), self.font, color, self.screen_w / 2, self.screen_h / 6)

            
            if self.done and self.play_sound:
                self.play_sound = False
                if self.win_sound.get_num_channels() == 0:
                    self.win_sound.play()

            if self.done:
                self.frames_done += 1
                if self.frames_done == 10 * self.fps:
                    self.showStats()

            num_rows = max(len(self.groups[0].sprites()) + len(self.dead_stats[0]), len(self.groups[1].sprites()) + len(self.dead_stats[1]))
            if self.cur_rows != num_rows:
                self.createStatsScreen(True)

            if self.stats_screen:
                if self.frames % (self.fps / 2) == 0:
                    for group in self.groups:
                        for member in group:
                            member.checkStatsChange()

                    self.createStatsScreen()

                    for group in self.groups:
                        for member in group:
                            member.old_stats.copy(member.stats)

                self.screen.blit(self.stats_surface, (10, 50))        

            # limits FPS to 60
            self.clock.tick(self.fps)
            font = pygame.font.Font("freesansbold.ttf", 40)
            self.draw_text(str(round(self.clock.get_fps())), font, "black", 1880, 1030)

    def showStats(self):
        self.mode = "STATS"
        while self.running:
            self.frames += 1
            for event in pygame.event.get():
                # quit event
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == MOUSEBUTTONDOWN:
                    if event.button == 2:
                        self.mode = "GAME"
                        return
                # keyboard click event
                if event.type == KEYDOWN:
                    if event.key == 9:
                        self.mode = "GAME"
                        return
                    
            num_rows = max(len(self.groups[0].sprites()) + len(self.dead_stats[0]), len(self.groups[1].sprites()) + len(self.dead_stats[1]))
            if self.cur_rows != num_rows:
                self.createStatsScreen(True)

            pygame.display.flip()
            self.screen.blit(self.background, (0, 0))

            # Every x seconds spawn a random powerup
            if not self.done and self.frames % (5 * self.fps) == 0:
                self.spawnPowerup()
            
            # Every x seconds there there is less than 10 circles spawn a speed powerup
            if not self.done and self.frames % (10 * self.fps) == 0 and len(self.groups[0].sprites()) + len(self.groups[1].sprites()) < 10:
                self.spawnPowerup(4)

            # update all groups (and check for collisions) w/o drawing them
            self.groups[0].update(self)
            self.laser_group.update(self)
            self.check_collisions()
            self.groups[1].update(self)
            self.clouds_group.update()
            self.explosions_group.update()
            for killfeed in self.killfeed_group.sprites():
                if killfeed.update() == 1:
                    self.killfeed_group.update(True)
            self.powerup_group.update(self)
            

            # other functions
            self.checkPowerupCollect()
            self.drawStats()

            # Do fortnite circle things
            if not self.done and len(self.groups[0].sprites()) + len(self.groups[1].sprites()) <= 10:
                self.fortnite_x_growing = self.fortnite_y_growing = True

            if self.fortnite_x_growing:
                self.fortnite_x_counter += 1
                if self.fortnite_x_counter % 3 == 0:
                    if self.fortnite_x <= 770:
                        self.fortnite_x += 1

            if self.fortnite_y_growing:
                self.fortnite_y_counter += 1
                if self.fortnite_y_counter % 3 == 0:
                    if self.fortnite_y <= 350:
                        self.fortnite_y += 1


            if self.frames % (self.fps / 2) == 0:
                self.createStatsScreen()

            self.screen.blit(self.stats_surface, (10, 50))


            self.clock.tick(self.fps)
            font = pygame.font.Font("freesansbold.ttf", 40)
            self.draw_text(str(round(self.clock.get_fps())), font, "black", 1880, 1030)

    def printStat(self, stats, x, y, dead = False):
        font = pygame.font.Font("freesansbold.ttf", 25)
        if dead:
            color = "red"
        else:
            color = "black"

        for i in range(0, len(stats)):
            if stats[i] == "0":
                stats[i] = "-"

            if i<3:
                self.draw_text(stats[i], font, color, x + i * 100, y, True, self.stats_surface)

            elif 3<=i<4:
                self.draw_text(stats[i], font, color, x + 275 + (i-3) * 50, y, True, self.stats_surface)

            else:
                self.draw_text(stats[i], font, color, x + 300 + (i-3) * 50, y, True, self.stats_surface)

        # pygame.quit()

    def centerImageAt(self, image, x, y):
        self.screen.blit(image, (x - (image.get_size()[0] / 2), y - (image.get_size()[1] / 2)))

    def createStatsScreen(self, first = False, second = False):
        # create stats screen image
        num_rows = max(len(self.groups[0].sprites()) + len(self.dead_stats[0]), len(self.groups[1].sprites()) + len(self.dead_stats[1]))
        self.cur_rows = num_rows
        font = pygame.font.Font("freesansbold.ttf", 80)

        if first:
            self.stats_surface = pygame.Surface((1710, num_rows * 30 + 215))
            self.stats_surface.set_alpha(220)
            self.stats_surface.fill("darkgray")

            if type(self.circles[0]["color"][1]) == type("string"):
                color = self.circles[0]["color"][2]
            else:
                color = self.circles[0]["color"][1]
            self.draw_text("{} Team".format(self.circles[0]["color"][0].capitalize()), font, color, 500, 50, True, self.stats_surface)
            
            if type(self.circles[1]["color"][1]) == type("string"):
                color = self.circles[1]["color"][2]
            else:
                color = self.circles[1]["color"][1]
            self.draw_text("{} Team".format(self.circles[1]["color"][0].capitalize()), font, color, 500 + 850, 50, True, self.stats_surface)

            self.stats_surface.blit(pygame.transform.scale(self.images[0][0], (175, 175)), (30, 10))
            self.stats_surface.blit(pygame.transform.scale(self.images[1][0], (175, 175)), (30 + 850, 10))

            self.stats_surface.blit(self.sword_image, (256, 150))
            self.stats_surface.blit(self.blood_image, (329, 150))

            for image in self.powerup_images_screen:
                image.set_alpha(255)
            self.coffin_img.set_alpha(255)

            self.stats_surface.blit(self.powerup_images_screen[5], (404, 150))
            self.stats_surface.blit(self.powerup_images_screen[1], (454, 150))
            self.stats_surface.blit(self.powerup_images_screen[0], (504, 150))
            self.stats_surface.blit(self.powerup_images_screen[3], (554, 150))
            self.stats_surface.blit(self.powerup_images_screen[4], (604, 150))
            self.stats_surface.blit(self.powerup_images_screen[6], (654, 150))
            self.stats_surface.blit(self.powerup_images_screen[7], (704, 150))
            self.stats_surface.blit(self.coffin_img, (754, 150))

            self.stats_surface.blit(self.sword_image, (256 + 850, 150))
            self.stats_surface.blit(self.blood_image, (329 + 850, 150))

            self.stats_surface.blit(self.powerup_images_screen[5], (404 + 850, 150))
            self.stats_surface.blit(self.powerup_images_screen[1], (454 + 850, 150))
            self.stats_surface.blit(self.powerup_images_screen[0], (504 + 850, 150))
            self.stats_surface.blit(self.powerup_images_screen[3], (554 + 850, 150))
            self.stats_surface.blit(self.powerup_images_screen[4], (604 + 850, 150))
            self.stats_surface.blit(self.powerup_images_screen[6], (654 + 850, 150))
            self.stats_surface.blit(self.powerup_images_screen[7], (704 + 850, 150))
            self.stats_surface.blit(self.coffin_img, (754 + 850, 150))

        # for i in range(0, num_rows):
        #     if i % 2 == 0:
        #         color = "lightgray"
        #     else:
        #         color = "white"
        #     pygame.draw.rect(self.stats_surface, color, (10, 195 + 30 * i, 1690, 30))

        if second:
            first = True

        # list all stats
        group_counter = 0
        for group in self.groups:
            member_counter = 0
            for member in group:
                member_report = member.stats.report()
                if not member.stats_changed and not first:  
                    member_counter += 1
                    continue

                if member_counter % 2 == 0:
                    color = "lightgray"
                else:
                    color = "white"
                pygame.draw.rect(self.stats_surface, color, (10 + 850 * group_counter, 195 + 30 * member_counter, 845, 30))

                if member.id < 10:
                    id = "0" + str(member.id)
                else:
                    id = str(member.id)

                stats = []

                id = "id: " + str(id)
                hp = str(round(member.hp / member.max_hp * 100, 1)) + "%"
                dmg_o = str(round(member_report[0]))
                dmg_i = str(round(member_report[1]))
                hp_h = str(round(member_report[2]))
                p_r = str(member_report[3])
                p_a = str(member_report[4])
                i_u = str(member_report[5])
                m_u = str(member_report[6])
                s_u = str(member_report[7])
                b_u = str(member_report[8])
                l_h = str(member_report[9])
                p_k = str(member_report[10])

                stats.append(id); stats.append(hp); stats.append(dmg_o); stats.append(dmg_i); stats.append(hp_h)
                stats.append(p_r); #stats.append(p_a); 
                stats.append(i_u); stats.append(m_u); stats.append(s_u)
                stats.append(b_u); stats.append(l_h); stats.append(p_k)
                self.printStat(stats, 65 + group_counter * 850, 200 + member_counter * 30)

                member_counter += 1

            for stats_list in self.dead_stats[group_counter]:
                stats = stats_list[1]

                if not first:
                    member_counter += 1
                    continue

                if member_counter % 2 == 0:
                    color = "lightgray"
                else:
                    color = "white"
                pygame.draw.rect(self.stats_surface, color, (10 + 850 * group_counter, 195 + 30 * member_counter, 845, 30))

                if stats_list[0] < 10:
                    id = "0" + str(stats_list[0])
                else:
                    id = str(stats_list[0])

                
                id = "id: " + str(id)
                hp = str(round(0, 1)) + "%"
                dmg_o = str(round(stats.report()[0]))
                dmg_i = str(round(stats.report()[1]))
                hp_h = str(round(stats.report()[2]))
                p_r = str(stats.report()[3])
                p_a = str(stats.report()[4])
                i_u = str(stats.report()[5])
                m_u = str(stats.report()[6])
                s_u = str(stats.report()[7])
                b_u = str(stats.report()[8])
                l_h = str(stats.report()[9])
                p_k = str(stats.report()[10])

                stats = []
                stats.append(id); stats.append(hp); stats.append(dmg_o); stats.append(dmg_i); stats.append(hp_h)
                stats.append(p_r); #stats.append(p_a); 
                stats.append(i_u); stats.append(m_u); stats.append(s_u)
                stats.append(b_u); stats.append(l_h); stats.append(p_k)


                self.printStat(stats, 65 + group_counter * 850, 200 + member_counter * 30, True)

                member_counter += 1
            
            group_counter += 1

class Circle(pygame.sprite.Sprite):
    def __init__(self, attributes, id, game, images, hud_images, XY = 0, R = 0, VEL = 0, NEW = False, smoke_images = []):
        super().__init__()
        self.g_id = attributes["group_id"]
        self.id = id
        self.game = game
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
        

        if VEL == 0:
            # Want a constant speed, but random direction to start
            speed = attributes["velocity"]
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
        
        self.m = attributes["mass"]
        if R == 0:
            self.r = 30 + random.randint(attributes["radius_min"], attributes["radius_max"])
        else:
            self.r = R

        self.image = pygame.Surface((4*self.r, 4*self.r), pygame.SRCALPHA, 32)

        self.images = images
        self.circle_image = self.getNextImage(0)

        self.hp = self.max_hp = attributes["health"]
        self.attack = attributes["attack"]
        self.dmg_multiplier = attributes["dmg_multiplier"]

        if XY == 0:
            # Need some sort of smart spawning so that they can't overlap 
            [self.x, self.y] = game.getSafeSpawn()
        else:
            [self.x, self.y] = XY

        # Powerups array
        self.powerups = []
        self.dmg_counter = 0

        self.constructSurface(True)
        self.rect = self.image.get_rect()
        self.rect.center = [self.x, self.y]

    def constructSurface(self, powerups = False):
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

        self.image.blit(self.circle_image, (self.image.get_size()[0] / 4, self.image.get_size()[1] / 4))

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
        
        if self.game.hp_mode:
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

        font = pygame.font.Font("freesansbold.ttf", size)
        text_obj = font.render(text, 1, "black")
        text_rect = text_obj.get_rect()
        text_rect.topleft = (self.image.get_size()[0] / 2 + offset - font.size(text)[0] / 2, self.image.get_size()[1] / 2 - offset - font.size(text)[1] / 2)
        self.image.blit(text_obj, text_rect)

        hp_circle_r = min(self.r/2, 16)
        offset = math.sqrt((self.r + hp_circle_r)**2 / 2)
        pygame.draw.circle(self.image, (64, 64, 64, 100), (self.image.get_size()[0] / 2 - offset, self.image.get_size()[1] / 2 - offset), hp_circle_r)
        
        font = pygame.font.Font("freesansbold.ttf", int(hp_circle_r * 1.4))
        text_obj = font.render(str(self.id), 1, "black")
        text_rect = text_obj.get_rect()
        text_rect.topleft = (self.image.get_size()[0] / 2 - offset - font.size(str(self.id))[0] / 2, self.image.get_size()[1] / 2 - offset - font.size(str(self.id))[1] / 2)
        self.image.blit(text_obj, text_rect)

    def killCircle(self):
        # if 1 in self.powerups:
        #     new_circle = self.game.addCircle(self.g_id, self.getXY(), self.r - 10, self.getVel(), True)

        #     self.game.addKillfeed(self, new_circle, 1)
        #     self.stats.resurrectPlayer()
        #     self.game.choir_sound.play()
        #     pygame.mixer.Sound.fadeout(self.game.choir_sound, 1000)
        #     self.game.createStatsScreen(True)

        self.game.clouds_group.add(Clouds(self.x, self.y, self.game.smoke_images, self.game.screen))

        stats = self.stats
        id = self.id
        self.kill()

        row_num = self.id - (len(self.game.groups[self.g_id]) - self.game.members_per_team)
        row_num_last = len(self.game.groups[self.g_id])

        if row_num % 2 == 0:
            color = "lightgray"
        else:
            color = "white"
        pygame.draw.rect(self.game.stats_surface, color, (10 + 850 * self.g_id, 195 + 30 * row_num, 845, 30))
        
        pygame.draw.rect(self.game.stats_surface, "darkgray", (10 + 850 * self.g_id, 195 + 30 * row_num_last, 845, 30))

        # self.game.dead_circle = True
        if [id, stats] not in self.game.dead_stats[self.g_id]:
            self.game.dead_stats[self.g_id].append([id, stats])

        self.game.createStatsScreen(False, True)

    def getNextImage(self, index):
        multiplier = self.getRad() / 1024
        return pygame.transform.scale(self.images[index], (int(2048 * multiplier), int(2048 * multiplier)))

    def getPowerups(self):
        return self.powerups
    
    def removePowerup(self, id):
        if id in self.powerups:
            if len(self.powerups) == 1:
                self.powerups = []
            else:
                self.powerups.remove(id)
                self.stats.activatePowerup()
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
            self.game.heal_sound.play()
            new_hp = min(self.hp + self.max_hp / 2, self.max_hp)
            self.stats.heal(new_hp - self.hp)
            self.hp = new_hp
            self.checkImageChange()
            self.game.addKillfeed(self, self, 5)
        # if removing laser, spawn laser in same direction as circle
        if id == 7:
            self.game.laser_group.add(Laser(self, self.getG_id(), self.x, self.y, self.v_x, self.v_y, self.game.powerup_images_screen[7]))
            self.game.laser_sound.play()

        # self.constructSurface()
        self.powerups_changed = True

    def collectPowerup(self, id):
        self.powerups.append(id)

        # check if picked up star (+5 luck)
        if id == 2:
            self.bonus_luck += 5
        # check if picked up muscle (3x dmg_multiplier)
        if id == 3:
            self.dmg_multiplier *= 3
        # check if picked up muscle (double speed + dmg_multiplier)
        if id == 4:
            self.dmg_multiplier *= 1.5
            self.v_x *= 2
            self.v_y *= 2
        # check if picked up bomb (explode in some time)
        if id == 6:
            self.bomb_timer = 3 * self.game.fps

        # self.constructSurface()
        self.powerups_changed = True

    def update(self, game):
        if self.bomb_timer >= 0:
            self.bomb_timer -= 1

            if self.bomb_timer == 0:
                game.blowupBomb(self, self.x, self.y, self.getG_id())
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

        if type(self.powerups) == type(None):
            self.powerups = []

        # show damage indicator
        flag = False
        if self.dmg_counter > 0:
            self.dmg_counter -= 1

            hp_circle_r = min(self.r/2, 16)
            offset = math.sqrt((self.r + hp_circle_r)**2 / 2)
            self.image.blit(self.game.blood_image_small, (self.image.get_size()[0] / 2 + self.r, self.image.get_size()[1] / 2 - self.game.blood_image_small.get_size()[0] - 5))

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

            pygame.draw.circle(self.image, color, (self.image.get_size()[0] / 2 + offset, self.image.get_size()[1] / 2 - offset), hp_circle_r)
            
            if self.game.hp_mode:
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

            font = pygame.font.Font("freesansbold.ttf", size)
            text_obj = font.render(text, 1, "black")
            text_rect = text_obj.get_rect()
            text_rect.topleft = (self.image.get_size()[0] / 2 + offset - font.size(text)[0] / 2, self.image.get_size()[1] / 2 - offset - font.size(text)[1] / 2)
            self.image.blit(text_obj, text_rect)

            self.took_dmg = False

        if self.powerups_changed:
            self.constructSurface(True)
            self.powerups_changed = False

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
        velocity = math.sqrt(self.getVel()[0]**2 + self.getVel()[1]**2)

        if velocity == np.nan:
            velocity = 0

        # print("attacking for: {} after changes: {}".format(self.attack, self.dmg_multiplier * velocity))
        return round(self.dmg_multiplier * velocity)

    def checkImageChange(self):
        if self.hp <= self.max_hp / 4:
            self.circle_image = self.getNextImage(3)
            self.constructSurface()

        elif self.hp <= self.max_hp * 2 / 4:
            self.circle_image = self.getNextImage(2)
            self.constructSurface()

        elif self.hp <= self.max_hp * 3 / 4:
            self.circle_image = self.getNextImage(1)
            self.constructSurface()

        else:
            self.circle_image = self.getNextImage(0)
            self.constructSurface()
        
    def dealDamage(self, amount):
        self.stats.dealDamage(amount)

    def takeDamage(self, amount):
        # if self.hp - amount <= 0:
        #     self.killCircle()
        #     return -1

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

    # return something on own death
    def getHitBy(self, enemy):
        self.took_dmg = True

        amount = enemy.getAttack()

        self.hp = self.hp - amount
        self.stats.receiveDamage(amount)
        self.dmg_counter = 144
        
        self.checkImageChange()
        
        # Check if enemy had insta-kill
        if 0 in enemy.powerups:
            self.hp = 0
        
        # Check if you had a star, if so remove it
        if 2 in self.powerups: self.removePowerup(2)

        response = []

        # if you died
        if self.hp <= 0:

            if 1 in enemy.powerups:
                self.killCircle()
                response.append(2)
            elif 0 in enemy.powerups:     
                enemy.removePowerup(0)
                self.killCircle()
                response.append(6)
            elif 3 in enemy.powerups:
                self.killCircle()
                response.append(3)
            elif 4 in enemy.powerups:
                self.killCircle()
                response.append(5)
            else:
                self.killCircle()
                response.append(1)
            return response
        else:
            if 2 in enemy.powerups:
                response.append(4)
            if 3 in enemy.powerups:
                response.append(2)
            response.append(0)
        
        return response

    def hitEnemy(self, enemy):
        self.stats.dealDamage(self.getAttack())
        if 3 in self.powerups:
            self.removePowerup(3)
            self.game.punch_sound.play()

        if 5 in self.powerups:
            self.removePowerup(5)

        if 4 in self.powerups:
            self.removePowerup(4)

        if 7 in self.powerups:
            self.removePowerup(7)
    
    def getHp(self):
        return self.hp

    def getG_id(self):
        return self.g_id
    
    def getId(self):
        return self.id

class CircleStats():
    def __init__(self, flag = False):
        self.dmg_dealt = 0
        self.dmg_received = 0
        self.hp_healed = 0
        self.powerups_activated = 0
        self.kills = 0
        self.players_killed = []

        self.instakills_used = 0
        self.players_resurrected = 0
        self.stars_used = 0
        self.muscles_used = 0
        self.speeds_used = 0
        self.bombs_used = 0
        self.laser_hits = 0

        if flag: self.dmg_dealt = 1

    def dealDamage(self, amount):
        self.dmg_dealt += amount

    def receiveDamage(self, amount):
        self.dmg_received += amount

    def heal(self, amount):
        self.hp_healed += amount

    def activatePowerup(self):
        self.powerups_activated += 1

    def killPlayer(self, id):
        if id not in self.players_killed:
            self.players_killed.append(id)
            self.kills += 1

    def useInstakill(self):
        self.instakills_used += 1

    def resurrectPlayer(self):
        self.players_resurrected += 1

    def useStar(self):
        self.stars_used += 1

    def useMuscle(self):
        self.muscles_used += 1

    def useSpeed(self):
        self.speeds_used += 1

    def useBomb(self):
        self.bombs_used += 1
    
    def laserHit(self):
        self.laser_hits += 1

    def report(self):
        return [
            self.dmg_dealt,
            self.dmg_received,
            self.hp_healed,
            self.players_resurrected ,
            self.powerups_activated,
            self.instakills_used,
            self.muscles_used,
            self.speeds_used,
            self.bombs_used,
            self.laser_hits,
            self.kills
        ]

    def copy(self, other):
        self.dmg_dealt =        other.dmg_dealt
        self.dmg_received =     other.dmg_received
        self.hp_healed =        other.hp_healed
        self.powerups_activated = other.powerups_activated
        self.kills =            other.kills
        self.players_killed =   other.players_killed

        self.instakills_used =  other.instakills_used
        self.players_resurrected = other.players_resurrected
        self.stars_used =       other.stars_used
        self.muscles_used =     other.muscles_used
        self.speeds_used =      other.speeds_used
        self.bombs_used =       other.bombs_used
        self.laser_hits =       other.laser_hits

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
    def __init__(self, x, y, images, screen):
        super().__init__()
        self.x = x
        self.y = y
        self.frames = 0
        self.images = images
        self.screen = screen

    def update(self):
        # puff of smoke animation
        self.frames += 2
        if self.frames <= 50:
            if self.frames <= 10:
                self.screen.blit(self.images[0], (self.x - self.images[0].get_size()[0] / 2, self.y - self.images[0].get_size()[1] / 2))
            elif self.frames <= 20:
                self.screen.blit(self.images[1], (self.x - self.images[1].get_size()[0] / 2, self.y - self.images[1].get_size()[1] / 2))
            elif self.frames <= 30:
                self.screen.blit(self.images[0], (self.x - self.images[0].get_size()[0] / 2, self.y - self.images[0].get_size()[1] / 2))
            elif self.frames <= 40:
                self.screen.blit(self.images[1], (self.x - self.images[1].get_size()[0] / 2, self.y - self.images[1].get_size()[1] / 2))
            elif self.frames <= 50:
                self.screen.blit(self.images[4], (self.x - self.images[4].get_size()[0] / 2, self.y - self.images[4].get_size()[1] / 2))
        else:
            self.kill()

class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y, images, screen):
        super().__init__()
        self.x = x
        self.y = y
        self.frames = 0
        self.images = images
        self.screen = screen

    def update(self):
        # explosion animation
        self.frames += 2
        if self.frames <= 70:
            if self.frames <= 10:
                self.screen.blit(self.images[0], (self.x - self.images[0].get_size()[0] / 2, self.y - self.images[0].get_size()[1] / 2))
            elif self.frames <= 20:
                self.screen.blit(self.images[1], (self.x - self.images[1].get_size()[0] / 2, self.y - self.images[1].get_size()[1] / 2))
            elif self.frames <= 30:
                self.screen.blit(self.images[0], (self.x - self.images[0].get_size()[0] / 2, self.y - self.images[0].get_size()[1] / 2))
            elif self.frames <= 40:
                self.screen.blit(self.images[1], (self.x - self.images[1].get_size()[0] / 2, self.y - self.images[1].get_size()[1] / 2))
            elif self.frames <= 50:
                self.screen.blit(self.images[4], (self.x - self.images[4].get_size()[0] / 2, self.y - self.images[4].get_size()[1] / 2))
            elif self.frames <= 60:
                self.screen.blit(self.images[5], (self.x - self.images[5].get_size()[0] / 2, self.y - self.images[5].get_size()[1] / 2))
            elif self.frames <= 70:
                self.screen.blit(self.images[6], (self.x - self.images[6].get_size()[0] / 2, self.y - self.images[6].get_size()[1] / 2))
        else:
            self.kill()

class Laser(pygame.sprite.Sprite):
    def __init__(self, circle, g_id, x, y, vx, vy, image):
        super().__init__()
        self.g_id = g_id
        self.circle = circle
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

        if game.mode == "GAME":
            self.image.set_alpha(255)
            game.screen.blit(self.image, (int(self.x - self.image.get_size()[0]/2), int(self.y - self.image.get_size()[1]/2)))
        
        # game.screen.blit(self.image, self.x, self.y)

        self.frames += 1
        if self.frames >= game.fps * 5:
            self.kill()

class Killfeed(pygame.sprite.Sprite):
    def __init__(self, left_circle, right_circle, action_img, x, count, screen):
        super().__init__()
        self.left_circle = left_circle
        self.right_circle = right_circle
        self.action_img = action_img
        self.x = x
        self.y = 260 + (60 * count)
        self.next_y = self.y
        self.screen = screen
        self.surface = pygame.Surface((200, 60), pygame.SRCALPHA, 32)
        self.left_img = pygame.transform.scale(left_circle.circle_image, (50, 50))
        self.right_img = pygame.transform.scale(right_circle.circle_image, (50, 50))
        self.frames = 0

        # self.surface.fill("gray")
        # self.surface.set_colorkey((0, 0, 0))
        self.surface.convert_alpha()
        self.surface.blit(self.left_img, (10, 5))
        self.draw_text(str(self.left_circle.getId()), pygame.font.Font("freesansbold.ttf", 20), "black", self.surface, 60, 42)
        self.surface.blit(self.action_img, (80, 15))
        self.surface.blit(self.right_img, (140, 5))
        self.draw_text(str(self.right_circle.getId()), pygame.font.Font("freesansbold.ttf", 20), "black", self.surface, 190, 42)

    def update(self, cycle = False):
        # check if they are now cycled out 
        if cycle:
            self.next_y -= 60

            if self.next_y < 260:
                self.kill()
                return
            
        if self.y != self.next_y:
            self.y -= 2

        self.frames += 1 
        if self.frames > 60 * 13: 
            self.kill()
            return 1
        elif self.frames < 60 * 5:
            self.surface.set_alpha(255)
            # self.left_img.set_alpha(255)
            # self.right_img.set_alpha(255)
            # self.action_img.set_alpha(255)
        else:
            alpha = 255 + 30 * 5 - self.frames / 2
            self.surface.set_alpha(alpha)
            # self.left_img.set_alpha(alpha)
            # self.right_img.set_alpha(alpha)
            # self.action_img.set_alpha(alpha)

        # draw elements
        self.screen.blit(self.surface, (self.x, self.y))
        # self.screen.blit(self.left_img, (self.x + 10, self.y))
        # self.draw_text(str(self.left_circle.getId()), pygame.font.Font("freesansbold.ttf", 20), "black", self.screen, self.x + 60, self.y + 40)
        # self.screen.blit(self.action_img, (self.x + 80, self.y + 10))
        # self.screen.blit(self.right_img, (self.x + 140, self.y))
        # self.draw_text(str(self.right_circle.getId()), pygame.font.Font("freesansbold.ttf", 20), "black", self.screen, self.x + 190, self.y + 40)

    def draw_text(self, text, font, color, surface, x, y):
        text_obj = font.render(text, 1, color)
        text_rect = text_obj.get_rect()
        text_rect.topleft = (x - font.size(text)[0] / 2, y)
        surface.blit(text_obj, text_rect)

def generateAllCircles():
    print("GENERATING ALL CIRCLES - THIS WILL TAKE A MOMENT ON FIRST RUN\n")
    for color in colors:
        for id in range(0, 2):
            if os.path.isdir("circles/{}/{}".format(id, color[0])):
                pass
            else:
                print("Generating all {} images".format(color[0]))
                # check for any special colors
                if type(color[0]) == type("string"):
                    os.mkdir("circles/{}/{}".format(id, color[0]))
                    for face in range(0, 4):
                        path = "circles/{}/{}.png".format(id, face)
                        image = pygame.image.load(path)

                        background = pygame.image.load("circles/{}".format(color[1]))

                        # loop through image, replace green pixels
                        for j in range(0, image.get_size()[0]):
                            for k in range(0, image.get_size()[1]):
                                pixel = image.get_at((j, k))
                                if pixel[0] <= 100 and pixel[1] >= 150 and pixel[2] <= 100:
                                    image.set_at((j, k), background.get_at((j, k)))
                                elif pixel[0] <= 100 and 100 <= pixel[1] <= 150 and pixel[2] <= 100:
                                    image.set_at((j, k), color[2])
                                elif 100 <= pixel[0] <= 150 and pixel[1] >= 200 and 100 <= pixel[2] <= 150:
                                    image.set_at((j, k), background.get_at((j, k)))

                        pygame.image.save(image, "circles/{}/{}/{}.png".format(id, color[0], face))

                # generate shapes as normal
                else:
                    os.mkdir("circles/{}/{}".format(id, color[0]))
                    for face in range(0, 4):
                        path = "circles/{}/{}.png".format(id, face)
                        image = pygame.image.load(path)

                        # loop through image, replace green pixels
                        for j in range(0, image.get_size()[0]):
                            for k in range(0, image.get_size()[1]):
                                pixel = image.get_at((j, k))
                                if pixel[0] <= 100 and pixel[1] >= 150 and pixel[2] <= 100:
                                    image.set_at((j, k), color[1])
                                elif pixel[0] <= 100 and 100 <= pixel[1] <= 150 and pixel[2] <= 100:
                                    image.set_at((j, k), color[3])
                                elif 100 <= pixel[0] <= 150 and pixel[1] >= 200 and 100 <= pixel[2] <= 150:
                                    image.set_at((j, k), color[2])

                        pygame.image.save(image, "circles/{}/{}/{}.png".format(id, color[0], face))

def test():
    img = pygame.image.load("circles/purple/0.png")
    for i in range(0, img.get_size()[0]):
        for j in range(0, img.get_size()[1]):
            if img.get_at((i, j)) == (153, 37, 118, 255):
                img.set_at((i, j), (255, 255, 255, 255))

    screen = pygame.display.set_mode((2048,2048))  
    done = False  
    
    while not done:  
        for event in pygame.event.get():  
            if event.type == pygame.QUIT:  
                done = True 

        screen.blit(img, (0, 0))
        pygame.display.flip()

def main():
    pygame.init()
    pygame.mixer.pre_init(44100, -16, 2, 512)

    # seed = False
    seed = int.from_bytes(random.randbytes(4), "little")
    # seed = "Enter your seed here :)"

    print("Playing game with seed: {}".format(seed))
    game = Game(circles[0], circles[1], seed)
    game.play_game()
    pygame.quit()

generateAllCircles()
main()
# test()
