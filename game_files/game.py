import pygame, random, os, numpy as np, math, time
from pygame.locals import *
from game_files.powerup import Powerup
from game_files.bluelaser import BlueLaser
from game_files.explosion import Explosion
from game_files.clouds import Clouds
from game_files.killfeed import Killfeed
from game_files.circle import Circle
from game_files.circledata import *

class Game: 
    def __init__(self, c0, c1, username_0, username_1, screen, seed = False, real = True, god_mode = False):
        
        # ------------- NECESSARY STUFF ---------
        
        self.real = real
        self.start_real = real
        self.god_mode = god_mode

        if seed != False:
            random.seed(seed)
        
        self.c0 = c0
        self.c1 = c1
        self.circles = [c0, c1]

        self.c0_count = c0["team_size"]
        self.c1_count = c1["team_size"]
        self.circle_counts = [self.c0_count, self.c1_count]

        self.player_0_username = username_0
        self.player_1_username = username_1

        self.p0_win_flag = False
        self.p1_win_flag = False

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

        self.screen_w = 1720
        self.screen_h = 1080
        self.fps = 60
        self.screen = screen
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

        # Groups
        self.powerup_group = pygame.sprite.Group()
        self.laser_group = pygame.sprite.Group()
        self.blue_laser_group = pygame.sprite.Group()
        self.clouds_group = pygame.sprite.Group()
        self.explosions_group = pygame.sprite.Group()
        self.killfeed_group = pygame.sprite.Group()


        # Fixed a bug by swapping the array index on self.circles[]["health"]
        # no clue how that works but it works

        # Max hp of each group
        self.max_hps = [0, 0]
        self.hps = []

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

        if not self.real:
            for i in range(self.circle_counts[0]):
                self.addCircle(0)
            for i in range(self.circle_counts[1]):
                self.addCircle(1)


        # Preprocess images
        self.c0_images = []
        self.c1_images = []
        self.smoke_images = []
        self.explosion_images = []
        self.powerup_images_hud = []
        self.powerup_images_screen = []

        # Defining all these sounds as None allows for easier omission if this game is simulated
        self.death_sounds = self.collision_sounds = self.game_sounds = [None]
        self.choir_sound = self.explosion_sound = self.fuse_sound = self.heal_sound = self.laser_hit_sound = self.laser_sound = self.pop_sound = self.punch_sound = self.shotgun_sound = self.twinkle_sound = self.win_sound = self.wind_sound = self.click_sound = self.close_sound = None

        if not self.real:
            return


        # ------------ MISC PYGAME STUFF --------

        self.cursor = pygame.transform.smoothscale(pygame.image.load("backgrounds/cursor.png"), (12, 12))
        self.cursor_rect = self.cursor.get_rect()
        self.cursor_rect.center = pygame.mouse.get_pos()

        self.hp_mode_surface = pygame.Surface((200, 200), pygame.SRCALPHA, 32)
        self.loading = pygame.image.load("backgrounds/loading.png")

        self.clock = pygame.time.Clock()
        self.background = pygame.image.load("backgrounds/BG1.png")

        self.font = pygame.font.Font("backgrounds/font.ttf", 160)


        # -----------------  IMAGE LOADING -----------------------


        self.player_0_wins, self.player_0_wins_rect = self.createText("{} wins!".format(username_0), 160, self.circles[0]["color"][2])
        self.player_1_wins, self.player_1_wins_rect = self.createText("{} wins!".format(username_1), 160, self.circles[1]["color"][2])
        self.simulating, self.simulating_rect = self.createText("Simulating...", 160, "white")
        self.player_0_wins_rect.center = self.player_1_wins_rect.center = self.simulating_rect.center = [1920 / 2, 1080 / 2]


        # Explosion
        for i in range(1, 8):
            image = pygame.image.load("smoke/explosion{}.png".format(i))
            # image = pygame.transform.smoothscale(image, (int(image.get_size()[0] / 2), int(image.get_size()[1] / 2)))
            self.explosion_images.append(image)

        # Smoke
        for i in range(1, 6):
            image = pygame.image.load("smoke/smoke{}.png".format(i))
            image = pygame.transform.smoothscale(image, (int(image.get_size()[0] / 2), int(image.get_size()[1] / 2)))
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
     
        self.images = [self.c0_images, self.c1_images]

        self.coffin_img = pygame.transform.smoothscale(pygame.image.load("powerups/coffin.png"), (40, 40))

        for powerup in self.powerups:
            image = pygame.image.load(powerup[0])
            self.powerup_images_screen.append(pygame.transform.smoothscale(image, (40, 40)))
            self.powerup_images_hud.append(pygame.transform.smoothscale(image, (20, 20)))

        self.blood_image = pygame.transform.smoothscale(pygame.image.load("powerups/blood.png"), (40, 40))
        self.sword_image = pygame.transform.smoothscale(pygame.image.load("powerups/sword.png"), (40, 40))
        self.blood_image_small = pygame.transform.smoothscale(pygame.image.load("powerups/blood.png"), (30, 30))


        self.exit, self.exit_rect = self.createText("exit", 50)
        self.exit_rect.center = (1870, 1050)

        # Now that images are loaded, add shapes
        for i in range(self.circle_counts[0]):
                self.addCircle(0)
        for i in range(self.circle_counts[1]):
            self.addCircle(1)

        # STUFF THAT IS NOW NECESSARY?

        self.cur_rows = max(len(self.groups[0].sprites()) + len(self.dead_stats[0]), len(self.groups[1].sprites()) + len(self.dead_stats[1]))
        self.stats_surface = pygame.Surface((1710, self.cur_rows * 30 + 215))

        # ------------------- SOUNDS ------------------

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

        # self.game_sounds[random.randint(0, len(self.game_sounds) - 1)].play(-1)

    def play_game(self):
        while self.running:
            self.frames += 1
            # poll for events

            if self.real:
                for event in pygame.event.get():
                    # button click event
                    if event.type == MOUSEBUTTONDOWN:
                        self.playSound(self.click_sound)
                        if event.button == 1:
                            if self.exit_rect.collidepoint(pygame.mouse.get_pos()):
                                self.running = False
                                # self.real = False

                                # # GO THROUGH ALL OTHER OBJECT AND SET REAL = FALSE
                                # for group in self.groups:
                                #     for shape in group:
                                #         shape.real = self.real

                                # for laser in self.laser_group:
                                #     laser.real = self.real

                                # for blue_laser in self.blue_laser_group:
                                #     blue_laser.real = self.real

                                # for killfeed in self.killfeed_group:
                                #     killfeed.kill()

                            elif self.god_mode:
                                self.addCircle(0, pygame.mouse.get_pos(), 0, 0, True)
                                self.createStatsScreen(True)

                        if not self.god_mode:
                            pass
                
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
                        elif self.god_mode:
                            self.spawnPowerup(event.key - 48, pygame.mouse.get_pos())

            if self.real:
                num_rows = max(len(self.groups[0].sprites()) + len(self.dead_stats[0]), len(self.groups[1].sprites()) + len(self.dead_stats[1]))
                if self.cur_rows != num_rows:
                    self.createStatsScreen(True)

            # flip() the display to put your work on screen
            
            if self.real:
                pygame.display.flip()
                self.screen.blit(self.background, (0, 0))
                self.screen.blit(self.exit, self.exit_rect)
                self.screen.blit(self.hp_mode_surface, (self.screen_w + 100, self.screen_h - 100))

            elif not self.real and self.start_real:
                pygame.display.flip()
                self.screen.blit(self.background, (0, 0))
                self.screen.blit(self.simulating, self.simulating_rect)


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

            if self.real:
                pygame.draw.rect(self.screen, "black", (self.fortnite_x, self.fortnite_y, self.screen_w - self.fortnite_x * 2, self.screen_h - self.fortnite_y * 2), 2)

            if len(self.groups[0].sprites()) == 0:
                self.done = True
                self.p1_win_flag = True
                self.fortnite_x_growing = self.fortnite_y_growing = False

                if self.real:
                    self.screen.blit(self.player_1_wins, self.player_1_wins_rect)

            elif len(self.groups[1].sprites()) == 0:
                self.done = True
                self.p0_win_flag = True
                self.fortnite_x_growing = self.fortnite_y_growing = False

                if self.real: 
                    self.screen.blit(self.player_0_wins, self.player_0_wins_rect)
            
            if self.done and self.play_sound and self.real:
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

            if self.real:
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

            

            # limits FPS to 60
            if self.real: 
                self.cursor_rect.center = pygame.mouse.get_pos()
                self.screen.blit(self.cursor, self.cursor_rect)
                self.clock.tick(self.fps)

            if self.done and not self.real:
                # self.createStatsScreen(True)

                if self.p0_win_flag: return 0
                else: return 1

        if self.real:
            # self.close_sound.play()
            # self.screen.blit(self.background, (0, 0))
            # self.screen.blit(self.loading, (1920 / 2 - self.loading.get_size()[0] / 2, 1080 / 2 - self.loading.get_size()[1] / 2))
            # pygame.display.update()
            # time.sleep(0.5)
            self.createStatsScreen(True)
            return self.stats_surface

    def createText(self, text, size, color = "white", font_name = "sitkasmallsitkatextbolditalicsitkasubheadingbolditalicsitkaheadingbolditalicsitkadisplaybolditalicsitkabannerbolditalic"):
        font = pygame.font.Font("backgrounds/font.ttf", size)

        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()

        return text_surface, text_rect

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
                    member.collectPowerup(powerup.getId())
                    powerup.kill()


                    if self.real: 
                        self.playSound(self.pop_sound)
                    
                        if powerup.getId() == 6:
                            self.playSound(self.fuse_sound)
                        elif powerup.getId() == 4:
                            self.playSound(self.wind_sound)
                        elif powerup.getId() == 2:
                            self.playSound(self.twinkle_sound)

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
            if self.real:
                self.blue_laser_group.add(BlueLaser(circle, direction, self.powerup_images_screen[8]))
            else:
                self.blue_laser_group.add(BlueLaser(circle, direction, None, self.real))

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
        if self.real: self.playSound(self.collision_sounds[random.randint(0, len(self.collision_sounds)-1)])

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
            text_rect.topleft = (x - text_obj.get_size()[0] / 2, y)
        else:
            text_rect.topleft = (x, y)

        if not screen:
            self.screen.blit(text_obj, text_rect)
        else:
            screen.blit(text_obj, text_rect)

    def blowupBomb(self, circle, x, y):
        if self.real:
            self.fuse_sound.stop()
            self.explosions_group.add(Explosion(x, y, self.explosion_images, self.screen))
            self.playSound(self.explosion_sound)
        
        circle.stats.useBomb()

        # Deal damage to everyone close to this point
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
        if self.real: self.clouds_group.add(Clouds(killed.x, killed.y, self.smoke_images, self.screen))
        bomb_holder.stats.killPlayer(killed.id)

        self.playSound(self.death_sounds[random.randint(0, len(self.death_sounds)-1)])
        self.addKillfeed(bomb_holder, killed, 6)

        killed.killCircle()

        if 1 in killed.powerups:
            self.memberResurrectMember(killed)

    def addKillfeed(self, right_circle, left_circle, action_id):
        if not self.real: return

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

        if self.real:
            new_circle = Circle(self.circles[g_id], self.id_count[g_id], self, self.images[g_id], self.powerup_images_hud, xy, r, v, new, self.smoke_images)
        else:
            new_circle = Circle(self.circles[g_id], self.id_count[g_id], self, None, None, xy, r, v, new, None, False)

        self.id_count[g_id] += 1
        self.groups[g_id].add(new_circle)

        return new_circle

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
        image = pygame.transform.smoothscale(image, (85, 85))

        self.screen.blit(image, (self.screen_w + 105, 10))
        self.draw_text("x{}".format(len(self.groups[0])), pygame.font.Font("backgrounds/font.ttf", 30), "white", self.screen_w + 147, 105)
        self.draw_text("{}%".format(round((self.hps[0] / self.max_hps[0]) * 100, 1)), pygame.font.Font("backgrounds/font.ttf", 30), "white", self.screen_w + 155, 130)

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
        image = pygame.transform.smoothscale(image, (85, 85))

        offset = self.screen_w / 2 - 100
        self.screen.blit(image, (self.screen_w + 10, 10))
        self.draw_text("x{}".format(len(self.groups[1])), pygame.font.Font("backgrounds/font.ttf", 30), "white", self.screen_w + 52, 105)
        self.draw_text("{}%".format(round((self.hps[1] / self.max_hps[1]) * 100, 1)), pygame.font.Font("backgrounds/font.ttf", 30), "white", self.screen_w + 60, 130)

    def printStat(self, stats, x, y, dead = False):
        font = pygame.font.Font("backgrounds/font.ttf", 30)
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
        if not self.real: return

        # create stats screen image
        num_rows = max(len(self.groups[0].sprites()) + len(self.dead_stats[0]), len(self.groups[1].sprites()) + len(self.dead_stats[1]))
        self.cur_rows = num_rows
        font = pygame.font.Font("backgrounds/font.ttf", 80)

        if first:
            self.stats_surface = pygame.Surface((1710, num_rows * 30 + 215))
            self.stats_surface.set_alpha(220)
            self.stats_surface.fill("darkgray")

            color = self.circles[0]["color"][2]
            self.draw_text("{}".format(self.player_0_username), font, color, 500 + 850 - 10, 50, True, self.stats_surface)

            color = self.circles[1]["color"][2]
            self.draw_text("{}".format(self.player_1_username), font, color, 500 - 10, 50, True, self.stats_surface)

            self.stats_surface.blit(pygame.transform.smoothscale(self.images[0][0], (175, 175)), (30 + 850 - 10, 10))
            self.stats_surface.blit(pygame.transform.smoothscale(self.images[1][0], (175, 175)), (30 - 10, 10))

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
