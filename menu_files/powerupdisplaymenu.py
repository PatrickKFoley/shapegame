from pygame import Surface
import pygame, random, math, numpy as np
from pygame.locals import *
from pygame.mixer import Sound
from game_files.circledata import *
from server_files.database_classes import Shape
from screen_elements.clickabletext import ClickableText
from screen_elements.text import Text

from menu_files.powerup_display_files.menupowerup import MenuPowerup
from game_files.clouds import Clouds
from menu_files.powerup_display_files.powerupdisplayshape import PowerupDisplayShape
from menu_files.powerup_display_files.powerupdisplaypowerup import PowerupDisplayPowerup
from menu_files.powerup_display_files.menublacklaser import MenuBlackLaser
from menu_files.powerup_display_files.menuredlaser import MenuRedLaser
from menu_files.powerup_display_files.menuexplosion import MenuExplosion
from shared_functions import *


class PowerupDisplayMenu():
    def __init__(self, screen: Surface, circle_images_full: list[list[Surface]]):
        # required parameters from menu
        self.screen = screen
        self.circle_images_full = circle_images_full

        # create text elements
        self.powerup_text: Text | None = None
        self.title_text = Text("shapegame", 150, 1920/2, 1080/10)
        self.loading_text = Text("loading playground", 150, 1920/2, 1080/2)
        self.add_shape_clickable = ClickableText("add shape!", 50, 140, 1045)
        self.exit_clickable = ClickableText("back", 50, 1870, 1045)

        self.clickables: list[ClickableText] = []
        self.clickables.append(self.exit_clickable)
        self.clickables.append(self.add_shape_clickable)

        # load background, create and center cursor
        self.background = pygame.image.load("backgrounds/BG1.png")
        self.cursor = pygame.transform.smoothscale(pygame.image.load("backgrounds/cursor.png"), (12, 12))
        self.cursor_rect = self.cursor.get_rect()
        self.cursor_rect.center = pygame.mouse.get_pos()

        # update display
        self.screen.blit(self.background, (0, 0))
        self.screen.blit(self.loading_text.surface, self.loading_text.rect)
        pygame.display.update()

        # pygame requirements
        self.clock = pygame.time.Clock()
        self.selected_powerup_changed = False
        self.exit_clicked = False

        # Sprite groups for shapes, powerups and animations
        self.hud_powerup_group = pygame.sprite.Group()
        self.powerup_display_shape_group = pygame.sprite.Group()
        self.powerup_display_powerup_group = pygame.sprite.Group()
        self.powerup_display_laser_group = pygame.sprite.Group()
        self.powerup_display_explosion_group = pygame.sprite.Group()
        self.powerup_display_clouds_group = pygame.sprite.Group()
        
        # this will make updating the groups easier
        self.groups: list[pygame.sprite.Group] = [
            self.hud_powerup_group,
            self.powerup_display_shape_group,
            self.powerup_display_powerup_group,
            self.powerup_display_laser_group,
            self.powerup_display_explosion_group,
            self.powerup_display_clouds_group
        ]

        # create containers for "animations" and powerups
        self.explosion_images: list[Surface] = []
        self.cloud_images: list[Surface] = []
        self.powerup_images_hud: list[Surface]= []

        # load explosion images
        for i in range(1, 8):
            image = pygame.image.load("smoke/explosion{}.png".format(i))
            self.explosion_images.append(image)

        # load smoke images
        for i in range(1, 6):
            image = pygame.image.load("smoke/smoke{}.png".format(i))
            image = pygame.transform.smoothscale(image, (int(image.get_size()[0] / 2), int(image.get_size()[1] / 2)))
            self.cloud_images.append(image)

        # info required for powerups (from game)
        self.powerup_names = ["bomb", "cross", "health", "laser", "blue_laser", "muscle", "mushroom", "skull", "speed", "star"]

        self.powerup_paths = [
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
        
        self.powerup_blurbs = {
            "": "",
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

        # create text blurb for display
        self.selected_powerup_name = ""
        self.powerup_text = Text(self.powerup_blurbs[self.selected_powerup_name], 40, 1920/2, 400)

        # populate the hud powerup group
        for id, name in enumerate(self.powerup_names):
            self.hud_powerup_group.add(MenuPowerup(name, id))

        # load powerup images
        for powerup in self.powerup_paths:
            image = pygame.image.load(powerup[0])
            self.powerup_images_hud.append(pygame.transform.smoothscale(image, (20, 20)))

        # load laser images
        self.black_laser = pygame.transform.smoothscale(pygame.image.load("powerups/blue_laser.png"), (40, 40))
        self.red_laser = pygame.transform.smoothscale(pygame.image.load("powerups/laser.png"), (40, 40))

        # load all Sounds
        self.click_sound = pygame.mixer.Sound("sounds/click.wav")
        self.start_sound = pygame.mixer.Sound("sounds/start.wav")
        self.open_sound = pygame.mixer.Sound("sounds/open.wav")
        self.menu_music = pygame.mixer.Sound("sounds/menu.wav")
        self.close_sound = pygame.mixer.Sound("sounds/close.wav")

        self.death_sounds: list[Sound] = []
        self.death_sounds.append(pygame.mixer.Sound("sounds/death/1.wav"))
        self.death_sounds.append(pygame.mixer.Sound("sounds/death/2.wav"))
        self.death_sounds.append(pygame.mixer.Sound("sounds/death/3.wav"))
        self.death_sounds.append(pygame.mixer.Sound("sounds/death/4.wav"))

        self.collision_sounds: list[Sound] = []
        self.collision_sounds.append(pygame.mixer.Sound("sounds/collisions/clink1.wav"))
        self.collision_sounds.append(pygame.mixer.Sound("sounds/collisions/clink2.wav"))
        self.collision_sounds.append(pygame.mixer.Sound("sounds/collisions/thud2.wav"))

        self.game_sounds: list[Sound] = []
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

        # lower volume of certain sounds
        self.open_sound.set_volume(.5)
        self.menu_music.set_volume(.5)
        self.close_sound.set_volume(.5)
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

    def start(self):
        while True:
            self.selected_powerup_changed = False

            self.handleInputs()
            self.updateAndDraw()
                
            # exit
            if self.exit_clicked:
                self.powerup_display_shape_group.empty()
                self.powerup_display_powerup_group.empty()
                return
            
            self.clock.tick(60)

    def handleInputs(self):
        # get events and mouse position
        events = pygame.event.get()
        mouse_pos = pygame.mouse.get_pos()

        # loop through all events
        for event in events:
            if event.type == MOUSEBUTTONDOWN:
                self.playSound(self.click_sound)

                # determine if a new powerup is to be selected
                for powerup in self.hud_powerup_group:
                    if powerup.rect.collidepoint(mouse_pos):
                        self.selected_powerup_name = powerup.getName()
                        self.selected_powerup_changed = True
                        continue
                
                # alter the displayed text, select the correct powerup
                if self.selected_powerup_changed:
                    for powerup in self.hud_powerup_group:
                        if powerup.getName() == self.selected_powerup_name: 
                            powerup.select()
                            self.powerup_text = Text(self.powerup_blurbs[self.selected_powerup_name], 40, 1920/2, 400)

                        else: powerup.deselect()

                # if the add shape button is clicked
                elif self.add_shape_clickable.rect.collidepoint(mouse_pos):
                    self.addPowerupDisplayShape()

                # if we are exiting
                elif self.exit_clickable.rect.collidepoint(mouse_pos):
                    self.exit_clicked = True

                # else, add a powerup
                else:
                    self.addPowerupDisplayPowerup(self.selected_powerup_name, mouse_pos)

    def updateAndDraw(self):
        # update and draw all on screen elements

        # get mouse position
        mouse_pos = pygame.mouse.get_pos()
        
        # flip display and draw background elements
        pygame.display.flip()
        self.screen.blit(self.background, (0, 0))
        self.screen.blit(self.title_text.surface, self.title_text.rect)
        if self.selected_powerup_name != "": self.screen.blit(self.powerup_text.surface, self.powerup_text.rect)

        # update and draw any on screen elements
        for clickable in self.clickables:
            clickable.update(mouse_pos)
            self.screen.blit(clickable.surface, clickable.rect)

        # update and draw all groups
        for group in self.groups:
            group.update()
            group.draw(self.screen)

        # center and draw cursor
        self.cursor_rect.center = mouse_pos
        self.screen.blit(self.cursor, self.cursor_rect)

        # check for collisions between powerups and shapes
        self.checkShapeCollisions()
        self.checkPowerupCollect()

    # ALL POWERUP DISPLAY HELPERS

    def addPowerupDisplayShape(self, model_shape = False):
        self.playSound(self.pop_sound)

        if model_shape == False:
            shape = createShape()
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

    def addPowerupDisplayPowerup(self, selected_powerup_name, mouse_pos):
        if selected_powerup_name == "": return

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

        self.powerup_display_powerup_group.add(PowerupDisplayPowerup(selected_powerup_name, name_to_id[selected_powerup_name], mouse_pos))

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