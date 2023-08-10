import pygame, random, math, numpy as np, os, time, pygame_textinput
from pygame.locals import *
from network import Network
from request import Request

colors = [
    # SPECIAL COLORS - TAKE CARE
    ["rainbow", "gradient1.png", (255, 180, 180)],
    ["grayscale", "gradient2.png", (100, 100, 100)],
    ["rose", "gradient3.png", (255, 51, 153)],
    ["lavender", "gradient4.png", (153, 153, 255)],
    ["mint", "gradient5.png", (0, 255, 128)],
    ["violet", "gradient6.png", (204, 28, 134)],
    ["sunrise", "gradient7.png", (223, 143, 15)],
    ["clay", "gradient8.png", (140, 70, 70)],
    ["sky", "gradient9.png", (49, 142, 172)],
    ["algae", "gradient10.png", (16, 143, 22)],
    ["bog", "gradient11.png", (160, 123, 107)],
    ["wound", "gradient12.png", (209, 33, 34)],
    ["dusk", "gradient13.png", (61, 62, 128)],
    ["rainier", "gradient14.png", (189, 126, 147)],
    ["midnight", "gradient15.png", (18, 18, 18)],
    ["eggshell", "gradient16.png", (138, 116, 122)],
    ["bruise", "gradient17.png", (92, 50, 124)],
    # REGULAR LIGHT DARK
    # ["red", (255, 0, 0), (255, 102, 102), (102, 0, 0)],
    # ["orange", (255, 128, 0), (255, 178, 102), (153, 76, 0)],
    # ["yellow", (255, 255, 0), (255, 255, 102), (153, 153, 0)],
    # ["green", (0, 204, 0), (51, 255, 51), (0, 153, 0)],
    # ["blue", (0, 0, 204), (51, 51, 255), (0, 0, 102)],
    # ["purple", (102, 0, 204), (153, 51, 255), (51, 0, 102)],
    # ["pink", (255, 0, 127), (255, 102, 178), (153, 0, 76)],
    # ["gray", (96, 96, 96), (160, 160, 160), (64, 64, 64)],
]

mins = {
    "density": 1,
    "velocity": 1,
    "radius": 5,
    "health": 25,
    "dmg_multiplier": 0.1,
    "luck": 1,
}

maxes = {
    "density": 99,
    "velocity": 9,
    "radius": 300,
    "health": 999,
    "dmg_multiplier": 9.9,
    "luck": 99,
}

circles = [
    {
        "density": 1,
        "velocity": 3,
        "radius_min": 30,
        "radius_max": 45,
        "health": 260,
        "dmg_multiplier": 1.7,
        "luck": 8,
        "team_size": 15
    },
    {
        "density": 1,
        "velocity": 4,
        "radius_min": 40,
        "radius_max": 55,
        "health": 340,
        "dmg_multiplier": 1.5,
        "luck": 10,
        "team_size": 15
    },
    {
        "density": 1,
        "velocity": 4,
        "radius_min": 50,
        "radius_max": 60,
        "health": 120,
        "dmg_multiplier": 1,
        "luck": 15,
        "team_size": 15
    },
    {
        "density": 1,
        "velocity": 4,
        "radius_min": 30,
        "radius_max": 40,
        "health": 160,
        "dmg_multiplier": 2.5,
        "luck": 12,
        "team_size": 15
    },
    {
        "density": 1,
        "velocity": 4,
        "radius_min": 85,
        "radius_max": 90,
        "health": 750,
        "dmg_multiplier": 1.5,
        "luck": 8,
        "team_size": 5
    },
]

class Game: 
    def __init__(self, c0, c0_count, c1, c1_count, screen, seed = False, real = True):
        self.real = real

        self.cursor = pygame.transform.scale(pygame.image.load("backgrounds/cursor.png"), (12, 12))
        self.cursor_rect = self.cursor.get_rect()
        self.cursor_rect.center = pygame.mouse.get_pos()

        if seed != False:
            random.seed(seed)
        
        self.c0 = c0
        self.c1 = c1
        self.circles = [c0, c1]

        self.c0_count = c0_count
        self.c1_count = c1_count
        self.circle_counts = [self.c0_count, self.c1_count]

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
        if os.path.isdir("circles/{}/{}".format(self.circles[1]["face_id"], self.circles[1]["color"][0])):
            for i in range(0, 4):
                self.c1_images.append(pygame.image.load("circles/{}/{}/{}.png".format(self.circles[1]["face_id"], self.circles[1]["color"][0], i)))
        else:
            print("\nJust a moment! New circles being drawn!")
            os.mkdir("circles/{}/{}".format(self.circles[1]["face_id"], self.circles[1]["color"][0]))
            for n in range(0, 4):
                path = "circles/{}/{}.png".format(self.circles[1]["face_id"], n)
                image = pygame.image.load(path)

                # loop through image, replace green pixels
                for j in range(0, image.get_size()[0]):
                    for k in range(0, image.get_size()[1]):
                        pixel = image.get_at((j, k))
                        if pixel[0] <= 100 and pixel[1] >= 150 and pixel[2] <= 100:
                            image.set_at((j, k), self.circles[1]["color"][1])
                        elif pixel[0] <= 100 and 100 <= pixel[1] <= 150 and pixel[2] <= 100:
                            image.set_at((j, k), self.circles[1]["color"][3])
                        elif 100 <= pixel[0] <= 150 and pixel[1] >= 200 and 100 <= pixel[2] <= 150:
                            image.set_at((j, k), self.circles[1]["color"][2])

                pygame.image.save(image, "circles/{}/{}/{}.png".format(self.circles[1]["face_id"], self.circles[1]["color"][0], n))
                self.c1_images.append(image)

        if os.path.isdir("circles/{}/{}".format(self.circles[0]["face_id"], self.circles[0]["color"][0])):
            for i in range(0, 4):
                self.c0_images.append(pygame.image.load("circles/{}/{}/{}.png".format(self.circles[0]["face_id"], self.circles[0]["color"][0], i)))
        else:
            print("\nJust a moment! New circles being drawn!")
            os.mkdir("circles/{}/{}".format(self.circles[0]["face_id"], self.circles[0]["color"][0]))
            for n in range(0, 4):
                path = "circles/{}/{}.png".format(self.circles[0]["face_id"], n)
                image = pygame.image.load(path)

                for j in range(0, image.get_size()[0]):
                    for k in range(0, image.get_size()[1]):
                        pixel = image.get_at((j, k))
                        if pixel[0] <= 100 and pixel[1] >= 150 and pixel[2] <= 100:
                            image.set_at((j, k), self.circles[0]["color"][1])
                        elif pixel[0] <= 100 and 100 <= pixel[1] <= 150 and pixel[2] <= 100:
                            image.set_at((j, k), self.circles[0]["color"][3])
                        elif 100 <= pixel[0] <= 150 and pixel[1] >= 200 and 100 <= pixel[2] <= 150:
                            image.set_at((j, k), self.circles[0]["color"][2])

                pygame.image.save(image, "circles/{}/{}/{}.png".format(self.circles[0]["face_id"], self.circles[0]["color"][0], n))
                self.c0_images.append(image)
     
        self.powerups = [
            ["powerups/skull.png",   0],
            ["powerups/cross.png",   1],
            ["powerups/star.png",    2],
            ["powerups/muscle.png",  3],
            ["powerups/speed.png",   4],
            ["powerups/health.png",  5],
            ["powerups/bomb.png",    6],
            ["powerups/laser.png",   7],
            ["powerups/blue_laser.png", 8],
            ["powerups/mushroom.png", 9],
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

        self.exit = pygame.image.load("backgrounds/exit.png")
        self.exit_rect = self.exit.get_rect()
        self.exit_rect.center = (1870, 1050)

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

        self.game_sounds = []
        self.game_sounds.append(pygame.mixer.Sound("sounds/game/1.wav"))

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

        self.screen_w = 1720
        self.screen_h = 1080
        self.fps = 60
        self.font = pygame.font.SysFont("bahnschrift", 160)
        self.screen = screen
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
        self.hp_mode_surface = pygame.Surface((200, 200), pygame.SRCALPHA, 32)
        self.loading = pygame.image.load("backgrounds/loading.png")

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
        self.blue_laser_group = pygame.sprite.Group()

        # Clouds & explosions
        self.clouds_group = pygame.sprite.Group()
        self.explosions_group = pygame.sprite.Group()

        # Killfeed
        self.killfeed_group = pygame.sprite.Group()

        # Max hp of each group
        self.max_hps = [0, 0]
        self.hps = []

        # self.members_per_team = 11

        # Fixed a bug by swapping the array index on self.circles[]["health"]
        # no clue how that works but it works

        self.max_hps[0] += self.circles[0]["health"] * self.circle_counts[0]
        self.max_hps[1] += self.circles[1]["health"] * self.circle_counts[1]
        self.hps = [self.max_hps[0], self.max_hps[1]]

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

        self.total_count = self.circle_counts[0] + self.circle_counts[1]
        # ----------------------
        for i in range(self.circle_counts[0]):
            self.addCircle(0)
        for i in range(self.circle_counts[1]):
            self.addCircle(1)

        self.createStatsScreen(True)

        # self.game_sounds[random.randint(0, len(self.game_sounds) - 1)].play(-1)

    def playSound(self, sound):
        if not self.real:
            return

        if sound.get_num_channels() <= 1:
            sound.play()
            if sound == self.wind_sound:
                pygame.mixer.Sound.fadeout(sound, 1500)
            elif sound == self.choir_sound:
                pygame.mixer.Sound.fadeout(sound, 1000)
            if sound == self.fuse_sound:
                sound.play(9)

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
                    self.playSound(self.pop_sound)
                    member.collectPowerup(powerup.getId())

                    if powerup.getId() == 6:
                        self.playSound(self.fuse_sound)
                    elif powerup.getId() == 4:
                        self.playSound(self.wind_sound)
                    elif powerup.getId() == 2:
                        self.playSound(self.twinkle_sound)
                    
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
        # Clear winner of any powerups they should win
        if 2 in winner.powerups:
            winner.stats.useStar()
        if 3 in winner.powerups:
            winner.removePowerup(3)
            winner.stats.useMuscle()
        if 4 in winner.powerups:
            winner.removePowerup(4)
            winner.stats.useSpeed()
        if 5 in winner.powerups:
            winner.removePowerup(5)
        if 7 in winner.powerups:
            winner.removePowerup(7)
        if 8 in winner.powerups:
            winner.removePowerup(8)
            # Will switch real brains of each removePowerup call to be done by Game, starting with this
            self.memberSpawnBlueLasers(winner)

        if 2 in loser.powerups:
            loser.removePowerup(2)


        if loser.hp <= 0:
            return 1
        else:
            return 0
        
    def memberSpawnBlueLasers(self, circle):
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
        
        for direction in directions:
            self.blue_laser_group.add(BlueLaser(circle, direction, self.powerup_images_screen[8]))

    def memberKillMember(self, winner, loser, action = -1):
        loser_resurrect = False

        # Create killfeed, play sound
        self.addKillfeed(winner, loser, action)
        self.playSound(self.death_sounds[len(self.death_sounds)-1])

        # check if dead loser has resurrect
        if 1 in loser.powerups:
            loser_resurrect = self.memberResurrectMember(loser)

        # remove powerup % update stats, kill circle
        winner.stats.killPlayer(loser.id)
        loser.killCircle()

        return loser_resurrect

    def memberInstaKillMember(self, winner, loser):
        loser_resurrect = False

        # Create killfeed, play sound
        self.addKillfeed(winner, loser, 0)
        self.playSound(self.shotgun_sound)

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
        self.playSound(self.choir_sound)

        # remove powerup
        god.removePowerup(1)

        return new_circle.id
            
    def handle_collision(self, mem_1, mem_2, flag = 0):
        self.playSound(self.collision_sounds[random.randint(0, len(self.collision_sounds)-1)])

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
            # self.powerups[member_1.getG_id()].append(member_1.getPowerups())

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
                            member_1.colliding_with.append(member_2.getId())
                            member_2.colliding_with.append(member_1.getId())
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
                        if member_1.getG_id() != laser.g_id:
                            self.laserHitMember(laser, member_1)

            for laser in self.blue_laser_group.sprites():
                [lx, ly] = [laser.x, laser.y]
                lr = laser.r

                dist = math.sqrt( (m1_x - lx)**2 + (m1_y - ly)**2 )
                max_dist = lr + m1_r

                if dist <= max_dist:
                    if not member_1.getId() in laser.ids_collided_with:
                        if member_1.getG_id() != laser.g_id:
                            self.blueLaserHitMember(laser, member_1)

    def laserHitMember(self, laser, hit):
        laser_damage = 25
        laser.circle.stats.laserHit()
        laser.circle.stats.dealDamage(laser_damage)
        laser.ids_collided_with.append(hit.id)
        self.playSound(self.laser_hit_sound)

        hit.takeDamage(laser_damage)

        if hit.hp <= 0:
            possible_id = self.memberKillMember(laser.circle, hit, 7)
            if possible_id: laser.ids_collided_with.append(possible_id)

            if 1 in laser.circle.powerups and not possible_id:
                self.memberResurrectMember(laser.circle, hit)

    def blueLaserHitMember(self, laser, hit):
        laser_damage = 10
        laser.circle.stats.blueLaserHit()
        laser.circle.stats.dealDamage(laser_damage)
        laser.ids_collided_with.append(hit.id)
        self.playSound(self.laser_hit_sound)

        hit.takeDamage(laser_damage)

        if hit.hp <= 0:
            possible_id = self.memberKillMember(laser.circle, hit, 8)
            if possible_id: laser.ids_collided_with.append(possible_id)

            if 1 in laser.circle.powerups and not possible_id:
                self.memberResurrectMember(laser.circle, hit)

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

    def blowupBomb(self, circle, x, y):
        self.fuse_sound.stop()

        # Deal damage to everyone close to this point
        if self.mode == "GAME":
            self.explosions_group.add(Explosion(x, y, self.explosion_images, self.screen))
        self.playSound(self.explosion_sound)
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

    def bombKillMember(self, bomb_holder, killed):
        self.clouds_group.add(Clouds(killed.x, killed.y, self.smoke_images, self.screen))
        bomb_holder.stats.killPlayer(killed.id)

        self.playSound(self.death_sounds[random.randint(0, len(self.death_sounds)-1)])
        self.addKillfeed(bomb_holder, killed, 6)

        killed.killCircle()

        if 1 in killed.powerups:
            self.memberResurrectMember(killed)

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


        if xy == 0:
            xy = self.spawn_locations[g_id][self.id_count[g_id]-1]

            if self.circle_counts[g_id] % 5 != 0:
                remainder = (self.circle_counts[g_id] % 5)

                
                # if you are one of the remainders, change your y coordinate
                if self.id_count[g_id] - 1 >= self.circle_counts[g_id] - remainder:
                    xy = (xy[0], (self.id_count[g_id] % 5) * self.screen_h / (remainder + 1))

        
        new_circle = Circle(self.circles[g_id], self.id_count[g_id], self, self.images[g_id], self.powerup_images_hud, xy, r, v, new, self.smoke_images)
        self.id_count[g_id] += 1
        self.groups[g_id].add(new_circle)

        return new_circle

    def play_game(self):
        while self.running:
            self.frames += 1
            # poll for events
            for event in pygame.event.get():
                # button click event
                if event.type == MOUSEBUTTONDOWN:
                    self.playSound(self.click_sound)
                    if event.button == 1:
                        if self.exit_rect.collidepoint(pygame.mouse.get_pos()):
                            self.running = False
                        else:
                            self.addCircle(0, pygame.mouse.get_pos(), 0, 0, True)
                            self.createStatsScreen(True)
            
                    elif event.button == 2:
                        self.fortnite_x = 0
                        self.fortnite_x_counter = 0
                        self.fortnite_x_growing = False
                        self.fortnite_y = 0
                        self.fortnite_y_counter = 0
                        self.fortnite_y_growing = False

                    elif event.button == 3:
                        self.addCircle(1, pygame.mouse.get_pos(), 0, 0, True)
                        self.createStatsScreen(True)

                # keyboard click event
                if event.type == KEYDOWN:
                    if event.key == 104:
                        self.toggleHealthMode()
                    if event.key == 9:
                        self.stats_screen = not self.stats_screen
                        self.createStatsScreen(True)
                    else:
                        self.spawnPowerup(event.key - 48, pygame.mouse.get_pos())

            num_rows = max(len(self.groups[0].sprites()) + len(self.dead_stats[0]), len(self.groups[1].sprites()) + len(self.dead_stats[1]))
            if self.cur_rows != num_rows:
                self.createStatsScreen(True)

            # flip() the display to put your work on screen
            
            if self.real:
                pygame.display.flip()
                self.screen.blit(self.background, (0, 0))
                self.screen.blit(self.exit, self.exit_rect)
                self.screen.blit(self.hp_mode_surface, (self.screen_w + 100, self.screen_h - 100))

            # Every x seconds spawn a random powerup
            if not self.done and self.frames % (5 * self.fps) == 0:
                self.spawnPowerup()

            # Every x seconds there there is less than 10 circles spawn a speed powerup
            if not self.done and self.frames % (10 * self.fps) == 0 and len(self.groups[0].sprites()) + len(self.groups[1].sprites()) < ((self.c0_count + self.c1_count) / 3):
                self.spawnPowerup(4)

            self.dead_circle = False

            # draw & update groups
            if self.real:
                self.groups[0].draw(self.screen)
                self.groups[1].draw(self.screen)
                self.laser_group.draw(self.screen)
                self.blue_laser_group.draw(self.screen)
                self.powerup_group.draw(self.screen)
                self.killfeed_group.draw(self.screen)
                self.clouds_group.draw(self.screen)
                self.explosions_group.draw(self.screen)

            self.groups[0].update(self)
            self.laser_group.update(self)
            self.blue_laser_group.update(self)
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
            
            if self.real:
                self.drawStats()

            # Do fortnite circle things
            if not self.done and len(self.groups[0].sprites()) + len(self.groups[1].sprites()) <= ((self.c0_count + self.c1_count) / 3):
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

            if self.real:
                pygame.draw.rect(self.screen, "black", (self.fortnite_x, self.fortnite_y, self.screen_w - self.fortnite_x * 2, self.screen_h - self.fortnite_y * 2), 2)

            if len(self.groups[0].sprites()) == 0:
                self.done = True
                self.fortnite_x_growing = self.fortnite_y_growing = False

                if self.real: self.draw_text("{} Wins!".format(self.circles[1]["color"][0].capitalize()), self.font, "white", self.screen_w / 2, self.screen_h / 6)

            elif len(self.groups[1].sprites()) == 0:
                self.done = True
                self.fortnite_x_growing = self.fortnite_y_growing = False

                if self.real: self.draw_text("{} Wins!".format(self.circles[0]["color"][0].capitalize()), self.font, "white", self.screen_w / 2, self.screen_h / 6)

            
            if self.done and self.play_sound:
                self.play_sound = False
                if self.win_sound.get_num_channels() == 0:
                    self.playSound(self.win_sound)

            if self.done:
                self.frames_done += 1
                if self.frames_done == 10 * self.fps:
                    self.stats_screen = True

                    if self.done and not self.real:
                        self.createStatsScreen(True)
                        return self.stats_surface

            num_rows = max(len(self.groups[0].sprites()) + len(self.dead_stats[0]), len(self.groups[1].sprites()) + len(self.dead_stats[1]))
            if self.cur_rows != num_rows and self.real:
                self.createStatsScreen(True)

            if self.stats_screen and self.real:
                if self.frames % (self.fps / 2) == 0:
                    for group in self.groups:
                        for member in group:
                            member.checkStatsChange()

                    self.createStatsScreen(True)

                    for group in self.groups:
                        for member in group:
                            member.old_stats.copy(member.stats)

                if self.real: self.screen.blit(self.stats_surface, (10, 50))

            self.cursor_rect.center = pygame.mouse.get_pos()
            self.screen.blit(self.cursor, self.cursor_rect)

            # limits FPS to 60
            if self.real: self.clock.tick(self.fps)

            # fps counter
            # font = pygame.font.Font("freesansbold.ttf", 40)
            # self.draw_text(str(round(self.clock.get_fps())), font, "black", 1880, 1030)

        self.close_sound.play()
        self.screen.blit(self.background, (0, 0))
        self.screen.blit(self.loading, (1920 / 2 - self.loading.get_size()[0] / 2, 1080 / 2 - self.loading.get_size()[1] / 2))
        pygame.display.update()
        time.sleep(0.5)
        self.createStatsScreen(True)
        return self.stats_surface

    def toggleHealthMode(self):
        self.hp_mode_surface = pygame.Surface((200, 200), pygame.SRCALPHA, 32)
        self.hp_mode = not self.hp_mode
        for group in self.groups:
            for member in group:
                member.took_dmg = True

        # font = pygame.font.Font("freesansbold.ttf", 40)
        # if self.hp_mode:
        #     self.draw_text("Health: Percentage", font, self.screen_w, self.screen_h - 100, True, self.hp_mode_surface)
        # else:
        #     self.draw_text("Health: Values", font, self.screen_w, self.screen_h - 100, True, self.hp_mode_surface)

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

        self.screen.blit(image, (self.screen_w + 105, 10))
        self.draw_text("x{}".format(len(self.groups[0])), pygame.font.SysFont("bahnschrift", 25), "black", self.screen_w + 147, 105)
        self.draw_text("{}%".format(round((self.hps[0] / self.max_hps[0]) * 100, 1)), pygame.font.SysFont("bahnschrift", 25), "black", self.screen_w + 155, 130)

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
        self.screen.blit(image, (self.screen_w + 10, 10))
        self.draw_text("x{}".format(len(self.groups[1])), pygame.font.SysFont("bahnschrift", 25), "black", self.screen_w + 52, 105)
        self.draw_text("{}%".format(round((self.hps[1] / self.max_hps[1]) * 100, 1)), pygame.font.SysFont("bahnschrift", 25), "black", self.screen_w + 60, 130)

    def printStat(self, stats, x, y, dead = False):
        font = pygame.font.SysFont("bahnschrift", 25)
        if dead:
            color = "red"
        else:
            color = "black"

        for i in range(0, len(stats)):
            if stats[i] == "0":
                stats[i] = "-"

            if i<3:
                self.draw_text(stats[i], font, color, x + i * 100, y - 4, True, self.stats_surface)

            elif 3<=i<4:
                self.draw_text(stats[i], font, color, x + 275 + (i-3) * 50, y - 4, True, self.stats_surface)

            else:
                self.draw_text(stats[i], font, color, x + 300 + (i-3) * 50, y - 4, True, self.stats_surface)
        
    def centerImageAt(self, image, x, y):
        self.screen.blit(image, (x - (image.get_size()[0] / 2), y - (image.get_size()[1] / 2)))

    def createStatsScreen(self, first = False, second = False):
        # create stats screen image
        num_rows = max(len(self.groups[0].sprites()) + len(self.dead_stats[0]), len(self.groups[1].sprites()) + len(self.dead_stats[1]))
        self.cur_rows = num_rows
        font = pygame.font.SysFont("bahnschrift", 80)

        if first:
            self.stats_surface = pygame.Surface((1710, num_rows * 30 + 215))
            self.stats_surface.set_alpha(220)
            self.stats_surface.fill("darkgray")

            if type(self.circles[0]["color"][1]) == type("string"):
                color = self.circles[0]["color"][2]
            else:
                color = self.circles[0]["color"][1]
            self.draw_text("{} Team".format(self.circles[0]["color"][0].capitalize()), font, color, 500 + 850 - 10, 50, True, self.stats_surface)
            
            if type(self.circles[1]["color"][1]) == type("string"):
                color = self.circles[1]["color"][2]
            else:
                color = self.circles[1]["color"][1]
            self.draw_text("{} Team".format(self.circles[1]["color"][0].capitalize()), font, color, 500 - 10, 50, True, self.stats_surface)

            self.stats_surface.blit(pygame.transform.scale(self.images[0][0], (175, 175)), (30 + 850 - 10, 10))
            self.stats_surface.blit(pygame.transform.scale(self.images[1][0], (175, 175)), (30 - 10, 10))

            self.stats_surface.blit(self.sword_image, (256 - 10, 150))
            self.stats_surface.blit(self.blood_image, (329 - 10, 150))

            for image in self.powerup_images_screen:
                image.set_alpha(255)
            self.coffin_img.set_alpha(255)

            self.stats_surface.blit(self.powerup_images_screen[5], (404 - 10, 150))
            self.stats_surface.blit(self.powerup_images_screen[1], (454 - 10, 150))
            self.stats_surface.blit(self.powerup_images_screen[0], (504 - 10, 150))
            self.stats_surface.blit(self.powerup_images_screen[3], (554 - 10, 150))
            self.stats_surface.blit(self.powerup_images_screen[4], (604 - 10, 150))
            self.stats_surface.blit(self.powerup_images_screen[6], (654 - 10, 150))
            self.stats_surface.blit(self.powerup_images_screen[7], (704 - 10, 150))
            self.stats_surface.blit(self.powerup_images_screen[8], (754 - 10, 150))
            self.stats_surface.blit(self.coffin_img, (804 - 10, 150))

            self.stats_surface.blit(self.sword_image, (256 + 850 - 10, 150))
            self.stats_surface.blit(self.blood_image, (329 + 850 - 10, 150))

            self.stats_surface.blit(self.powerup_images_screen[5], (404 + 850 - 10, 150))
            self.stats_surface.blit(self.powerup_images_screen[1], (454 + 850 - 10, 150))
            self.stats_surface.blit(self.powerup_images_screen[0], (504 + 850 - 10, 150))
            self.stats_surface.blit(self.powerup_images_screen[3], (554 + 850 - 10, 150))
            self.stats_surface.blit(self.powerup_images_screen[4], (604 + 850 - 10, 150))
            self.stats_surface.blit(self.powerup_images_screen[6], (654 + 850 - 10, 150))
            self.stats_surface.blit(self.powerup_images_screen[7], (704 + 850 - 10, 150))
            self.stats_surface.blit(self.powerup_images_screen[8], (754 + 850 - 10, 150))
            self.stats_surface.blit(self.coffin_img, (804 + 850 - 10, 150))

        # for i in range(0, num_rows):
        #     if i % 2 == 0:
        #         color = "lightgray"
        #     else:
        #         color = "white"
        #     pygame.draw.rect(self.stats_surface, color, (10, 195 + 30 * i, 1690, 30))

        if second:
            first = True

        # list all stats
        group_counter = 1
        offset_counter = 0
        for group in reversed(self.groups):
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
                pygame.draw.rect(self.stats_surface, color, (10 + 850 * offset_counter, 195 + 30 * member_counter, 845, 30))

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
                b_l_h = str(member_report[10])
                p_k = str(member_report[11])

                stats.append(id); stats.append(hp); stats.append(dmg_o); stats.append(dmg_i); stats.append(hp_h)
                stats.append(p_r); #stats.append(p_a); 
                stats.append(i_u); stats.append(m_u); stats.append(s_u)
                stats.append(b_u); stats.append(l_h); stats.append(b_l_h); stats.append(p_k)
                self.printStat(stats, 65 + offset_counter * 850, 200 + member_counter * 30)

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
                pygame.draw.rect(self.stats_surface, color, (10 + 850 * offset_counter, 195 + 30 * member_counter, 845, 30))

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
                b_l_h = str(stats.report()[10])
                p_k = str(stats.report()[11])


                stats = []
                stats.append(id); stats.append(hp); stats.append(dmg_o); stats.append(dmg_i); stats.append(hp_h)
                stats.append(p_r); #stats.append(p_a); 
                stats.append(i_u); stats.append(m_u); stats.append(s_u)
                stats.append(b_u); stats.append(l_h); stats.append(b_l_h); stats.append(p_k)


                self.printStat(stats, 65 + offset_counter * 850, 200 + member_counter * 30, True)

                member_counter += 1
            
            group_counter -= 1
            offset_counter += 1

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

        self.image = pygame.Surface((4*self.r, 4*self.r), pygame.SRCALPHA, 32)
        self.images = images
        self.circle_image = self.getNextImage(0)
        self.circle_image_rect = self.circle_image.get_rect()
        self.circle_image_rect.center = (self.image.get_size()[0] / 2, self.image.get_size()[1] / 2)

        self.hp = self.max_hp = attributes["health"]
        self.dmg_multiplier = attributes["dmg_multiplier"]

        if XY == 0:
            # Need some sort of smart spawning so that they can't overlap 
            [self.x, self.y] = game.spawn_locations[self.g_id][self.id]
        else:
            [self.x, self.y] = XY

        # Powerups array
        self.powerups = []
        self.dmg_counter = 0

        self.constructSurface(True)
        self.rect = self.image.get_rect()
        self.rect.center = [self.x, self.y]

    def growTo(self, radius):
        self.growing = True
        self.next_r = radius

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

    def killCircle(self):
        self.game.clouds_group.add(Clouds(self.x, self.y, self.game.smoke_images, self.game.screen))

        stats = self.stats
        id = self.id
        self.kill()

        # row_num = self.id - (len(self.game.groups[self.g_id]) - self.game.circle_counts[self.g_id])
        # # row_num_last = len(self.game.groups[self.g_id])

        # if row_num % 2 == 0:
        #     color = "lightgray"
        # else:
        #     color = "white"
        # pygame.draw.rect(self.game.stats_surface, color, (10 + 850 * self.g_id, 195 + 30 * row_num, 845, 30))
        
        # pygame.draw.rect(self.game.stats_surface, "darkgray", (10 + 850 * self.g_id, 195 + 30 * row_num_last, 845, 30))

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
            self.game.playSound(self.game.heal_sound)
            new_hp = min(self.hp + self.max_hp / 2, self.max_hp)
            self.stats.heal(new_hp - self.hp)
            self.hp = new_hp
            self.checkImageChange()
            self.game.addKillfeed(self, self, 5)
        # if removing laser, spawn laser in same direction as circle
        if id == 7:
            # want to limit the speed of laser to 10
            desired_speed = 8
            current_speed = math.sqrt(self.v_x**2 + self.v_y**2)
            multiplier = desired_speed / current_speed

            self.game.laser_group.add(Laser(self, self.getG_id(), self.x, self.y, self.v_x * multiplier, self.v_y * multiplier, self.game.powerup_images_screen[7]))
            self.game.playSound(self.game.laser_sound)

        if id == 9:
            self.growTo(self.r - self.growth_amount)
            self.dmg_multiplier /= 5
            

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
        if id == 9:
            # start growing
            self.growing = True
            self.next_r = self.r + self.growth_amount

            # heal some amount + killfeed and shit
            self.game.playSound(self.game.heal_sound)
            self.stats.heal(100)
            self.hp += 100
            self.checkImageChange()
            self.game.addKillfeed(self, self, 9)

            # get increased damage multiplier
            self.dmg_multiplier *= 5

        # self.constructSurface()
        self.powerups_changed = True

    def update(self, game):
        if self.bomb_timer >= 0:
            self.bomb_timer -= 1

            if self.bomb_timer == 0:
                game.blowupBomb(self, self.x, self.y)
                self.bomb_timer = -1
                self.removePowerup(6)

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
                self.checkImageChange()
                self.constructSurface(True)
                self.circle_image_rect = self.circle_image.get_rect()
                self.circle_image_rect.center = (self.image.get_size()[0] / 2, self.image.get_size()[1] / 2)
                self.rect = self.image.get_rect()
                self.rect.center = [self.x, self.y]
            elif self.r > self.next_r:
                self.r -= 1
                self.m = round(self.density * (3/4) * 3.14 * self.r**3)
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
            
            if self.frames_held_mushroom == self.game.fps * 10:
                self.frames_held_mushroom = 0
                self.removePowerup(9)



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

class CircleStats:
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
        self.blue_laser_hits = 0

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

    def blueLaserHit(self):
        self.blue_laser_hits += 1

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
            self.blue_laser_hits,
            self.kills,
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
        self.image = self.images[0]
        self.screen = screen

        self.rect = self.image.get_rect()
        self.rect.center = [self.x, self.y]

    def update(self):
        # puff of smoke animation
        self.frames += 2
        if self.frames <= 50:
            if self.frames <= 10:
                self.image = self.images[0]
            elif self.frames <= 20:
                self.image = self.images[1]
            elif self.frames <= 30:
                self.image = self.images[2]
            elif self.frames <= 40:
                self.image = self.images[3]
            elif self.frames <= 50:
                self.image = self.images[4]
        else:
            self.kill()
        
        self.rect = self.image.get_rect()
        self.rect.center = [self.x, self.y]

class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y, images, screen):
        super().__init__()
        self.x = x
        self.y = y
        self.frames = 0
        self.images = images
        self.screen = screen
        self.image = self.images[0]

        self.rect = self.image.get_rect()
        self.rect.center = [self.x, self.y]

    def update(self):
        # explosion animation
        self.frames += 2
        if self.frames <= 70:
            if self.frames <= 10:
                self.image = self.images[0]
            elif self.frames <= 20:
                self.image = self.images[1]
            elif self.frames <= 30:
                self.image = self.images[2]
            elif self.frames <= 40:
                self.image = self.images[3]
            elif self.frames <= 50:
                self.image = self.images[4]
            elif self.frames <= 60:
                self.image = self.images[5]
            elif self.frames <= 70:
                self.image = self.images[6]
        else:
            self.kill()

        self.rect = self.image.get_rect()
        self.rect.center = [self.x, self.y]

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

        self.rect = self.image.get_rect()
        self.rect.center = [self.x, self.y]

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

        self.image.set_alpha(255)
        # game.screen.blit(self.image, (int(self.x - self.image.get_size()[0]/2), int(self.y - self.image.get_size()[1]/2)))
        
        # game.screen.blit(self.image, self.x, self.y)

        self.rect.center = [self.x, self.y]

        self.frames += 1
        if self.frames >= game.fps * 5:
            self.kill()

class BlueLaser(pygame.sprite.Sprite):
    def __init__(self, circle, directions, image):
        super().__init__()
        self.circle = circle
        self.g_id = circle.getG_id()
        self.x = circle.getXY()[0]
        self.y = circle.getXY()[1]
        self.vx = directions[0]
        self.vy = directions[1]
        self.image = image
        self.r = image.get_size()[0]/2
        self.ids_collided_with = []

        self.rect = self.image.get_rect()
        self.rect.center = [self.x, self.y]

    def update(self, game):
        self.x += self.vx
        self.y += self.vy

        self.rect.center = [self.x, self.y]

        flag = False
        # ensure laser stays within bounds
        if self.x > game.screen_w - self.r - game.fortnite_x:
            flag = True

        if self.x < self.r + game.fortnite_x:
            flag = True

        if self.y > game.screen_h - self.r - game.fortnite_y:
            flag = True

        if self.y < self.r + game.fortnite_y:
            flag = True

        if flag == True: self.kill()

        self.image.set_alpha(255)
        # game.screen.blit(self.image, (int(self.x - self.image.get_size()[0]/2), int(self.y - self.image.get_size()[1]/2))) 

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
        self.draw_text(str(self.left_circle.getId()), pygame.font.SysFont("bahnschrift", 20), "black", self.surface, 60, 38)
        self.surface.blit(self.action_img, (80, 15))
        self.surface.blit(self.right_img, (140, 5))
        self.draw_text(str(self.right_circle.getId()), pygame.font.SysFont("bahnschrift", 20), "black", self.surface, 190, 38)

        self.image = self.surface
        self.rect = self.image.get_rect()
        self.rect.topleft = [self.x, self.y]

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
            self.image.set_alpha(255)
            # self.left_img.set_alpha(255)
            # self.right_img.set_alpha(255)
            # self.action_img.set_alpha(255)
        else:
            alpha = 255 + 30 * 5 - self.frames / 2
            self.image.set_alpha(alpha)
            # self.left_img.set_alpha(alpha)
            # self.right_img.set_alpha(alpha)
            # self.action_img.set_alpha(alpha)

        self.rect.topleft = [self.x, self.y]

        # draw elements
        # self.screen.blit(self.surface, (self.x, self.y))
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

class SimpleCircle(pygame.sprite.Sprite):
    def __init__(self, xy, image):
        super().__init__()
        self.x = xy[0]
        self.y = xy[1]
        self.vx = random.randint(-4, 4)
        self.vy = random.randint(-3, 3)
        self.r = random.randint(50, 60)
        self.m = random.randint(10, 15)
        self.frames = 0

        self.face_id = random.randint(0, 2)
        self.color_string = colors[random.randint(0, len(colors)-1)][0]
        self.image = pygame.transform.scale(image, (self.r * 2, self.r * 2))

        self.rect = self.image.get_rect()
        self.rect.center = [self.x, self.y]

    def update(self):
         # ensure circle stays within bounds
        if self.x > 1920 - self.r:
            self.x = 1920 - self.r
            self.vx = -1 * self.vx

        if self.x < self.r:
            self.x = self.r
            self.vx = -1 * self.vx

        if self.y > 400 - self.r:
            self.y = 400 - self.r
            self.vy = -1 * self.vy

        if self.y < self.r:
            self.y = self.r
            self.vy = -1 * self.vy

        # update position
        self.rect.center = [self.x, self.y]
        
        self.x += self.vx
        self.y += self.vy
        self.frames += 1
        self.rect.center = [self.x, self.y]

    def setVel(self, vel):
        self.vx = vel[0]
        self.vy = vel[1]

class preGame:
    def __init__(self):
        self.network = Network()

        self.cursor = pygame.transform.scale(pygame.image.load("backgrounds/cursor.png"), (12, 12))
        self.cursor_rect = self.cursor.get_rect()
        self.cursor_rect.center = pygame.mouse.get_pos()
        self.screen = pygame.display.set_mode((1920, 1080), pygame.NOFRAME)
        self.background = pygame.image.load("backgrounds/BG1.png")
        self.title = pygame.image.load("backgrounds/title.png")
        self.title_rect = self.title.get_rect()
        self.title_rect.center = (1920 / 2, 1080 / 2)
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("bahnschrift", 80)
        self.game_played = False
        self.stats_surface = 0

        self.exit_clicked = False
        self.frames_since_exit_clicked = 0

        self.click_sound = pygame.mixer.Sound("sounds/click.wav")
        self.start_sound = pygame.mixer.Sound("sounds/start.wav")
        self.open_sound = pygame.mixer.Sound("sounds/open.wav")
        self.menu_music = pygame.mixer.Sound("sounds/menu.wav")
        self.close_sound = pygame.mixer.Sound("sounds/close.wav")

        self.open_sound.set_volume(.5)
        self.menu_music.set_volume(.5)
        self.close_sound.set_volume(.5)
        
        self.open_sound.play()

        self.play = pygame.image.load("backgrounds/play.png")
        self.play_rect = self.play.get_rect()
        self.play_rect.center = [1920 / 2, 875]

        self.you = pygame.image.load("backgrounds/you.png")
        self.you_rect = self.you.get_rect()
        self.you_rect.center = (550, 400)

        self.opponent = pygame.image.load("backgrounds/opponent.png")
        self.opponent_rect = self.opponent.get_rect()
        self.opponent_rect.center = (1340, 400)

        self.ready_red = pygame.image.load("backgrounds/readyred.png")
        self.ready_red_rect = self.ready_red.get_rect()
        self.ready_red_rect.center = (1920 / 2, 1000)

        self.ready_green = pygame.image.load("backgrounds/readygreen.png")
        self.ready_green_rect = self.ready_green.get_rect()
        self.ready_green_rect.center = (1920 / 2, 1000)

        self.simulate = pygame.image.load("backgrounds/simulate.png")
        self.simulate_rect = self.simulate.get_rect()
        self.simulate_rect.center = [1920 / 2, 725]

        self.network_match = pygame.image.load("backgrounds/networkmatch.png")
        self.network_match_rect = self.network_match.get_rect()
        self.network_match_rect.center = [1920 / 2, 980]

        self.screen.blit(self.background, (0, 0))
        self.screen.blit(self.title, self.title_rect)
        pygame.display.set_caption("shapegame")
        pygame.display.update()

        self.num_faces = 5

        self.face_0 = random.randint(0, self.num_faces - 1)
        self.color_0 = random.randint(0, len(colors)-1)
        self.face_1 = random.randint(0, self.num_faces - 1)
        self.color_1 = random.randint(0, len(colors)-1)

        self.face_ids = [self.face_0, self.face_1]

        self.c0_count = circles[self.face_0]["team_size"]
        self.c1_count = circles[self.face_1]["team_size"]

        self.shown_circles = [[self.face_0, colors[self.color_0][0]], [self.face_1, colors[self.color_1][0]]]

        self.circles = pygame.sprite.Group()

        self.circle_images = []
        for i in range(0, 5):
            self.circle_images.append([])
            for color in colors:
                self.circle_images[i].append(pygame.transform.scale(pygame.image.load("circles/{}/{}/0.png".format(i, color[0])), (200, 200)))


        self.circle_1 = self.circle_images[self.face_0][self.color_0]
        self.circle_2 = self.circle_images[self.face_1][self.color_1]

        self.arrow_right = pygame.transform.scale(pygame.image.load("backgrounds/arrow_right.png"), (50, 50))
        self.arrow_left = pygame.transform.scale(pygame.image.load("backgrounds/arrow_left.png"), (50, 50))

        self.exit = pygame.image.load("backgrounds/exit.png")
        self.exit_rect = self.exit.get_rect()
        self.exit_rect.center = (1870, 1050)

        self.loading = pygame.image.load("backgrounds/loading.png")
        self.simulating = pygame.image.load("backgrounds/simulating.png")

        # draw arrows
        self.color_right_1 = self.arrow_right
        self.color_right_1_rect = self.color_right_1.get_rect()
        self.color_right_1_rect.center = (1920 / 3 + 50, 2 * 1080 / 3 + 230)

        self.color_left_1 = self.arrow_left
        self.color_left_1_rect = self.color_right_1.get_rect()
        self.color_left_1_rect.center = (1920 / 3 - 50, 2 * 1080 / 3 + 230)

        self.face_right_1 = self.arrow_right
        self.face_right_1_rect = self.face_right_1.get_rect()
        self.face_right_1_rect.center = (1920 / 3 + 50, 2 * 1080 / 3 + 270)

        self.face_left_1 = self.arrow_left
        self.face_left_1_rect = self.face_right_1.get_rect()
        self.face_left_1_rect.center = (1920 / 3 - 50, 2 * 1080 / 3 + 270)

        self.color_right_0 = self.arrow_right
        self.color_right_0_rect = self.color_right_0.get_rect()
        self.color_right_0_rect.center = (2 * 1920 / 3 + 50, 2 * 1080 / 3 + 230)

        self.color_left_0 = self.arrow_left
        self.color_left_0_rect = self.color_right_0.get_rect()
        self.color_left_0_rect.center = (2 * 1920 / 3 - 50, 2 * 1080 / 3 + 230)

        self.face_right_0 = self.arrow_right
        self.face_right_0_rect = self.face_right_0.get_rect()
        self.face_right_0_rect.center = (2 * 1920 / 3 + 50, 2 * 1080 / 3 + 270)

        self.face_left_0 = self.arrow_left
        self.face_left_0_rect = self.face_right_0.get_rect()
        self.face_left_0_rect.center = (2 * 1920 / 3 - 50, 2 * 1080 / 3 + 270)


        self.l_count_obj = self.font.render(str(self.c0_count), 1, "white")
        self.l_count_rect = self.l_count_obj.get_rect()
        self.l_count_rect.center = (1920 - 125, 820)
        
        self.l_left = self.arrow_left
        self.l_left_rect = self.l_left.get_rect()
        self.l_left_rect.center = (1920 - 150, 880)

        self.l_right = self.arrow_right
        self.l_right_rect = self.l_right.get_rect()
        self.l_right_rect.center = (1920 - 95, 880)

        self.r_count_obj = self.font.render(str(self.c1_count), 1, "white")
        self.r_count_rect = self.r_count_obj.get_rect()
        self.r_count_rect.center = (125, 820)
        
        self.r_left = self.arrow_left
        self.r_left_rect = self.r_left.get_rect()
        self.r_left_rect.center = (100, 880)

        self.r_right = self.arrow_right
        self.r_right_rect = self.r_right.get_rect()
        self.r_right_rect.center = (150, 880)

        self.seed_input_clicked = False

        self.input_manager = pygame_textinput.TextInputManager()
        self.input_manager.value = "Seed (optional)"
        self.input_manager.cursor_pos = len(self.input_manager.value)

        self.seed_input = pygame_textinput.TextInputVisualizer(self.input_manager, pygame.font.SysFont("bahnschrift", 35))
        self.seed_input.font_color = "white"
        self.seed_input.cursor_color = "white"
        self.seed_input.cursor_visible = False
        self.seed_input_rect = self.seed_input.surface.get_rect()
        self.seed_input_rect.center = [1920 / 2, 1050]
        # self.seed_input.value = "Seed (optional)"
        # self.seed_input.cursor_pos = 2

        self.stat_rects = [{}, {}]
        self.menu_music.play(-1)

    def createCircleStatsSurfaces(self):
        surface_0 = pygame.Surface((400, 400), pygame.SRCALPHA, 32)
        surface_1 = pygame.Surface((400, 400), pygame.SRCALPHA, 32)
        font = pygame.font.SysFont("bahnschrift", 30)

        keys = ["Density:", "Velocity:", "Radius:", "Health:", "Damage x:", "Luck:"]
        values_0 = [str(circles[self.face_0]["density"]), str(circles[self.face_0]["velocity"]), 
                    str(circles[self.face_0]["radius_min"]) + " - " + str(circles[self.face_0]["radius_max"]), 
                    str(circles[self.face_0]["health"]), str(circles[self.face_0]["dmg_multiplier"]), 
                    str(circles[self.face_0]["luck"])]
        
        values_1 = [str(circles[self.face_1]["density"]), str(circles[self.face_1]["velocity"]), 
                    str(circles[self.face_1]["radius_min"]) + " - " + str(circles[self.face_1]["radius_max"]), 
                    str(circles[self.face_1]["health"]), str(circles[self.face_1]["dmg_multiplier"]), 
                    str(circles[self.face_1]["luck"])]

        element_count = 0
        for element in keys:
            key_obj = font.render(element, 1, "white")
            key_rect = key_obj.get_rect()
            key_rect.topright = (250, element_count * 30)

            surface_0.blit(key_obj, key_rect)
            element_count += 1

        keys_for_rects = ["density", "velocity", "radius", "health", "dmg_multiplier", "luck"]

        element_count = 0
        for element in values_0:
            key_obj = font.render(element, 1, "white")
            key_rect = key_obj.get_rect()
            key_rect.topleft = (270, element_count * 30)

            surface_0.blit(key_obj, key_rect)

            self.stat_rects[0][str(keys_for_rects[element_count])] = key_rect
            element_count += 1

        element_count = 0
        for element in keys:
            key_obj = font.render(element, 1, "white")
            key_rect = key_obj.get_rect()
            key_rect.topright = (250, element_count * 30)

            surface_1.blit(key_obj, key_rect)
            element_count += 1

        element_count = 0
        for element in values_1:
            key_obj = font.render(element, 1, "white")
            key_rect = key_obj.get_rect()
            key_rect.topleft = (270, element_count * 30)

            surface_1.blit(key_obj, key_rect)

            self.stat_rects[1][str(keys_for_rects[element_count])] = key_rect
            element_count += 1

        return [surface_0, surface_1]

    def createCircleStatsSurfacesNetwork(self, player_face, opponent_face):
        surface_0 = pygame.Surface((400, 400), pygame.SRCALPHA, 32)
        surface_1 = pygame.Surface((400, 400), pygame.SRCALPHA, 32)
        font = pygame.font.SysFont("bahnschrift", 30)

        keys = ["Density:", "Velocity:", "Radius:", "Health:", "Damage x:", "Luck:"]
        values_0 = [str(circles[player_face]["density"]), str(circles[player_face]["velocity"]), 
                    str(circles[player_face]["radius_min"]) + " - " + str(circles[player_face]["radius_max"]), 
                    str(circles[player_face]["health"]), str(circles[player_face]["dmg_multiplier"]), 
                    str(circles[player_face]["luck"])]
        
        values_1 = [str(circles[opponent_face]["density"]), str(circles[opponent_face]["velocity"]), 
                    str(circles[opponent_face]["radius_min"]) + " - " + str(circles[opponent_face]["radius_max"]), 
                    str(circles[opponent_face]["health"]), str(circles[opponent_face]["dmg_multiplier"]), 
                    str(circles[opponent_face]["luck"])]

        element_count = 0
        for element in keys:
            key_obj = font.render(element, 1, "white")
            key_rect = key_obj.get_rect()
            key_rect.topright = (250, element_count * 30)

            surface_0.blit(key_obj, key_rect)
            element_count += 1

        keys_for_rects = ["density", "velocity", "radius", "health", "dmg_multiplier", "luck"]

        element_count = 0
        for element in values_0:
            key_obj = font.render(element, 1, "white")
            key_rect = key_obj.get_rect()
            key_rect.topleft = (270, element_count * 30)

            surface_0.blit(key_obj, key_rect)

            self.stat_rects[0][str(keys_for_rects[element_count])] = key_rect
            element_count += 1

        element_count = 0
        for element in keys:
            key_obj = font.render(element, 1, "white")
            key_rect = key_obj.get_rect()
            key_rect.topright = (250, element_count * 30)

            surface_1.blit(key_obj, key_rect)
            element_count += 1

        element_count = 0
        for element in values_1:
            key_obj = font.render(element, 1, "white")
            key_rect = key_obj.get_rect()
            key_rect.topleft = (270, element_count * 30)

            surface_1.blit(key_obj, key_rect)

            self.stat_rects[1][str(keys_for_rects[element_count])] = key_rect
            element_count += 1

        return [surface_0, surface_1]

    def addNewCircles(self):
        # CHANGE WHEN ADDING FACE_IDS
        self.new_circle_images = [0, 0, 0, 0, 0]
        self.new_circle_images[0] = self.circle_images[0].copy()
        self.new_circle_images[1] = self.circle_images[1].copy()
        self.new_circle_images[2] = self.circle_images[2].copy()
        self.new_circle_images[3] = self.circle_images[3].copy()
        self.new_circle_images[4] = self.circle_images[4].copy()

        self.face_id = random.randint(0, self.num_faces - 1)
        self.color_id = random.randint(0, len(self.new_circle_images[self.face_id])-1)
        self.circles.add(SimpleCircle((1 * 1920 / 5, 150), self.new_circle_images[self.face_id][self.color_id]))
        for element in self.new_circle_images:
            element.pop(self.color_id)

        self.face_id = random.randint(0, self.num_faces - 1)
        self.color_id = random.randint(0, len(self.new_circle_images[self.face_id])-1)
        self.circles.add(SimpleCircle((2 * 1920 / 5, 150), self.new_circle_images[self.face_id][self.color_id]))
        for element in self.new_circle_images:
            element.pop(self.color_id)

        self.face_id = random.randint(0, self.num_faces - 1)
        self.color_id = random.randint(0, len(self.new_circle_images[self.face_id])-1)
        self.circles.add(SimpleCircle((3 * 1920 / 5, 150), self.new_circle_images[self.face_id][self.color_id]))
        for element in self.new_circle_images:
            element.pop(self.color_id)

        self.face_id = random.randint(0, self.num_faces - 1)
        self.color_id = random.randint(0, len(self.new_circle_images[self.face_id])-1)
        self.circles.add(SimpleCircle((4 * 1920 / 5, 150), self.new_circle_images[self.face_id][self.color_id]))
        for element in self.new_circle_images:
            element.pop(self.color_id)

        self.face_id = random.randint(0, self.num_faces - 1)
        self.color_id = random.randint(0, len(self.new_circle_images[self.face_id])-1)
        self.circles.add(SimpleCircle((5 * 1920 / 5, 150), self.new_circle_images[self.face_id][self.color_id]))
        for element in self.new_circle_images:
            element.pop(self.color_id)

        self.face_id = random.randint(0, self.num_faces - 1)
        self.color_id = random.randint(0, len(self.new_circle_images[self.face_id])-1)
        self.circles.add(SimpleCircle((1 * 1920 / 5, 300), self.new_circle_images[self.face_id][self.color_id]))
        for element in self.new_circle_images:
            element.pop(self.color_id)

        self.face_id = random.randint(0, self.num_faces - 1)
        self.color_id = random.randint(0, len(self.new_circle_images[self.face_id])-1)
        self.circles.add(SimpleCircle((2 * 1920 / 5, 300), self.new_circle_images[self.face_id][self.color_id]))
        for element in self.new_circle_images:
            element.pop(self.color_id)

        self.face_id = random.randint(0, self.num_faces - 1)
        self.color_id = random.randint(0, len(self.new_circle_images[self.face_id])-1)
        self.circles.add(SimpleCircle((3 * 1920 / 5, 300), self.new_circle_images[self.face_id][self.color_id]))
        for element in self.new_circle_images:
            element.pop(self.color_id)

        self.face_id = random.randint(0, self.num_faces - 1)
        self.color_id = random.randint(0, len(self.new_circle_images[self.face_id])-1)
        self.circles.add(SimpleCircle((4 * 1920 / 5, 300), self.new_circle_images[self.face_id][self.color_id]))
        for element in self.new_circle_images:
            element.pop(self.color_id)

        self.face_id = random.randint(0, self.num_faces - 1)
        self.color_id = random.randint(0, len(self.new_circle_images[self.face_id])-1)
        self.circles.add(SimpleCircle((5 * 1920 / 5, 300), self.new_circle_images[self.face_id][self.color_id]))
        for element in self.new_circle_images:
            element.pop(self.color_id)

    def checkCollisions(self):
        for c1 in self.circles.sprites():
            for c2 in self.circles.sprites():
                if c1 == c2:
                    continue

                dist = math.sqrt( (c1.x - c2.x)**2 + (c1.y - c2.y)**2 )
                max_dist = c1.r + c2.r
                
                if dist <= max_dist:
                    self.collide(c1, c2)

    def collide(self, c1, c2):
        c1.x -= c1.vx
        c1.y -= c1.vy
        c2.x -= c2.vx
        c2.y -= c2.vy

        # STEP 1

        [x2, y2] = [c2.x, c2.y]
        [x1, y1] = [c1.x, c1.y]

        norm_vec = np.array([x2 - x1, y2 - y1])

        divisor = math.sqrt(norm_vec[0]**2 + norm_vec[1]**2)
        unit_vec = np.array([norm_vec[0] / divisor, norm_vec[1] / divisor])

        unit_tan_vec = np.array([-1 * unit_vec[1], unit_vec[0]])

        # STEP 2

        v1 = np.array([c1.vx, c1.vy])
        m1 = c1.m

        v2 = np.array([c2.vx, c2.vy])
        m2 = c2.m

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
        c1.setVel(v1p)

        v2p = v2np_ + v2tp_
        c2.setVel(v2p)

    def show(self):
        running = True
        while running:
            # Want to have two circles spawn in from opposite sides of the screen and bounce away from each other
            if len(self.circles) == 0:
                self.addNewCircles()

            if self.game_played:
                if self.stats_surface != 0:
                    self.screen.blit(self.stats_surface, (1920 / 2 - self.stats_surface.get_size()[0] / 2, 50)) 
            else:
                self.circles.draw(self.screen)
            self.circles.update()
            # self.circles.sprites()[0].update()
            self.checkCollisions()
            # self.circles.sprites()[1].update()


            # Bottom half of screen
            simulate_clicked = False
            play_clicked = False
            self.shown_circles = [[self.face_0, colors[self.color_0][0]], [self.face_1, colors[self.color_1][0]]]

            # Draw some shit
            pygame.display.flip()
            self.screen.blit(self.background, (0, 0))
            self.screen.blit(self.title, (1920 / 2 - self.title.get_size()[0] / 2, 1080 / 2 - self.title.get_size()[1] / 2))
            self.screen.blit(self.play, self.play_rect)
            self.screen.blit(self.exit, self.exit_rect)
            self.screen.blit(self.simulate, self.simulate_rect)
            self.screen.blit(self.network_match, self.network_match_rect)

            # Show two circles 
            self.screen.blit(self.circle_1, (2 * 1920 / 3 - self.circle_1.get_size()[0] / 2, 2 * 1080 / 3))
            self.screen.blit(self.circle_2, (1920 / 3 - self.circle_2.get_size()[0] / 2, 2 * 1080 / 3))


            self.screen.blit(self.color_right_1, self.color_right_1_rect)
            self.screen.blit(self.color_left_1, self.color_left_1_rect)
            self.screen.blit(self.face_right_1, self.face_right_1_rect)
            self.screen.blit(self.face_left_1, self.face_left_1_rect)


            self.screen.blit(self.color_right_0, self.color_right_0_rect)
            self.screen.blit(self.color_left_0, self.color_left_0_rect)
            self.screen.blit(self.face_right_0, self.face_right_0_rect)
            self.screen.blit(self.face_left_0, self.face_left_0_rect)

            [self.surface_0, self.surface_1] = self.createCircleStatsSurfaces()

            self.screen.blit(self.surface_0, (1300, 735))
            self.screen.blit(self.surface_1, (150, 735))

            # pygame.draw.rect(self.screen, "white", (-10, -10, 1940, 410), 2)
            self.l_count_obj = self.font.render(str(self.c0_count), 1, "white")
            self.l_count_rect = self.l_count_obj.get_rect()
            self.l_count_rect.center = (1920 - 125, 820)

            self.r_count_obj = self.font.render(str(self.c1_count), 1, "white")
            self.r_count_rect = self.r_count_obj.get_rect()
            self.r_count_rect.center = (125, 820)

            # draw counts + arrows
            self.screen.blit(self.l_count_obj, self.l_count_rect)
            self.screen.blit(self.l_left, self.l_left_rect)
            self.screen.blit(self.l_right, self.l_right_rect)

            self.screen.blit(self.r_count_obj, self.r_count_rect)
            self.screen.blit(self.r_left, self.r_left_rect)
            self.screen.blit(self.r_right, self.r_right_rect)

            events = pygame.event.get()

            if self.seed_input_clicked: self.seed_input.update(events); self.seed_input_rect = self.seed_input.surface.get_rect(); self.seed_input_rect.center = [1920 / 2, 1000]

            self.screen.blit(self.seed_input.surface, self.seed_input_rect)

            for event in events:
                if event.type == MOUSEBUTTONDOWN:
                    self.click_sound.play()
                    if event.button == 1:
                        # loop through stats rects and check if any of them got clicked?
                        for key, item in self.stat_rects[0].items():
                            if item.collidepoint((pygame.mouse.get_pos()[0]-1300, pygame.mouse.get_pos()[1]-735)):

                                amount = 1
                                pressed_keys = pygame.key.get_pressed()
                                counter = 0
                                for pressed_key in pressed_keys:
                                    if pressed_key == 1 and counter == 225:
                                        amount *= 10
                                    if pressed_key == 1 and counter == 224:
                                        amount *= -1
                                    counter += 1

                                if key == "radius":
                                    circles[self.face_ids[0]]["radius_min"] += amount
                                    circles[self.face_ids[0]]["radius_max"] += amount

                                    if circles[self.face_ids[0]]["radius_max"] > maxes["radius"]:
                                        circles[self.face_ids[0]]["radius_max"] = maxes["radius"]
                                        circles[self.face_ids[0]]["radius_min"] = maxes["radius"] - 10

                                    if circles[self.face_ids[0]]["radius_min"] < mins["radius"]:
                                        circles[self.face_ids[0]]["radius_max"] = mins["radius"]
                                        circles[self.face_ids[0]]["radius_min"] = mins["radius"] - 10
                                else:
                                    if key == "dmg_multiplier" or key == "luck":
                                        amount *= 0.1

                                    circles[self.face_ids[0]][key] = round(amount + circles[self.face_ids[0]][key], 1)

                                    if circles[self.face_ids[0]][key] > maxes[key]:
                                        circles[self.face_ids[0]][key] = maxes[key]

                                    if circles[self.face_ids[0]][key] < mins[key]:
                                        circles[self.face_ids[0]][key] = mins[key]
                                
                                [self.surface_0, self.surface_1] = self.createCircleStatsSurfaces()
                        for key, item in self.stat_rects[1].items():
                            if item.collidepoint((pygame.mouse.get_pos()[0]-150, pygame.mouse.get_pos()[1]-735)):

                                amount = 1
                                pressed_keys = pygame.key.get_pressed()
                                counter = 0
                                for pressed_key in pressed_keys:
                                    if pressed_key == 1 and counter == 225:
                                        amount *= 10
                                    if pressed_key == 1 and counter == 224:
                                        amount *= -1
                                    counter += 1

                                if key == "radius":
                                    circles[self.face_ids[1]]["radius_min"] += amount
                                    circles[self.face_ids[1]]["radius_max"] += amount

                                    if circles[self.face_ids[1]]["radius_max"] > maxes["radius"]:
                                        circles[self.face_ids[1]]["radius_max"] = maxes["radius"]
                                        circles[self.face_ids[1]]["radius_min"] = maxes["radius"] - 10

                                    if circles[self.face_ids[1]]["radius_min"] < mins["radius"]:
                                        circles[self.face_ids[1]]["radius_max"] = mins["radius"]
                                        circles[self.face_ids[1]]["radius_min"] = mins["radius"] - 1
                                else:
                                    if key == "dmg_multiplier" or key == "luck":
                                        amount *= 0.1

                                    circles[self.face_ids[1]][key] = round(amount + circles[self.face_ids[1]][key], 1)

                                    if circles[self.face_ids[1]][key] > maxes[key]:
                                        circles[self.face_ids[1]][key] = maxes[key]

                                    if circles[self.face_ids[1]][key] < mins[key]:
                                        circles[self.face_ids[1]][key] = mins[key]
                                
                                [self.surface_0, self.surface_1] = self.createCircleStatsSurfaces()

                        unclick_seed_input = True

                        if self.network_match_rect.collidepoint(pygame.mouse.get_pos()):
                            self.networkPreGame()
                            self.exit_clicked = False

                        elif self.seed_input_rect.collidepoint(pygame.mouse.get_pos()):
                            self.seed_input_clicked = True
                            self.seed_input.cursor_visible = True
                            unclick_seed_input = False

                        elif self.color_right_1_rect.collidepoint(pygame.mouse.get_pos()):
                            self.color_1 += 1
                            if self.color_1 == len(colors): self.color_1 = 0
                            self.changeCircles()

                        elif self.color_left_1_rect.collidepoint(pygame.mouse.get_pos()):
                            self.color_1 -= 1
                            if self.color_1 == -1: self.color_1 = len(colors) - 1
                            # play_clicked = True
                            self.changeCircles()

                        elif self.face_right_1_rect.collidepoint(pygame.mouse.get_pos()):
                            self.face_1 += 1
                            if self.face_1 == self.num_faces: self.face_1 = 0
                            self.changeCircles()

                        elif self.face_left_1_rect.collidepoint(pygame.mouse.get_pos()):
                            self.face_1 -= 1
                            if self.face_1 == -1: self.face_1 = self.num_faces - 1
                            self.changeCircles()

                        elif self.color_right_0_rect.collidepoint(pygame.mouse.get_pos()):
                            self.color_0 += 1
                            if self.color_0 == len(colors): self.color_0 = 0
                            self.changeCircles()

                        elif self.color_left_0_rect.collidepoint(pygame.mouse.get_pos()):
                            self.color_0 -= 1
                            if self.color_0 == -1: self.color_0 = len(colors) - 1
                            # play_clicked = True
                            self.changeCircles()

                        elif self.face_right_0_rect.collidepoint(pygame.mouse.get_pos()):
                            self.face_0 += 1
                            if self.face_0 == self.num_faces: self.face_0 = 0
                            self.changeCircles()

                        elif self.face_left_0_rect.collidepoint(pygame.mouse.get_pos()):
                            self.face_0 -= 1
                            if self.face_0 == -1: self.face_0 = self.num_faces - 1
                            self.changeCircles()

                        elif self.play_rect.collidepoint(pygame.mouse.get_pos()):
                            play_clicked = True

                        elif self.simulate_rect.collidepoint(pygame.mouse.get_pos()):
                            simulate_clicked = True

                        elif self.l_left_rect.collidepoint(pygame.mouse.get_pos()):
                            if self.c0_count != 1: self.c0_count -= 1

                        elif self.l_right_rect.collidepoint(pygame.mouse.get_pos()):
                            if self.c0_count != 20: self.c0_count += 1

                        elif self.r_left_rect.collidepoint(pygame.mouse.get_pos()):
                            if self.c1_count != 1: self.c1_count -= 1

                        elif self.r_right_rect.collidepoint(pygame.mouse.get_pos()):
                            if self.c1_count != 20: self.c1_count += 1

                        elif self.exit_rect.collidepoint(pygame.mouse.get_pos()):
                            self.close_sound.play()
                            self.exit_clicked = True
                            pygame.mixer.Sound.fadeout(self.menu_music, 1000)

                        if unclick_seed_input:
                            self.seed_input_clicked = False
                            self.seed_input.cursor_visible = False

                if event.type == KEYDOWN:
                    if event.key == 9:
                        self.game_played = not self.game_played

            if simulate_clicked:
                self.screen.blit(self.background, (0, 0))
                self.screen.blit(self.simulating, (1920 / 2 - self.simulating.get_size()[0] / 2, 1080 / 2 - self.simulating.get_size()[1] / 2))
                pygame.display.update()

                circle_0 = circles[self.face_0].copy()
                circle_1 = circles[self.face_1].copy()

                circle_0["color"] = colors[self.color_0]
                circle_0["group_id"] = 0
                circle_0["face_id"] = self.face_0

                circle_1["color"] = colors[self.color_1]
                circle_1["group_id"] = 1
                circle_1["face_id"] = self.face_1

                seed = self.seed_input.value
                if seed == "Seed (optional)":
                    seed = False

                real = False
                print("Simulating game with seed: {}".format(seed))
                self.start_sound.play()
                pygame.mixer.Sound.fadeout(self.menu_music, 1000)
                game = Game(circle_0, self.c0_count, circle_1, self.c1_count, self.screen, seed, real)
                self.stats_surface = game.play_game()
                self.game_played = True

            if play_clicked:
                self.screen.blit(self.background, (0, 0))
                self.screen.blit(self.loading, (1920 / 2 - self.loading.get_size()[0] / 2, 1080 / 2 - self.loading.get_size()[1] / 2))
                pygame.display.update()

                circle_0 = circles[self.face_0].copy()
                circle_1 = circles[self.face_1].copy()

                circle_0["color"] = colors[self.color_0]
                circle_0["group_id"] = 0
                circle_0["face_id"] = self.face_0

                circle_1["color"] = colors[self.color_1]
                circle_1["group_id"] = 1
                circle_1["face_id"] = self.face_1

                seed = self.seed_input.value
                if seed == "Seed (optional)":
                    seed = False
                
                real = True
                print("Playing game with seed: {}".format(seed))
                self.start_sound.play()
                pygame.mixer.Sound.fadeout(self.menu_music, 1000)
                game = Game(circle_0, self.c0_count, circle_1, self.c1_count, self.screen, seed, real)
                self.stats_surface = game.play_game()
                self.game_played = True

            if self.menu_music.get_num_channels() == 0:
                self.menu_music.play(-1)

            self.cursor_rect.center = pygame.mouse.get_pos()
            self.screen.blit(self.cursor, self.cursor_rect)

            if self.exit_clicked:
                self.frames_since_exit_clicked += 1
                if self.frames_since_exit_clicked == 60:
                    running = False

            # limits FPS to 60
            self.clock.tick(60)
            # print(self.clock.get_fps())
    
    def changeCircles(self):
        self.circle_1 = self.circle_images[self.face_0][self.color_0]
        self.circle_2 = self.circle_images[self.face_1][self.color_1]
        self.face_ids = [self.face_0, self.face_1]

        self.c0_count = circles[self.face_0]["team_size"]
        self.c1_count = circles[self.face_1]["team_size"]

    def decodePlayer(self, string):
        tuple = string.split(",")
        return int(tuple[0]), int(tuple[1])

    def encodePlayer(self, tuple):
        return str(tuple[0]) + "," + str(tuple[1])

    def networkPreGame(self):
        self.title_rect.center = (1920 / 2, 150)

        player_request = self.network.getInitRequest()

        # create arrows
        color_right = self.arrow_right
        color_right_rect = color_right.get_rect()
        color_right_rect.center = [500, 750]

        color_left = self.arrow_left
        color_left_rect = color_left.get_rect()
        color_left_rect.center = [400, 750]

        face_right = self.arrow_right
        face_right_rect = face_right.get_rect()
        face_right_rect.center = [500, 800]

        face_left = self.arrow_left
        face_left_rect = face_left.get_rect()
        face_left_rect.center = [400, 800]

        running = True
        ready = False
        while running:
            # DO THE SERVER COMMUNICATIONS
            opponent_request = self.network.send(player_request)

            for event in pygame.event.get():
                if event.type == MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    self.click_sound.play()

                    if self.exit_rect.collidepoint(mouse_pos):
                        self.exit_clicked = True

                    elif color_right_rect.collidepoint(mouse_pos) and not ready:
                        player_request.color_id += 1
                        if player_request.color_id == len(colors): player_request.color_id = 0

                    elif color_left_rect.collidepoint(mouse_pos) and not ready:
                        player_request.color_id -= 1
                        if player_request.color_id == -1: player_request.color_id = len(colors) - 1

                    elif face_right_rect.collidepoint(mouse_pos) and not ready:
                        player_request.face_id += 1
                        if player_request.face_id == self.num_faces: player_request.face_id = 0

                    elif face_left_rect.collidepoint(mouse_pos) and not ready:
                        player_request.face_id -= 1
                        if player_request.face_id == -1: player_request.face_id = self.num_faces - 1

                    elif self.ready_red_rect.collidepoint(mouse_pos):
                        ready = not ready

            pygame.display.flip()
            self.screen.blit(self.background, (0, 0))
            self.screen.blit(self.title, self.title_rect)  
            self.screen.blit(self.exit, self.exit_rect)

            self.screen.blit(color_right, color_right_rect)
            self.screen.blit(color_left, color_left_rect)

            self.screen.blit(face_right, face_right_rect)
            self.screen.blit(face_left, face_left_rect)

            player_circle = self.circle_images[player_request.getFaceId()][player_request.getColorId()]
            player_circle_rect = player_circle.get_rect()
            player_circle_rect.center = (450, 600)

            opponent_circle = self.circle_images[opponent_request.getFaceId()][opponent_request.getColorId()]
            opponent_circle_rect = opponent_circle.get_rect()
            opponent_circle_rect.center = (1470, 600)

            player_stats, opponent_stats = self.createCircleStatsSurfacesNetwork(player_request.getFaceId(), opponent_request.getFaceId())
            player_stats_rect = player_stats.get_rect()
            player_stats_rect.center = (650, 700)
            opponent_stats_rect = opponent_stats.get_rect()
            opponent_stats_rect.center = (1190, 700)

            self.screen.blit(player_circle, player_circle_rect)
            self.screen.blit(opponent_circle, opponent_circle_rect)
            self.screen.blit(player_stats, player_stats_rect)
            self.screen.blit(opponent_stats, opponent_stats_rect)

            self.screen.blit(self.you, self.you_rect)
            self.screen.blit(self.opponent, self.opponent_rect)

            if ready:
                self.screen.blit(self.ready_green, self.ready_green_rect)
            else:
                self.screen.blit(self.ready_red, self.ready_red_rect)

            if self.exit_clicked:
                self.title_rect.center = (1920 / 2, 1080 / 2)
                running = False

            if type(opponent_request.getReady()) != type(True):
                self.screen.blit(self.background, (0, 0))
                self.screen.blit(self.loading, (1920 / 2 - self.loading.get_size()[0] / 2, 1080 / 2 - self.loading.get_size()[1] / 2))
                pygame.display.update()

                circle_0 = circles[player_request.getFaceId()].copy()
                circle_1 = circles[opponent_request.getFaceId()].copy()

                circle_0["color"] = colors[player_request.getColor_id()]
                circle_0["group_id"] = 0
                circle_0["face_id"] = player_request.getFaceId()

                circle_1["color"] = colors[opponent_request.getColorId()]
                circle_1["group_id"] = 1
                circle_1["face_id"] = opponent_request.getFaceId()

                seed = opponent_request.getReady()
                
                real = True
                print("Playing game with seed: {}".format(seed))
                self.start_sound.play()
                pygame.mixer.Sound.fadeout(self.menu_music, 1000)
                game = Game(circle_0, circle_0["team_size"], circle_1, circle_1["team_size"], self.screen, seed, real)
                self.stats_surface = game.play_game()
            
            self.cursor_rect.center = pygame.mouse.get_pos()
            self.screen.blit(self.cursor, self.cursor_rect)
            self.clock.tick(60)

def generateAllCircles():
    print("GENERATING ALL CIRCLES - THIS WILL TAKE A MOMENT ON FIRST RUN\n")
    for color in colors:
        for id in range(0, 5):
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
    screen = pygame.display.set_mode((500,500))  
    done = False  
    while not done:  

        for event in pygame.event.get():  

            if event.type == MOUSEBUTTONDOWN:
                    if event.button == 1:
                        pressed = pygame.key.get_pressed()
                        counter = 0
                        for key in pressed:
                            if key == 1: print(key, ", ", counter)
                            counter += 1

            if event.type == pygame.QUIT:  
                done = True 

        pygame.display.flip()

def main():
    pygame.init()
    pygame.mixer.pre_init(44100, -16, 2, 512)
    pygame.mouse.set_visible(False)
    preGame().show()
    pygame.quit()

# generateAllCircles()
main()
# test()