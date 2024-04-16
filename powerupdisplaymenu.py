import pygame, random, math, numpy as np
from pygame.locals import *
from circledata import *
from shape import Shape
from clickabletext import ClickableText

from menupowerup import MenuPowerup
from clouds import Clouds
from powerupdisplayshape import PowerupDisplayShape
from powerupdisplaypowerup import PowerupDisplayPowerup
from menublacklaser import MenuBlackLaser
from menuredlaser import MenuRedLaser
from menuexplosion import MenuExplosion


class PowerupDisplayMenu():
    def __init__(self, screen, circle_images_full):
        self.screen = screen

        self.powerup_display_shape_group = pygame.sprite.Group()
        self.powerup_display_powerup_group = pygame.sprite.Group()
        self.powerup_display_laser_group = pygame.sprite.Group()
        self.powerup_display_explosion_group = pygame.sprite.Group()
        self.powerup_display_clouds_group = pygame.sprite.Group()

        self.black_laser = pygame.transform.smoothscale(pygame.image.load("powerups/blue_laser.png"), (40, 40))
        self.red_laser = pygame.transform.smoothscale(pygame.image.load("powerups/laser.png"), (40, 40))
        self.explosion_images = []
        self.cloud_images = []

        # Explosion
        for i in range(1, 8):
            image = pygame.image.load("smoke/explosion{}.png".format(i))
            self.explosion_images.append(image)

            # Smoke
        for i in range(1, 6):
            image = pygame.image.load("smoke/smoke{}.png".format(i))
            image = pygame.transform.smoothscale(image, (int(image.get_size()[0] / 2), int(image.get_size()[1] / 2)))
            self.cloud_images.append(image)

        self.powerup_images_hud = []
        self.powerup_info = [
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

        for powerup in self.powerup_info:
            image = pygame.image.load(powerup[0])
            self.powerup_images_hud.append(pygame.transform.smoothscale(image, (20, 20))) 

        self.cursor = pygame.transform.smoothscale(pygame.image.load("backgrounds/cursor.png"), (12, 12))
        self.cursor_rect = self.cursor.get_rect()
        self.cursor_rect.center = pygame.mouse.get_pos()
        self.background = pygame.image.load("backgrounds/BG1.png")
        self.title, self.title_rect = self.createText("shapegame", 150)
        self.title_rect.center = (1920 / 2, 1080 / 2)

        self.loading, self.loading_rect = self.createText("loading playground", 150)
        self.loading_rect.center = (1920 / 2, 1080 / 2)

        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font("backgrounds/font.ttf", 80)

        self.exit_clicked = False

        self.click_sound = pygame.mixer.Sound("sounds/click.wav")
        self.start_sound = pygame.mixer.Sound("sounds/start.wav")
        self.open_sound = pygame.mixer.Sound("sounds/open.wav")
        self.menu_music = pygame.mixer.Sound("sounds/menu.wav")
        self.close_sound = pygame.mixer.Sound("sounds/close.wav")

        self.open_sound.set_volume(.5)
        self.menu_music.set_volume(.5)
        self.close_sound.set_volume(.5)

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

        self.exit_clickable = ClickableText("back", 50, 1870, 1045)

        self.clickables = []
        self.clickables.append(self.exit_clickable)

        self.screen.blit(self.background, (0, 0))
        self.screen.blit(self.loading, self.loading_rect)
        pygame.display.set_caption("shapegame")
        pygame.display.update()

        self.circle_images_full = circle_images_full

    def start(self):
        # make collection of all of the powerups 
        powerups_group = pygame.sprite.Group()
        powerup_names = ["bomb", "cross", "health", "laser", "blue_laser", "muscle", "mushroom", "skull", "speed", "star"]
        add_shape_clickable = ClickableText("add shape!", 50, 140, 1045)

        for id, name in enumerate(powerup_names):
            powerups_group.add(MenuPowerup(name, id))

        name = ""

        while True:
            events = pygame.event.get()
            mouse_pos = pygame.mouse.get_pos()
            selected_powerup_changed = False

            for event in events:
                if event.type == MOUSEBUTTONDOWN:
                    self.playSound(self.click_sound)

                    # determine if a new powerup is to be selected
                    for powerup in powerups_group:
                        if powerup.rect.collidepoint(mouse_pos):
                            name = powerup.getName()
                            selected_powerup_changed = True
                            continue
                    
                    if selected_powerup_changed:
                        for powerup in powerups_group:
                            if powerup.getName() == name: 
                                powerup.select()
                                self.preparePowerupDisplay(name)

                            else: powerup.deselect()

                    elif add_shape_clickable.rect.collidepoint(mouse_pos):
                        self.addPowerupDisplayShape()

                    # if we are exiting
                    elif self.exit_clickable.rect.collidepoint(mouse_pos):
                        self.exit_clicked = True

                    else:
                        self.addPowerupDisplayPowerup(name, mouse_pos)
                    

            # update any on screen elements
            self.exit_clickable.update(mouse_pos)
            add_shape_clickable.update(mouse_pos)

            # draw stuff
            pygame.display.flip()
            self.screen.blit(self.background, (0, 0))
            self.screen.blit(self.title, (1920 / 2 - self.title.get_size()[0] / 2, 1080 / 10 - self.title.get_size()[1] / 2))
            self.screen.blit(self.exit_clickable.surface, self.exit_clickable.rect)
            self.screen.blit(add_shape_clickable.surface, add_shape_clickable.rect)
            if name != "": self.screen.blit(self.powerup_info, self.powerup_info_rect)

            powerups_group.draw(self.screen)
            powerups_group.update()
            self.powerup_display_shape_group.draw(self.screen)
            self.powerup_display_shape_group.update()
            self.powerup_display_powerup_group.draw(self.screen)
            self.powerup_display_powerup_group.update()
            self.powerup_display_laser_group.draw(self.screen)
            self.powerup_display_laser_group.update()
            self.powerup_display_explosion_group.draw(self.screen)
            self.powerup_display_explosion_group.update()
            self.powerup_display_clouds_group.draw(self.screen)
            self.powerup_display_clouds_group.update()
            self.cursor_rect.center = mouse_pos
            self.screen.blit(self.cursor, self.cursor_rect)

            self.checkShapeCollisions()
            self.checkPowerupCollect()

            # exit
            if self.exit_clicked:
                self.powerup_display_shape_group.empty()
                self.powerup_display_powerup_group.empty()
                return
            
            self.clock.tick(60)

    # ALL REQUIRED FUNCTIONS FROM MENU

    def createText(self, text, size, color = "white"):
        font = pygame.font.Font("backgrounds/font.ttf", size)
        

        if type(text) == type("string"):
            text_surface = font.render(text, True, color)
            text_rect = text_surface.get_rect()

            return text_surface, text_rect
        
        elif type(text) == type(["array"]):
            text_surfaces = []
            for element in text:
                text_surfaces.append(font.render(element, True, color))

            max_line_length = max(surface.get_size()[0] for surface in text_surfaces)
            line_height = text_surfaces[0].get_size()[1]

            surface = pygame.Surface((max_line_length, (len(text_surfaces) + 1) * line_height), pygame.SRCALPHA, 32)

            for i, text_surface in enumerate(text_surfaces):
                surface.blit(text_surface, [max_line_length/2 - text_surface.get_size()[0]/2, line_height * (i+1)])

            return surface, surface.get_rect()

    def createShape(self):
        # decrement number of shape tokens

        face_id = random.randint(0, 4)
        color_id = random.randint(0, len(colors)-1)

        base = circles_unchanged[face_id]

        density = base["density"]
        velocity = base["velocity"] + random.randint(-3, 3)
        radius_min = base["radius_min"] + random.randint(-3, 3)
        radius_max = base["radius_max"] + random.randint(-3, 3)
        health = base["health"] + random.randint(-100, 100)
        dmg_multiplier = round(base["dmg_multiplier"] + round((random.randint(-10, 10) / 10), 2), 2)
        luck = round(base["luck"] + round((random.randint(-10, 10) / 10), 2), 2)
        team_size = base["team_size"] + random.randint(-3, 3)

        shape = Shape(-1, face_id, color_id, density, velocity, radius_min, radius_max, health, dmg_multiplier, luck, team_size, "no one")
        return shape

    # ALL POWERUP DISPLAY HELPERS

    def preparePowerupDisplay(self, name):
        powerup_info = {
            "bomb": ["a short moment after collection, a bomb will damage the shapes around it.", "if this explosion kills another shape, the collecting shape will be resurrected!"],
            "cross": ["if a shape with a red cross kills another shape, it will revive a teammate!"],
            "health": ["if a shape with a green cross deals damage, it will heal itself!", "the amount healed is half the shape's maximum health, up to full health."],
            "laser": ["if a shape with a red laser deals damage, it will shoot a laser forward!", "the laser deals 25 damage, hitting each enemy shape at most once."],
            "blue_laser": ["if a shape with a black laser deals damage, it will shoot 8 lasers out in a circle!", "the laser deals 10 damage to each enemy shape hit"],
            "muscle": ["when a muscle is collected, the wielder's next hit will deal 3x damage!", "this effect is lost after the next successful hit."],
            "mushroom": ["when a mushroom is collected, the wielder will grow in size!", "this causes the shape to deal more damage, as its momentum is increased."],
            "skull": ["a skull is an instant kill!", "it guarantees that the wielding shape will win its next collision, and kill the opponent."],
            "speed": ["picking up a speed bonus will increase the shapes speed!", "this causes the shape to deal more damage, as its momentum is increased."],
            "star": ["picking up a star increases the luck of the wielder!", "this makes the wielder more likely to win their next collision.", "this effect is lost after the next unsuccessful hit."]
        }

        self.powerup_info, self.powerup_info_rect = self.createText(powerup_info[name], 40)
        self.powerup_info_rect.center = [1920/2, 400]

    def addPowerupDisplayShape(self, model_shape = False):
        self.playSound(self.pop_sound)

        if model_shape == False:
            shape = self.createShape()
            image = self.circle_images_full[shape.face_id][shape.color_id]

            spawn_angle = random.randint(0, 180)

            x = int(shape.radius_max + 1920/2 + 1200 * math.cos(math.radians(spawn_angle)))
            y = int(shape.radius_max + 1080/2 + 1200 * math.sin(math.radians(spawn_angle)))

            vx = (x - 1920/2) *-1 / 100
            vy = (y - 1080/2) *-1 / 100

            menu_shape = PowerupDisplayShape(shape, image, self.powerup_images_hud, [x, y], [vx, vy])

            self.powerup_display_shape_group.add(menu_shape)
            self.powerup_display_clouds_group.add(Clouds(menu_shape.x, menu_shape.y, self.cloud_images, self.screen, menu_shape))
        else:
            image = self.circle_images_full[model_shape.shape.face_id][model_shape.shape.color_id]

            menu_shape = PowerupDisplayShape(model_shape.shape, image, self.powerup_images_hud, [model_shape.x, model_shape.y], [model_shape.v_x, model_shape.v_y])

            self.powerup_display_shape_group.add(menu_shape)
            self.powerup_display_clouds_group.add(Clouds(menu_shape.x, menu_shape.y, self.cloud_images, self.screen, menu_shape))

    def addPowerupDisplayPowerup(self, name, mouse_pos):
        if name == "": return

        self.playSound(self.pop_sound)

        name_to_id = {
            "skull": 0, 
            "cross": 1,
            "star": 2,
            "muscle": 3,
            "speed": 4,
            "health": 5,
            "bomb": 6,
            "laser": 7,
            "blue_laser": 8,
            "mushroom": 9
        }

        self.powerup_display_powerup_group.add(PowerupDisplayPowerup(name, name_to_id[name], mouse_pos))

    def checkPowerupCollect(self):
        for shape in self.powerup_display_shape_group:
            # good time to check to make explosions
            if shape.bomb_timer == -1:
                shape.bomb_timer = 0
                self.shapeSpawnExplosion(shape)

            for powerup in self.powerup_display_powerup_group:
                dist = math.sqrt( (powerup.x - shape.x)**2 + (powerup.y - shape.y)**2)
                max_dist = shape.r + 10

                if dist <= max_dist:
                    shape.collectPowerup(powerup.id)
                    powerup.kill()

                    if powerup.id == 4:
                        self.playSound(self.wind_sound)
                    elif powerup.id == 2:
                        self.playSound(self.twinkle_sound)
                    elif powerup.id == 6:
                        self.playSound(self.fuse_sound)
                    else:
                        self.playSound(self.pop_sound)

    # ALL SHAPE INTERACTION FUNCTIONS

    def checkShapeCollisions(self):
        for shape1 in self.powerup_display_shape_group.sprites():

            for laser in self.powerup_display_laser_group:
                dist = math.sqrt((shape1.x - laser.x)**2 + (shape1.y - laser.y)**2)
                max_dist = shape1.r + laser.r

                if dist <= max_dist:
                    self.laserHitShape(laser, shape1)

            for s2 in self.powerup_display_shape_group.sprites():
                if shape1 == s2: continue

                dist = math.sqrt( (shape1.x - s2.x)**2 + (shape1.y - s2.y)**2 )
                max_dist = shape1.r + s2.r

                if dist <= max_dist: self.collideShapes(shape1, s2, True)

    def collideShapes(self, s1, s2, damage = False):
        self.playSound(self.collision_sounds[random.randint(0, len(self.collision_sounds)-1)])

        if damage:
            # check if either shapes have instant kill, and should win collision
            if 0 in s1.powerups and 0 in s2.powerups:
                pass
            elif 0 in s1.powerups:
                self.shapeDamageShape(s1, s2)
            elif 0 in s2.powerups:
                self.shapeDamageShape(s2, s1)

            else:
                roll_1 = random.randint(1, 20) + s1.luck
                roll_2 = random.randint(1, 20) + s2.luck

                if roll_1 > roll_2:
                    self.shapeDamageShape(s1, s2)
                else:
                    self.shapeDamageShape(s2, s1)

        s1.x -= s1.v_x
        s1.y -= s1.v_y
        s2.x -= s2.v_x
        s2.y -= s2.v_y

        # STEP 1

        [x2, y2] = [s2.x, s2.y]
        [x1, y1] = [s1.x, s1.y]

        norm_vec = np.array([x2 - x1, y2 - y1])

        divisor = math.sqrt(norm_vec[0]**2 + norm_vec[1]**2)
        unit_vec = np.array([norm_vec[0] / divisor, norm_vec[1] / divisor])

        unit_tan_vec = np.array([-1 * unit_vec[1], unit_vec[0]])

        # STEP 2

        v1 = np.array([s1.v_x, s1.v_y])
        m1 = 10

        v2 = np.array([s2.v_x, s2.v_y])
        m2 = 10

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
        s1.setVel(v1p)

        v2p = v2np_ + v2tp_
        s2.setVel(v2p)
    
    def shapeInstaKillShape(self, winner, loser):
        self.playSound(self.shotgun_sound)

        loser_resurrect = False

        # check if dead loser has resurrect
        if 1 in loser.powerups:
            self.shapeResurrectShape(loser)
            loser_resurrect = True

        if not loser_resurrect:
            self.createCloudsAt(loser.x, loser.y)

        # remove powerups, kill shape
        winner.removePowerup(0)
        loser.killShape()

        return loser_resurrect

    def shapeResurrectShape(self, god, dead_circle = False):
        self.playSound(self.choir_sound)
        
        if dead_circle == False:
            new_circle_before = god
        else:
            new_circle_before = dead_circle

        r = new_circle_before.shape.radius_min
        new_circle_before.shape = god.shape
        new_circle_before.shape.radius_min = r


        self.addPowerupDisplayShape(new_circle_before)
        return True

    def shapeKillShape(self, winner, loser):
        self.playSound(self.death_sounds[random.randint(0, len(self.death_sounds)-1)])

        loser_resurrect = False

        if 1 in loser.powerups:
            loser_resurrect = self.shapeResurrectShape(loser)

        return loser_resurrect

    def shapeSpawnBlackLaser(self, shape):
        self.playSound(self.laser_sound)

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
            self.powerup_display_laser_group.add(MenuBlackLaser(shape, direction, self.black_laser))

    def shapeSpawnRedLaser(self, shape):
        self.playSound(self.laser_sound)

        self.powerup_display_laser_group.add(MenuRedLaser(shape, self.red_laser))

    def bombKillShape(self, shape):
        if 1 in shape.powerups:
            self.shapeResurrectShape(shape)
        else:
            self.createCloudsAt(shape.x, shape.y)

        shape.killShape()

    def shapeSpawnExplosion(self, shape):
        self.playSound(self.explosion_sound)

        explosion = MenuExplosion(shape.x, shape.y, self.explosion_images)
        num_kills = 0

        # damage shapes
        for other_shape in self.powerup_display_shape_group:
            dist = math.sqrt( (explosion.x - other_shape.x)**2 + (explosion.y - other_shape.y)**2)

            if dist <= explosion.damage:
                other_shape.takeDamage(explosion.damage - dist)

            if other_shape.hp <= 0:
                self.bombKillShape(shape)
                num_kills += 1

        if num_kills >= 2 and 1 not in shape.powerups:
            self.shapeResurrectShape(shape)

        self.powerup_display_explosion_group.add(explosion)

    def shapeDamageShape(self, winner, loser):
        loser_died = False
        loser_resurrect = 1 in loser.powerups

        if 0 in winner.powerups:
            loser_resurrect = self.shapeInstaKillShape(winner, loser)

            if 1 in winner.powerups and not loser_resurrect:
                # winner resurrects loser
                self.shapeResurrectShape(winner, loser)
                
            return

        else:
            loser_died = loser.takeDamage(winner.getAttack())


        if loser.hp <= 0:
            loser_resurrect = self.shapeKillShape(winner, loser)

            if 1 in winner.powerups and not loser_resurrect:
                self.shapeResurrectShape(winner, loser)

         # Determine if any powerups were used for stats
        # Clear winner of any powerups they should win
        if 3 in winner.powerups:
            winner.removePowerup(3)
            self.playSound(self.punch_sound)
        if 4 in winner.powerups:
            winner.removePowerup(4)
        if 5 in winner.powerups:
            winner.removePowerup(5)
            self.playSound(self.heal_sound)
        if 6 in winner.powerups:
            winner.removePowerup(6)
            self.shapeSpawnExplosion(winner)
        if 7 in winner.powerups:
            winner.removePowerup(7)
            self.shapeSpawnRedLaser(winner)
        elif 8 in winner.powerups:
            winner.removePowerup(8)
            # Will switch real brains of each removePowerup call to be done by Game, starting with this
            self.shapeSpawnBlackLaser(winner)
            

        if 2 in loser.powerups:
            loser.removePowerup(2)


        if loser.hp <= 0:
            self.createCloudsAt(loser.x, loser.y)

            return 1
        else:
            return 0
        
        winner.constructSurface()
        loser.constructSurface()

    def createCloudsAt(self, x, y):
        self.powerup_display_clouds_group.add(Clouds(x, y, self.cloud_images, self.screen))

    def laserHitShape(self, laser, shape):
        if not shape in laser.shapes_collided_with:
            self.playSound(self.laser_hit_sound)

            laser.shapes_collided_with.append(shape)

            shape.takeDamage(laser.damage)

            if shape.hp <= 0:
                resurrect = self.shapeKillShape(laser.shape, shape)

                # TODO: don't let new shape be hit?

                if 1 in laser.shape.powerups and not resurrect:
                    self.shapeResurrectShape(laser.shape, shape)

    def playSound(self, sound):
        if sound.get_num_channels() <= 1:
            sound.play()

            if sound == self.wind_sound:
                pygame.mixer.Sound.fadeout(sound, 1500)
            elif sound == self.choir_sound:
                pygame.mixer.Sound.fadeout(sound, 1000)
            elif sound == self.fuse_sound:
                sound.play(9)
            elif sound == self.explosion_sound:
                self.fuse_sound.stop()