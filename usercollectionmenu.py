import pygame
from pygame.locals import *
from circledata import *
from clickabletext import ClickableText
from menucircle import MenuShape
from arrow import Arrow

class UserCollectionMenu():
    def __init__(self, screen, circle_images_full, shapes, user, session):
        self.screen = screen
        self.circle_images_full = circle_images_full
        self.shapes = shapes
        self.user = user
        self.session = session

        self.collection_group = pygame.sprite.Group()

        self.cursor = pygame.transform.smoothscale(pygame.image.load("backgrounds/cursor.png"), (12, 12))
        self.cursor_rect = self.cursor.get_rect()
        self.cursor_rect.center = pygame.mouse.get_pos()
        self.background = pygame.image.load("backgrounds/BG1.png")
        self.title, x = self.createText("shapegame", 150)
        self.title_rect = self.title.get_rect()
        self.title_rect.center = (1920 / 2, 1080 / 2)
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font("backgrounds/font.ttf", 80)
        self.stats_surface = 0


        self.click_sound = pygame.mixer.Sound("sounds/click.wav")
        self.close_sound = pygame.mixer.Sound("sounds/close.wav")
        self.close_sound.set_volume(.5)

        self.exit_clickable = ClickableText("back", 50, 1870, 1045)
        self.logged_in_as, self.logged_in_as_rect = self.createText("logged in as: " + self.user.username, 35)
        self.logged_in_as_rect.topleft = (10, 1030)

        self.right = Arrow(1920/2 + 50, 700, "->")
        self.left = Arrow(1920/2 - 50, 700, "<-")

        self.clickables = []
        self.clickables.append(self.exit_clickable)
        self.clickables.append(self.right)
        self.clickables.append(self.left)

        self.screen.blit(self.background, (0, 0))
        self.screen.blit(self.title, self.title_rect)
        pygame.display.update()

    def start(self):
        selected_shape = 0

        text_surface, text_rect = self.createText("loading your shapes", 100)
        text_rect.center = [1920 / 2, 1080 / 2]

        self.screen.blit(self.background, (0, 0))
        self.screen.blit(text_surface, text_rect)
        pygame.display.update()
        self.collection_group.empty()

        counter = 1
        for shape in self.shapes:
            self.collection_group.add(MenuShape(counter, shape, self.circle_images_full[shape.face_id][shape.color_id], len(self.shapes), "COLLECTIONS", False, self.session))
            counter += 1

        if len(self.shapes) >= 5:
            selected_shape = 3
        elif len(self.shapes) == 4:
            selected_shape = 3
        elif len(self.shapes) == 3:
            selected_shape = 2
        elif len(self.shapes) == 2:
            selected_shape = 2
        else:
            selected_shape = 1

        counter = 0
        for shape in self.collection_group.sprites():
            counter += 1
            if counter == selected_shape:
                shape.toggleSelected()
                
        running = True
        while running:
            mouse_pos = pygame.mouse.get_pos()
            for clickable in self.clickables:
                clickable.update(mouse_pos)

            events = pygame.event.get()
            for event in events:
                if event.type == MOUSEBUTTONDOWN:
                    self.click_sound.play()

                    if self.exit_clickable.rect.collidepoint(mouse_pos):
                        self.close_sound.play()
                        running = False
                    
                    elif self.left.rect.collidepoint(mouse_pos) or self.right.rect.collidepoint(mouse_pos):
                        if self.left.rect.collidepoint(mouse_pos):
                            if selected_shape != 1:
                                selected_shape -= 1
                                for shape in self.collection_group.sprites():
                                    if len(self.shapes) >= 6:
                                        shape.moveRight()

                        elif self.right.rect.collidepoint(mouse_pos):
                            if selected_shape != len(self.shapes):
                                selected_shape += 1
                                for shape in self.collection_group.sprites():
                                    counter += 1
                                    if len(self.shapes) >= 6:
                                        shape.moveLeft()

                        counter = 0
                        for shape in self.collection_group.sprites():
                            counter += 1
                            if counter == selected_shape:
                                shape.select()
                            else:
                                shape.disable()
                                
            self.screen.blit(self.background, (0, 0))

            self.collection_group.draw(self.screen)
            self.collection_group.update(self.screen) 

            self.screen.blit(self.title, (1920 / 2 - self.title.get_size()[0] / 2, 1080 / 5 - self.title.get_size()[1] / 2))
            self.screen.blit(self.exit_clickable.surface, self.exit_clickable.rect)
            self.screen.blit(self.logged_in_as, self.logged_in_as_rect)

            self.screen.blit(self.left.surface, self.left.rect)
            self.screen.blit(self.right.surface, self.right.rect)

            self.cursor_rect.center = pygame.mouse.get_pos()
            self.screen.blit(self.cursor, self.cursor_rect)

            pygame.display.flip()

            self.clock.tick(60)

        # self.collection_group.empty()
        for shape in self.collection_group.sprites():
            shape.goHome()
            shape.disable()

    # HELPERS FROM MENU

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
