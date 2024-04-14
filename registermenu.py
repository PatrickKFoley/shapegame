import pygame
from pygame.locals import *
from circledata import *
from user import User
from shape import Shape
from clickabletext import ClickableText
from editabletext import EditableText

class RegisterMenu():
    def __init__(self, screen, session):
        self.screen = screen
        self.session = session

        self.cursor = pygame.transform.smoothscale(pygame.image.load("backgrounds/cursor.png"), (12, 12))
        self.cursor_rect = self.cursor.get_rect()
        self.cursor_rect.center = pygame.mouse.get_pos()
        self.background = pygame.image.load("backgrounds/BG1.png")
        self.title, x = self.createText("shapegame", 150)
        self.title_rect = self.title.get_rect()
        self.title_rect.center = (1920 / 2, 1080 / 2)
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font("backgrounds/font.ttf", 80)
        self.game_played = False

        self.exit_clicked = False

        self.click_sound = pygame.mixer.Sound("sounds/click.wav")
        self.start_sound = pygame.mixer.Sound("sounds/start.wav")
        self.open_sound = pygame.mixer.Sound("sounds/open.wav")
        self.menu_music = pygame.mixer.Sound("sounds/menu.wav")
        self.close_sound = pygame.mixer.Sound("sounds/close.wav")

        self.open_sound.set_volume(.5)
        self.menu_music.set_volume(.5)
        self.close_sound.set_volume(.5)
        
        self.open_sound.play()

        self.exit_clickable = ClickableText("exit", 50, 1870, 1045)
        self.register_clickable = ClickableText("register", 50, 1920 / 2, 1050)

        self.clickables = []
        self.clickables.append(self.exit_clickable)
        self.clickables.append(self.register_clickable)

        self.screen.blit(self.background, (0, 0))
        self.screen.blit(self.title, self.title_rect)
        pygame.display.update()


        # Registration text input handlers
        self.register_username_editable = EditableText("Username: ", 60, 1920/2, 700)
        self.register_password_editable = EditableText("Password: ", 60, 1920/2, 800)
        self.register_password_confirm_editable = EditableText("Confirm password: ", 60, 1920/2, 900)

    def start(self):
        editable_texts = []
        editable_texts.append(self.register_username_editable)
        editable_texts.append(self.register_password_editable)
        editable_texts.append(self.register_password_confirm_editable)

        bad_password, bad_password_rect = self.createText("Passwords must match!", 50)
        bad_password_rect.center = [1920/2, 975]
        bad_password_flag = False

        short_password, short_password_rect = self.createText("Passwords too short!", 50)
        short_password_rect.center = [1920/2, 975]
        short_password_flag = False

        username_taken, username_taken_rect = self.createText("Username taken!", 50)
        username_taken_rect.center = [1920/2, 975]
        username_taken_flag = False

        while True:
            # get new inputs
            events = pygame.event.get()
            mouse_pos = pygame.mouse.get_pos()

            # handle inputs
            for event in events:
                if event.type == MOUSEBUTTONDOWN: 
                    self.click_sound.play()

                    # turn off all text inputs
                    for element in editable_texts:
                        element.deselect()

                    # if we are exiting
                    if self.exit_clickable.rect.collidepoint(mouse_pos):
                        self.exit_clicked = True

                    # if we are selecting username or password field
                    elif self.register_username_editable.rect.collidepoint(mouse_pos):
                        self.register_username_editable.select()

                    elif self.register_password_editable.rect.collidepoint(mouse_pos):
                        self.register_password_editable.select()

                    elif self.register_password_confirm_editable.rect.collidepoint(mouse_pos):
                        self.register_password_confirm_editable.select()

                    elif self.register_clickable.rect.collidepoint(mouse_pos):
                        # Check if input values are good

                        # reset any flags
                        bad_password_flag = False
                        short_password_flag = False
                        username_taken_flag = False

                        # search for username
                        try:
                            possible_user = self.session.query(User).filter(User.username == self.register_username_editable.getText()).one()
                            username_taken_flag = True
                        except:
                            pass

                        # password must be > 8 character
                        # if (len(self.register_password_editable.getText()) <= 8):
                        #     short_password_flag = True

                        # passwords must match
                        if (self.register_password_confirm_editable.getText() != self.register_password_editable.getText()):
                            bad_password_flag = True

                        # if no flags raised, user can register
                        if (not bad_password_flag and not username_taken_flag and not short_password_flag):
                            user = self.createUser(self.register_username_editable.getText())

                            if user == False:
                                # TODO issue creating user
                                continue

                            shapes = self.session.query(Shape).filter(Shape.owner_id == int(user.id)).all()
                            return user, shapes


            # draw things
            pygame.display.flip()
            self.screen.blit(self.background, (0, 0))
            self.screen.blit(self.title, (1920 / 2 - self.title.get_size()[0] / 2, 1080 / 2 - self.title.get_size()[1] / 2))
            self.screen.blit(self.exit_clickable.surface, self.exit_clickable.rect)
            self.screen.blit(self.register_clickable.surface, self.register_clickable.rect)

            
            if username_taken_flag: self.screen.blit(username_taken, username_taken_rect)
            elif short_password_flag: self.screen.blit(short_password, short_password_rect)
            elif bad_password_flag: self.screen.blit(bad_password, bad_password_rect)
            
            
            for element in editable_texts:
                self.screen.blit(element.surface, element.rect)

            self.cursor_rect.center = mouse_pos
            self.screen.blit(self.cursor, self.cursor_rect)


            # update any on screen elements
            self.exit_clickable.update(mouse_pos)
            self.register_clickable.update(mouse_pos)
            for element in editable_texts:
                element.update(events)

            # exit
            if self.exit_clicked:

                # reset any text inputs
                for element in editable_texts:
                    element.reset()

                return
                
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

    def createUser(self, username):
        try:
            user = User(username)
            self.session.add(user)
            self.session.commit()
            return user
        except:
            self.session.rollback()
            return False
