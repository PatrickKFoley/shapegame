import pygame, random, math, numpy as np
from pygame.locals import *
from menu_files.create_shape_files.newmenushape import NewMenuShape
from game_files.circledata import *
from server_files.database_user import User
from server_files.database_shape import Shape
from threading import Thread
from screen_elements.clickabletext import ClickableText

class CreateShapeMenu():
    def __init__(self, screen, user, shapes, session, circle_images_full):

        self.network = None
        self.user = user
        self.shapes = shapes
        self.screen = screen
        self.session = session

        self.new_shapes_group = pygame.sprite.Group()

        self.cursor = pygame.transform.smoothscale(pygame.image.load("backgrounds/cursor.png"), (12, 12))
        self.cursor_rect = self.cursor.get_rect()
        self.cursor_rect.center = pygame.mouse.get_pos()
        self.background = pygame.image.load("backgrounds/BG1.png")
        self.title, x = self.createText("shapegame", 150)
        self.title_rect = self.title.get_rect()
        self.title_rect.center = (1920 / 2, 1080 / 2)
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font("backgrounds/font.ttf", 80)

 
        self.exit_clicked = False


        self.click_sound = pygame.mixer.Sound("sounds/click.wav")
        self.close_sound = pygame.mixer.Sound("sounds/close.wav")
        self.close_sound.set_volume(.5)

        self.create_shape, self.create_shape_rect = self.createText("create a new shape!", 150)
        self.logged_in_as, self.logged_in_as_rect = self.createText("logged in as: " + self.user.username, 35)
        self.logged_in_as_rect.topright = (1900, 10)
        self.create_shape_rect.center = [1920/2, 90]
        self.exit_clickable = ClickableText("exit", 50, 1870, 1045)
        self.go_to_collections_clickable = ClickableText("go to collections", 40, 450, 1045)
        self.create_clickable = ClickableText("create!", 50, 1920/2, 1000)

        self.clickables = []
        self.clickables.append(self.exit_clickable)
        self.clickables.append(self.go_to_collections_clickable)
        self.clickables.append(self.create_clickable)

        self.screen.blit(self.background, (0, 0))
        self.screen.blit(self.title, self.title_rect)
        pygame.display.update()


        self.circle_images_full = circle_images_full
        self.circle_images_larger = []

    def start(self):
        newest_stats = None
        shape_tokens_remaining, shape_tokens_remaining_rect = self.createText("shape tokens: " + str(self.user.shape_tokens), 35)
        shape_tokens_remaining_rect.topleft = [10, 1030]

        while True:
            events = pygame.event.get()
            mouse_pos = pygame.mouse.get_pos()

            # handle inputs
            for event in events:
                if event.type == MOUSEBUTTONDOWN: 
                    self.click_sound.play()

                    # deselect all new shapes
                    for shape in self.new_shapes_group:
                        shape.deselect()

                    # if we click on a shape we want to see that shape's stats
                    for shape in self.new_shapes_group:
                        if shape.rect.collidepoint(mouse_pos):
                            newest_stats = shape.stats_surface
                            shape.select()

                    # if we are exiting
                    if self.exit_clickable.rect.collidepoint(mouse_pos):
                        self.exit_clicked = True

                    elif self.go_to_collections_clickable.rect.collidepoint(mouse_pos):
                        return "COLLECTIONS"

                    elif self.create_clickable.rect.collidepoint(mouse_pos) and self.user.shape_tokens != 0:
                        # create new shape, add to db
                        new_shape = self.createShape(self.user.id)
                        new_menu_shape = NewMenuShape(new_shape, self.circle_images_full[new_shape.face_id][new_shape.color_id])
                        newest_stats = new_menu_shape.stats_surface

                        # rewrite number of tokens remaining
                        shape_tokens_remaining, shape_tokens_remaining_rect = self.createText("shape tokens: " + str(self.user.shape_tokens), 35)
                        shape_tokens_remaining_rect.topleft = [10, 1030]
                        
                        # add to user's collection group
                        self.shapes.append(new_shape)
                        self.new_shapes_group.add(new_menu_shape)

            self.screen.blit(self.background, (0, 0))
            self.new_shapes_group.draw(self.screen)
            # draw things
            
            self.new_shapes_group.update()
            self.checkShapeCollisions(self.new_shapes_group)

            if newest_stats != None:
                self.screen.blit(newest_stats, [-50, 700])
            
            
            self.screen.blit(self.create_shape, self.create_shape_rect)
            self.screen.blit(self.exit_clickable.surface, self.exit_clickable.rect)
            self.screen.blit(self.go_to_collections_clickable.surface, self.go_to_collections_clickable.rect)
            self.screen.blit(shape_tokens_remaining, shape_tokens_remaining_rect)
            self.screen.blit(self.logged_in_as, self.logged_in_as_rect)

            if self.user.shape_tokens != 0:
                self.screen.blit(self.create_clickable.surface, self.create_clickable.rect)

            self.cursor_rect.center = mouse_pos
            self.screen.blit(self.cursor, self.cursor_rect)


            # update any on screen elements
            self.exit_clickable.update(mouse_pos)
            self.create_clickable.update(mouse_pos)
            self.go_to_collections_clickable.update(mouse_pos)

            pygame.display.flip()

            # exit
            if self.exit_clicked:
                # delete all new shapes
                self.new_shapes_group.empty()

                return "NONE"
                
            self.clock.tick(60)

    # HELPERS

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

    # FUNCTIONS

    def commitShape(self, shape):
        self.session.query(User).filter(User.id == self.user.id).update({'shape_tokens': User.shape_tokens -1})
        self.session.add(shape)
        self.session.commit()

    def createShape(self, owner_id = -1):
        # decrement number of shape tokens
        face_id = random.randint(0, 4)
        color_id = random.randint(0, len(colors)-1)

        base = circles_unchanged[face_id]

        density = base["density"]
        velocity = base["velocity"] + random.randint(0, 3)
        radius_min = base["radius_min"] + random.randint(-3, 3)
        radius_max = base["radius_max"] + random.randint(-3, 3)
        health = base["health"] + random.randint(-100, 100)
        dmg_multiplier = round(base["dmg_multiplier"] + (random.randint(-10, 10) / 10), 2)
        luck = round(base["luck"] + (random.randint(-10, 10) / 10), 2)
        team_size = base["team_size"] + random.randint(-3, 3)

        # DON'T LET RAD_MIN > RAD_MAX
        while radius_min >= radius_max:
            radius_min = base["radius_min"] + random.randint(-3, 3)
            radius_max = base["radius_max"] + random.randint(-3, 3)

        # DON'T LET DMGX == 0
        while dmg_multiplier == 0.0:
            dmg_multiplier = round(base["dmg_multiplier"] + (random.randint(-10, 10) / 10), 2)

        if owner_id != -1:
            try:
                shape = Shape(owner_id, face_id, color_id, density, velocity, radius_min, radius_max, health, dmg_multiplier, luck, team_size, self.user.username)
                
                thread = Thread(target=self.commitShape(shape))
                thread.start()
                # thread.join()

                return shape
            except:
                self.session.rollback()
                return False
        else:
            shape = Shape(owner_id, face_id, color_id, density, velocity, radius_min, radius_max, health, dmg_multiplier, luck, team_size, "no one")
            return shape

    def checkShapeCollisions(self, group, damage = False):
        for s1 in group.sprites():
            for s2 in group.sprites():
                if s1 == s2: continue

                dist = math.sqrt( (s1.x - s2.x)**2 + (s1.y - s2.y)**2 )
                max_dist = s1.r + s2.r

                if dist <= max_dist: self.collideShapes(s1, s2, damage)

    def collideShapes(self, s1, s2, damage = False):
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
