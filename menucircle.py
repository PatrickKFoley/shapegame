import pygame
from circledata import *

class MenuShape(pygame.sprite.Sprite):
    def __init__(self, id, shape, num_shapes, mode = "PLAYER", selected = False):
        self.id = id
        super().__init__()
        self.image_full =  pygame.image.load("circles/{}/{}/0.png".format(shape.face_id, colors[shape.color_id][0]))
        self.num_shapes = min(num_shapes + 1, 6)
        self.x = id  * 1920 / self.num_shapes
        self.mode = mode

        if mode == "COLLECTIONS":
            self.y = 500
        elif mode == "OPPONENT":
            self.y = 300
        else:
            self.y = 600

        self.next_x = self.x

        self.shape = shape
        self.selected = selected

        self.stats_surface = self.createStatsSurface()
        self.stats_surface_rect = self.stats_surface.get_rect()

        if mode == "COLLECTIONS":
            self.stats_surface_rect.center = [1920 / 2 - 50, 1000]
        elif mode == "OPPONENT":
            self.stats_surface_rect.center = [1920 / 2 + 500, 1050]
        else:
            self.stats_surface_rect.center = [1920 / 2 - 500, 1050]

        if mode == "COLLECTIONS":
            self.small_r = 180
            self.large_r = 280
        elif mode == "OPPONENT":
            self.small_r = 140
            self.large_r = 210
        else:
            self.small_r = 180
            self.large_r = 280

        if selected:
            self.image = pygame.transform.scale(self.image_full, (self.large_r, self.large_r))
            self.r = self.large_r
        else:
            self.image = pygame.transform.scale(self.image_full, (self.small_r, self.small_r))
            self.r = self.small_r
        self.next_r = self.r

        self.rect = self.image.get_rect()
        self.rect.center = [self.x, self.y]

    def createStatsSurface(self):
        if self.mode == "PLAYER" or self.mode == "OPPONENT":
            font_size = 35
        else:
            font_size = 40

        surface = pygame.Surface((500, 500), pygame.SRCALPHA, 32)
        font = pygame.font.Font("backgrounds/font.ttf", font_size)

        keys = ["Density:", "Velocity:", "Radius:", "Health:", "Damage x:", "Luck:", "Team Size:"]
        keys_for_rects = ["density", "velocity", "radius_min", "radius_max", "health", "dmg_multiplier", "luck", "team_size"]
        values = [str(self.shape.density), str(self.shape.velocity), 
                    str(self.shape.radius_min) + " - " + str(self.shape.radius_max), 
                    str(self.shape.health), str(self.shape.dmg_multiplier), 
                    str(self.shape.luck), str(self.shape.team_size)]
        
        values_separate = [self.shape.density, self.shape.velocity, 
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
                bonus_rect.topright = (500, line * font_size)
                surface.blit(bonus_surface, bonus_rect)
                line += 1
            
            i += 1
        
        i = 0
        for value in values:
            key_text = font.render(keys[i], 1, "white")
            key_text_rect = key_text.get_rect()
            key_text_rect.topright = (250, i * font_size)

            surface.blit(key_text, key_text_rect)

            value_text = font.render(value, 1, "white")
            value_text_rect = value_text.get_rect()
            value_text_rect.topleft = (270, i * font_size)

            surface.blit(value_text, value_text_rect)
            i += 1

        return surface

    def moveLeft(self):
        self.next_x -= 1920 / self.num_shapes

    def moveRight(self):
        self.next_x += 1920 / self.num_shapes
    
    def toggleSelected(self):
        self.selected = not self.selected

        if self.r == self.small_r:
            self.next_r = self.large_r
        elif self.r == self.large_r:
            self.next_r = self.small_r

    def goHome(self):
        self.x = self.id  * 1920 / self.num_shapes

    def disable(self):
        if not self.selected: return

        self.selected = False
        self.next_r = self.small_r

    def select(self):
        self.selected = True
        self.next_r = self.large_r

    def update(self, screen):
        if self.r > self.next_r:
            self.r -= 10
            self.image = pygame.transform.scale(self.image_full, (self.r, self.r))

            self.rect = self.image.get_rect()
            self.rect.center = [self.x, self.y]
        elif self.r < self.next_r:
            self.r += 10
            self.image = pygame.transform.scale(self.image_full, (self.r, self.r))

            self.rect = self.image.get_rect()
            self.rect.center = [self.x, self.y]

        if self.x > self.next_x:
            self.x -= 20
            self.rect.center = [self.x, self.y]
        elif self.x < self.next_x:
            self.x += 20
            self.rect.center = [self.x, self.y]

        if self.selected:
            screen.blit(self.stats_surface, self.stats_surface_rect)

        

