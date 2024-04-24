import pygame, datetime, pytz
from server_files.database_shape import Shape
from sqlalchemy import func
from game_files.circledata import *

OFFSET = -35

class MenuShape(pygame.sprite.Sprite):
    def __init__(self, id, shape, image_full, num_shapes, mode = "PLAYER", selected = False, session = False):
        self.id = id
        super().__init__()
        self.image_full = image_full
        self.num_shapes = min(num_shapes + 1, 6)
        self.x = id  * 1920 / self.num_shapes
        self.mode = mode
        self.session = session

        if mode == "COLLECTIONS":
            self.y = 500 - 25
        elif mode == "OPPONENT":
            self.y = 300  - 35 -25
        else:
            self.y = 600  - 35 -25

        self.next_x = self.x

        self.shape = shape
        self.selected = selected

        self.stats_surface = self.createStatsSurface()
        self.stats_surface_rect = self.stats_surface.get_rect()

        if mode == "COLLECTIONS":
            self.stats_surface_rect.center = [1920 / 2 - 35, 1000 -50]
        elif mode == "OPPONENT":
            self.stats_surface_rect.center = [1920 / 2 + 480, 1050 + OFFSET - 45]
        else:
            self.stats_surface_rect.center = [1920 / 2 - 600, 1050 + OFFSET - 45]

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
            width = 500
        else:
            font_size = 40
            width = 1000

        big_font_size = 40
        title_font_size = offset = 75



        surface = pygame.Surface((width, 500), pygame.SRCALPHA, 32)
        font = pygame.font.Font("backgrounds/font.ttf", font_size)
        font_big = pygame.font.Font("backgrounds/font.ttf", big_font_size)
        font_title = pygame.font.Font("backgrounds/font.ttf", title_font_size)

        title_surface = font_title.render("{} {}".format(self.shape.title, self.shape.name), 1, colors[self.shape.color_id][2])
        title_rect = title_surface.get_rect()
        title_rect.topleft = (width/2 + 30 - title_surface.get_size()[0]/2, 0)

        if self.mode == "PLAYER" or self.mode == "OPPONENT":
            title_rect.topleft = (width/2 + 50 - title_surface.get_size()[0]/2, 0)

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

        # Add a line for how long the owner has owned the shape

        if self.mode == "PLAYER" or self.mode == "OPPONENT":
            time_owned = str(datetime.datetime.utcnow() - self.shape.obtained_on)

            if "day" not in time_owned:
                time_owned = (time_owned.split(".")[0]).split(":")
                days = int(int(time_owned[0]) // 24)
                hours = int(int(time_owned[0]) % 24)
                minutes = int(time_owned[1])

            else:
                days = int(time_owned.split(" ")[0])
                hours = int(time_owned.split(" ")[2].split(":")[0])
                minutes = hours = int(time_owned.split(" ")[2].split(":")[1])

            time_owned_str = "time owned:"
            time_owned_surface, time_owned_rect = self.createText(time_owned_str, font_size)
            time_owned_rect.topright = (250, i * font_size + big_font_size + offset)

            date_str = "{}d, {}h, {}m".format(days, hours, minutes)
            date_surface, date_rect = self.createText(date_str, font_size)
            date_rect.topleft = (270, i * font_size + big_font_size + offset)

            surface.blit(time_owned_surface, time_owned_rect)
            surface.blit(date_surface, date_rect)

        # Draw on the right side of the screen

        if self.session != False:
            count = self.session.query(func.count(Shape.id)).filter(Shape.face_id == self.shape.face_id, Shape.color_id == self.shape.color_id).scalar()
        else: count = 0

        utc_timezone = pytz.timezone('UTC')
        est_timezone = pytz.timezone('US/Eastern')

        obtained_on_datetime = utc_timezone.localize(self.shape.obtained_on).astimezone(est_timezone)
        created_on_datetime = utc_timezone.localize(self.shape.created_on).astimezone(est_timezone)

        obtained_on_str = ["obtained on: ", "{}".format(obtained_on_datetime.strftime("%m/%d/%Y, %H:%M"))]
        created_on_surface, created_on_rect = self.createText(obtained_on_str, font_size - 5)
        surface.blit(created_on_surface, [750 - created_on_surface.get_size()[0]/2, -25 + offset])

        created_on_str = ["created on: ", "{}".format(created_on_datetime.strftime("%m/%d/%Y, %H:%M"))]
        created_surface, created_rect = self.createText(created_on_str, font_size - 5)
        surface.blit(created_surface, [750 - created_surface.get_size()[0]/2, 45 + offset])

        num_owners_str = "number of owners: {}".format(self.shape.num_owners)
        num_owners_surface, num_owners_rect = self.createText(num_owners_str, font_size - 5)
        surface.blit(num_owners_surface, [750 - num_owners_surface.get_size()[0]/2, 160 + offset])

        created_by_str = "created by: {}".format(self.shape.created_by)
        created_by_surface, created_by_rect = self.createText(created_by_str, font_size - 5)
        surface.blit(created_by_surface, [750 - created_by_surface.get_size()[0]/2, 205 + offset])

        rarity_str = "your shape is 1 of {}".format(count)
        rarity_surface, rarity_rect = self.createText(rarity_str, font_size - 5)
        surface.blit(rarity_surface, [750 - rarity_surface.get_size()[0]/2, 250 + offset])

        return surface

    @staticmethod
    def createText(text, size, color = "white"):
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
        self.next_x = self.x

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

        

