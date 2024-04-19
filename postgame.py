import pygame
from pygame.locals import *
from clickabletext import ClickableText
from postgameshape import PostGameShape

class PostGame():
    def __init__(self, victory, your_shape, their_shape, keeps, you_name, their_name, screen):
        self.victory = victory
        self.your_shape_data = your_shape
        self.their_shape_data = their_shape
        self.keeps = keeps
        self.your_username = you_name
        self.their_username = their_name
        self.screen = screen

        self.your_shape = PostGameShape(self.your_shape_data, True, victory)
        self.their_shape = PostGameShape(self.their_shape_data, False, not victory)
        self.shapes_group = pygame.sprite.Group()
        self.shapes_group.add(self.your_shape)
        self.shapes_group.add(self.their_shape)

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
        self.screen.blit(self.your_username[0], self.your_username[1])
        self.screen.blit(self.their_username[0], self.their_username[1])
        self.shapes_group.draw(self.screen)
        self.screen.blit(self.cursor, self.cursor_rect)

    def animateElements(self):
        # move the transferred shape to the appropriate side
        if self.frames == 100:
            
            if self.victory: self.their_shape.moveTo(600)
            else: self.your_shape.moveTo(1920 - 600)



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