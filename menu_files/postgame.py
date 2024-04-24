import pygame
from pygame.locals import *

from menu_files.postgame_files.postgameshape import PostGameShape
from screen_elements.clickabletext import ClickableText
from screen_elements.xpbar import XpBar


class PostGame():
    def __init__(self, victory, your_shape, their_shape, keeps, xp_earned, you_name, their_name, screen):
        self.victory = victory
        self.your_shape_data = your_shape
        self.their_shape_data = their_shape
        self.keeps = keeps
        self.your_username = you_name
        self.their_username = their_name
        self.your_username.rect.center = [450, 725]
        self.their_username.rect.center = [1920 - 450, 725]
        self.screen = screen

        self.your_shape = PostGameShape(self.your_shape_data, True, victory, keeps)
        self.their_shape = PostGameShape(self.their_shape_data, False, not victory, keeps)
        self.shapes_group = pygame.sprite.Group()
        self.shapes_group.add(self.your_shape)
        self.shapes_group.add(self.their_shape)

        if victory:
            self.your_xp_bar = XpBar([450, 850], your_shape.xp, xp_earned)
            self.their_xp_bar = XpBar([1920-450, 850], their_shape.xp, 0)
        else:
            self.your_xp_bar = XpBar([450, 850], your_shape.xp, 0)
            self.their_xp_bar = XpBar([1920-450, 850], their_shape.xp, xp_earned)
        self.xp_bar_group = pygame.sprite.Group()
        self.xp_bar_group.add(self.your_xp_bar)
        self.xp_bar_group.add(self.their_xp_bar)

        self.background = pygame.image.load("backgrounds/BG1.png")
        self.title, self.title_rect = self.createText("shapegame", 150)
        self.title_rect.center = (1920 / 2, 1080 / 9)
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font("backgrounds/font.ttf", 80)
        self.exit_clickable = ClickableText("back", 50, 1870, 1045)
        self.cursor = pygame.transform.smoothscale(pygame.image.load("backgrounds/cursor.png"), (12, 12))
        self.cursor_rect = self.cursor.get_rect()
        self.cursor_rect.center = pygame.mouse.get_pos()

        if victory: self.top_text, self.top_text_rect = self.createText("you won!", 120)
        else: self.top_text, self.top_text_rect = self.createText("you lost :(", 120)
        self.top_text_rect.center = (1920 / 2, 1080 / 4)

        self.clickables = []
        self.clickables.append(self.exit_clickable)

        self.running = True
        self.frames = 0

    def start(self):
        pygame.display.update()

        while self.running:
            # ---- DISPLAY UPDATES ----

            pygame.display.flip()

            mouse_pos = pygame.mouse.get_pos()
            events = pygame.event.get()

            self.handleInputs(events, mouse_pos)
            self.updateClickables(mouse_pos)
            self.updateCursor(mouse_pos)
            self.shapes_group.update()
            self.xp_bar_group.update()

            self.animateElements()
            self.drawElements()

            self.clock.tick(60)
            self.frames += 1

    # HELPERS

    def drawElements(self):
        self.screen.blit(self.background, [0, 0])
        self.screen.blit(self.title, self.title_rect)
        self.screen.blit(self.top_text, self.top_text_rect)
        self.screen.blit(self.exit_clickable.surface, self.exit_clickable.rect)
        self.screen.blit(self.your_username.surface, self.your_username.rect)
        self.screen.blit(self.their_username.surface, self.their_username.rect)
        self.shapes_group.draw(self.screen)
        self.xp_bar_group.draw(self.screen)
        self.screen.blit(self.cursor, self.cursor_rect)

    def animateElements(self):
        # move the transferred shape to the appropriate side
        if self.frames == 100 and self.keeps:
            if self.victory: self.their_shape.moveTo(625)
            else: self.your_shape.moveTo(1920 - 625)

        if self.frames == 100:
            self.your_xp_bar.animating = self.their_xp_bar.animating = True

    def updateCursor(self, mouse_pos):
        self.cursor_rect.center = mouse_pos

    def updateClickables(self, mouse_pos):
        for clickable in self.clickables:
            clickable.update(mouse_pos)

    def handleInputs(self, events, mouse_pos):
        for event in events:
            if event.type == MOUSEBUTTONDOWN:
                if self.exit_clickable.rect.collidepoint(mouse_pos):
                    self.running = False

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