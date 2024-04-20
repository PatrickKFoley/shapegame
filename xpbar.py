import pygame
from circledata import *

class XpBar(pygame.sprite.Sprite):
    def __init__(self, topleft, start_xp, xp_gained):
        super().__init__()

        self.background_full = pygame.image.load("circles/gradient9.png")
        self.front_full = pygame.image.load("circles/gradient6.png")

        self.length = 1920/4
        self.width = 35
        self.topleft = topleft
        self.animating = False

        # calculate all required metrics
        end_xp = start_xp + xp_gained
        self.start_level = 0
        self.end_level = 0
        start_percent = round((start_xp) / (xp_amounts[0]), 3)
        end_percent = round((end_xp) / (xp_amounts[0]), 3)
        
        for i, amount in enumerate(xp_amounts):
            if start_xp >= amount:
                self.start_level = i + 1
                start_percent = round((start_xp - amount) / (xp_amounts[i + 1] - amount), 3)

            if end_xp >= amount:
                self.end_level = i + 1
                end_percent = round((end_xp - amount) / (xp_amounts[i + 1] - amount), 3)

                if end_percent == 0.0: end_percent = 1
                if end_percent == 1.0: end_percent = 0
        
        self.levels_gained = self.end_level - self.start_level
        self.front_length_start = int(1920/4 * start_percent) - 10
        self.front_length_end = int(1920/4 * end_percent) - 10

        if self.front_length_start <= 0: self.front_length_start = 0
        if self.front_length_end <= 0: self.front_length_end = 0

        # print(self.front_length_start, self.front_length_end)
        # print(self.start_level, self.end_level, self.levels_gained)


        self.buildSurface()

    def update(self):
        if not self.animating:
            return

        if self.front_length_start < self.front_length_end or self.levels_gained > 0:
            self.front_length_start += 10

            if self.front_length_start >= self.length - 10:
                self.front_length_start = 0
                self.levels_gained -= 1
                self.start_level += 1
            
            self.buildSurface()

    def buildSurface(self):
        surface = pygame.Surface((self.length + 10, self.width + 60), pygame.SRCALPHA, 32)

        background = pygame.transform.smoothscale(self.background_full, (int(self.length), int(self.width)))

        front = pygame.transform.smoothscale(self.front_full, (int(self.front_length_start), int(self.width - 10)))
        
        level, level_rect = self.createText("level: {}".format(self.start_level + 1), 60)
        level_rect.center = [(self.length + 10) / 2, self.width + 35]

        surface.blit(background, [5, 10])
        surface.blit(front, [10, 15])
        surface.blit(level, level_rect)


        self.image = surface
        self.rect = self.image.get_rect()
        self.rect.center = self.topleft
        

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
