import pygame
from pygame.locals import *
from game_files.circledata import *
from screen_elements.clickabletext import ClickableText
from screen_elements.text import Text
from menu_files.main_menu_files.menucircle import MenuShape
from screen_elements.arrow import Arrow

class UserCollectionMenu():
    def __init__(self, screen, circle_images_full, shapes, user, session):
        # parameters passed from menu
        self.screen = screen
        self.circle_images_full = circle_images_full
        self.shapes = shapes
        self.user = user
        self.session = session

        # create pygame objects
        self.clock = pygame.time.Clock()

        # sprite group for your shape collection
        self.collection_group = pygame.sprite.Group()

        # load and center cursor, load background
        self.background = pygame.image.load("backgrounds/BG1.png")
        self.cursor = pygame.transform.smoothscale(pygame.image.load("backgrounds/cursor.png"), (12, 12))
        self.cursor_rect = self.cursor.get_rect()
        self.cursor_rect.center = pygame.mouse.get_pos()

        # load sounds
        self.click_sound = pygame.mixer.Sound("sounds/click.wav")

        # create text elements
        self.title_text = Text("shapegame", 150, 1920/2, 1080/7)
        self.logged_in_as_text = Text("logged in as: {}".format(self.user.username), 35, 10, 1030, "topleft")
        self.loading_shapes_text = Text("loading your shapes", 100, 1920/2, 1080/2)

        self.texts = []
        self.texts.append(self.title_text)
        self.texts.append(self.logged_in_as_text)

        # create clickable elements
        self.exit_clickable = ClickableText("back", 50, 1870, 1045)
        self.right = Arrow(1920/2 + 50, 700-25, "->")
        self.left = Arrow(1920/2 - 50, 700-25, "<-")

        self.clickables = []
        self.clickables.append(self.exit_clickable)
        self.clickables.append(self.right)
        self.clickables.append(self.left)

        # update the display
        self.screen.blit(self.background, (0, 0))
        self.screen.blit(self.loading_shapes_text.surface, self.loading_shapes_text.rect)
        pygame.display.update()

        # determine what shape will be selected
        self.selected_shape = 0
        if len(self.shapes) >= 5:   self.selected_shape = 3
        elif len(self.shapes) == 4: self.selected_shape = 3
        elif len(self.shapes) == 3: self.selected_shape = 2
        elif len(self.shapes) == 2: self.selected_shape = 2
        else:                       self.selected_shape = 1

        # load your shape collection
        for counter, shape in enumerate(self.shapes):
            # create shape sprite
            shape = MenuShape(counter+1, shape, self.circle_images_full[shape.face_id][shape.color_id], len(self.shapes), "COLLECTIONS", False, self.session)
            self.collection_group.add(shape)

            # select this sprite if it is the selected sprite
            if counter + 1 == self.selected_shape:
                shape.toggleSelected()

        # exit flag
        self.exit_clicked = False

    def start(self):
        while True:
            self.handleInputs()
            self.drawScreenElements()

            if self.exit_clicked: return

            self.clock.tick(60)

    def handleInputs(self):
        events = pygame.event.get()
        mouse_pos = pygame.mouse.get_pos()

        for event in events:
            if event.type == MOUSEBUTTONDOWN:
                self.click_sound.play()

                # exit
                if self.exit_clickable.rect.collidepoint(mouse_pos):
                    self.exit_clicked = True
                
                # if one of the arrows was clicked
                elif self.left.rect.collidepoint(mouse_pos) or self.right.rect.collidepoint(mouse_pos):
                    
                    # if the left arrow was clicked
                    if self.left.rect.collidepoint(mouse_pos):
                        # if we are not on the left-most shape
                        if self.selected_shape != 1:
                            # change selection
                            self.selected_shape -= 1

                            # if there are more than 6 shapes, instruct them to move
                            if len(self.shapes) >= 6:
                                for shape in self.collection_group:
                                    shape.moveRight()

                    # if the right arrow was clicked
                    elif self.right.rect.collidepoint(mouse_pos):
                        # if we are not on the right-most shape
                        if self.selected_shape != len(self.shapes):
                            # change selection
                            self.selected_shape += 1

                            # if there are more than 6 shapes, instruct them to move
                            if len(self.shapes) >= 6:
                                for shape in self.collection_group:
                                    shape.moveLeft()

                    # ensure the right shape is selected
                    for counter, shape in enumerate(self.collection_group):
                        if (counter + 1) == self.selected_shape:
                            shape.select()
                        else:
                            shape.disable()

    def drawScreenElements(self):
        # flip the display, get mouse position
        pygame.display.flip()
        mouse_pos = pygame.mouse.get_pos()

        # draw the background
        self.screen.blit(self.background, (0, 0))

        # update and draw your sprites
        self.collection_group.update(self.screen) 
        self.collection_group.draw(self.screen)

        # update and draw clickable elements
        for clickable in self.clickables:
            clickable.update(mouse_pos)
            self.screen.blit(clickable.surface, clickable.rect)

        # draw text elements
        for text in self.texts:
            self.screen.blit(text.surface, text.rect)

        # center and draw cursor
        self.cursor_rect.center = pygame.mouse.get_pos()
        self.screen.blit(self.cursor, self.cursor_rect)