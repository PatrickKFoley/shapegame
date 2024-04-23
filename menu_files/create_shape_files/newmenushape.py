import pygame, random, math
from game_files.circledata import *

SHRINK_AMOUNT = 0.025

class NewMenuShape(pygame.sprite.Sprite):
    def __init__(self, shape, image_full):
        super().__init__()
        self.image_full =  image_full
        self.shape = shape
        self.r = int(self.shape.radius_max * 1.5)

        self.selected = False
        self.growing = False
        self.shrinking = False
        self.shrink_amount = 2

        self.stats_surface = self.createStatsSurface()
        self.stats_surface_rect = self.stats_surface.get_rect()

        # make them spawn off screen

        self.spawn_angle = random.randint(0, 360)

        self.x = int(self.r + 1920/2 + 1200 * math.cos(math.radians(self.spawn_angle)))
        self.y = int(self.r + 1080/2 + 1200 * math.sin(math.radians(self.spawn_angle)))

        # move them towards the center of the screen
        self.v_x = (self.x - 1920/2) *-1 / 100
        self.v_y = (self.y - 1080/2) *-1 / 100

        

        self.image = pygame.transform.smoothscale(self.image_full, (self.r * 2, self.r * 2))
        self.rect = self.image.get_rect()
        self.rect.center = [self.x, self.y]

        self.on_screen = False

    def createStatsSurface(self):
        font_size = 40
        big_font_size = 50
        title_font_size = offset = 75

        surface = pygame.Surface((500, 500), pygame.SRCALPHA, 32)
        font = pygame.font.Font("backgrounds/font.ttf", font_size)
        font_big = pygame.font.Font("backgrounds/font.ttf", big_font_size)
        font_title = pygame.font.Font("backgrounds/font.ttf", title_font_size)

        title_surface = font_title.render("{} {}".format(self.shape.title, self.shape.name), 1, colors[self.shape.color_id][2])
        title_rect = title_surface.get_rect()
        title_rect.topleft = (300 - title_surface.get_size()[0]/2, 0)


        level_surface = font_big.render("level: " + str(self.shape.level), 1, "white")
        level_rect = level_surface.get_rect()
        level_rect.topright = (297, 0 + offset)

        win_surface = font_big.render("wins: " + str(self.shape.num_wins), 1, "white")
        win_rect = win_surface.get_rect()
        win_rect.topright = (500, 0 + offset)

        surface.blit(title_surface, title_rect)

        surface.blit(level_surface, level_rect)
        surface.blit(win_surface, win_rect)

        keys = ["Velocity:", "Radius:", "Health:", "Damage x:", "Luck:", "Team Size:"]
        keys_for_rects = ["velocity", "radius_min", "radius_max", "health", "dmg_multiplier", "luck", "team_size"]
        values = [str(self.shape.velocity), 
                    str(self.shape.radius_min) + " - " + str(self.shape.radius_max), 
                    str(self.shape.health), str(self.shape.dmg_multiplier), 
                    str(self.shape.luck), str(self.shape.team_size)]
        
        values_separate = [self.shape.velocity, 
                    self.shape.radius_min, self.shape.radius_max, 
                    self.shape.health, self.shape.dmg_multiplier, 
                    self.shape.luck, self.shape.team_size]
        
        line = i = 0
        for value in values_separate:
            if value < circles_unchanged[self.shape.face_id][keys_for_rects[i]]:
                bonus_surface = font.render(str(round(value - circles_unchanged[self.shape.face_id][keys_for_rects[i]], 2)), 1, "red")
            else:
                bonus_surface = font.render("+" + str(round(value - circles_unchanged[self.shape.face_id][keys_for_rects[i]], 2)), 1, "green")
            bonus_rect = bonus_surface.get_rect()

            if keys_for_rects[i] != "radius_min":
                bonus_rect.topright = (500, line * font_size + big_font_size + offset)
                surface.blit(bonus_surface, bonus_rect)
                line += 1
            
            i += 1
        
        i = 0
        for value in values:
            key_text = font.render(keys[i], 1, "white")
            key_text_rect = key_text.get_rect()
            key_text_rect.topright = (250, i * font_size + big_font_size + offset)

            surface.blit(key_text, key_text_rect)

            value_text = font.render(value, 1, "white")
            value_text_rect = value_text.get_rect()
            value_text_rect.topleft = (270, i * font_size + big_font_size + offset)

            surface.blit(value_text, value_text_rect)
            i += 1

        return surface
   
    def select(self):
        self.selected = True
        # self.growing = True
        # self.shrinking = False

    def deselect(self):
        self.selected = False
        # self.growing = False
        # self.shrinking = True

    def update(self):
        # print(self.x, self.y)

        # if they get too far away, move them to center
        if self.x < -200 or self.x > 2120 or self.y < -200 or self.y > 1280:
            self.v_x = (self.x - 1920/2) *-1 / 100
            self.v_y = (self.y - 1080/2) *-1 / 100

        self.move()

        # if self.selected:
        #     if self.growing:
        #         self.shrink_amount -= SHRINK_AMOUNT
        #         self.change_size()

        #         if self.shrink_amount == 0.0:
        #             self.growing = False
        #             self.shrinking = True

        #     else:
        #         self.shrink_amount += SHRINK_AMOUNT
        #         self.change_size()

        #         if self.shrink_amount == 2.0:
        #             self.shrinking = False
        #             self.growing = True

        
        # # if you are no longer selected, but > standard size, shrink
        # else:
        #     if self.shrink_amount != 2:
        #         self.shrink_amount += SHRINK_AMOUNT
        #         self.change_size()

        #         if self.shrink_amount == 2:
        #             self.shrinking = False

    def change_size(self):
        self.r = int(self.r - self.shrink_amount)

        self.image = pygame.transform.smoothscale(self.image_full, (self.r * 2, self.r * 2))
        self.rect = self.image.get_rect()
        self.rect.center = [self.x, self.y]

    def move(self):
        self.x += self.v_x
        self.y += self.v_y

        if 200 < self.x < 1720 and 250 < self.y < 880:
            self.on_screen = True

        if self.on_screen:
            if self.x > 1720:
                self.x = 1720
                self.v_x = -1 * self.v_x

            if self.x < 200:
                self.x = 200
                self.v_x = -1 * self.v_x
            
            if self.y > 880:
                self.y = 880
                self.v_y = -1 * self.v_y

            if self.y < 250:
                self.y = 250
                self.v_y = -1 * self.v_y

        self.rect.center = [self.x, self.y]

    def setVel(self, vel):
        self.v_x = vel[0]
        self.v_y = vel[1]