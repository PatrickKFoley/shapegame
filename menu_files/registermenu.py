import pygame
from pygame.locals import *
from game_files.circledata import *
from server_files.database_user import User
from server_files.database_shape import Shape
from screen_elements.clickabletext import ClickableText
from screen_elements.editabletext import EditableText
from screen_elements.text import Text

class RegisterMenu():
    def __init__(self, screen, session):
        # parameters from menu
        self.screen = screen
        self.session = session

        # create pygame objects
        self.clock = pygame.time.Clock()

        # load and center cursor, load background
        self.background = pygame.image.load("backgrounds/BG1.png")
        self.cursor = pygame.transform.smoothscale(pygame.image.load("backgrounds/cursor.png"), (12, 12))
        self.cursor_rect = self.cursor.get_rect()
        self.cursor_rect.center = pygame.mouse.get_pos()

        # load sounds
        self.click_sound = pygame.mixer.Sound("sounds/click.wav")
        self.start_sound = pygame.mixer.Sound("sounds/start.wav")
        self.open_sound = pygame.mixer.Sound("sounds/open.wav")
        self.menu_music = pygame.mixer.Sound("sounds/menu.wav")
        self.close_sound = pygame.mixer.Sound("sounds/close.wav")
        self.open_sound.set_volume(.5)
        self.menu_music.set_volume(.5)
        self.close_sound.set_volume(.5)

        # create text elements
        self.title_text = Text("shapegame", 150, 1920/2, 1080/2)
        self.bad_password_text = Text("Passwords must match!", 50, 1920/2, 975)
        self.short_password_text = Text("Password too short!", 50, 1920/2, 975)
        self.username_taken_text = Text("Username taken!", 50, 1920/2, 975)

        self.texts = []
        self.texts.append(self.title_text)
        self.texts.append(self.bad_password_text)
        self.texts.append(self.short_password_text)
        self.texts.append(self.username_taken_text)

        # create clickable elements
        self.exit_clickable = ClickableText("exit", 50, 1870, 1045)
        self.register_clickable = ClickableText("register", 50, 1920 / 2, 1050)

        self.clickables = []
        self.clickables.append(self.exit_clickable)
        self.clickables.append(self.register_clickable)

        # Registration text input handlers
        self.register_username_editable = EditableText("Username: ", 60, 1920/2, 700)
        self.register_password_editable = EditableText("Password: ", 60, 1920/2, 800)
        self.register_password_confirm_editable = EditableText("Confirm password: ", 60, 1920/2, 900)

        self.editable_texts = []
        self.editable_texts.append(self.register_username_editable)
        self.editable_texts.append(self.register_password_editable)
        self.editable_texts.append(self.register_password_confirm_editable)

        # update the display
        self.screen.blit(self.background, (0, 0))
        self.screen.blit(self.title_text.surface, self.title_text.rect)
        pygame.display.update()

        # flags
        self.exit_clicked = False
        self.bad_password_flag = False
        self.short_password_flag = False
        self.username_taken_flag = False

    def start(self):
        while True:
            # get events (must happen only once per loop, otherwise next gets will have nothing in buffer)
            events = pygame.event.get()

            # handle inputs, which might redirect (when user registered)
            redirect = self.handleInputs(events)
            if redirect != None: return redirect

            # update and draw screen elements
            self.drawScreenElements(events)
            
            # exit
            if self.exit_clicked:
                # reset any text inputs
                for element in self.editable_texts:
                    element.reset()

                return
                
            self.clock.tick(60)

    # start helpers

    def handleInputs(self, events):
        mouse_pos = pygame.mouse.get_pos()

        # handle inputs
        for event in events:
            if event.type == MOUSEBUTTONDOWN: 
                self.click_sound.play()

                # turn off all text inputs
                for element in self.editable_texts:
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
                    self.bad_password_flag = False
                    self.short_password_flag = False
                    self.username_taken_flag = False

                    # search for username
                    try:
                        possible_user = self.session.query(User).filter(User.username == self.register_username_editable.getText()).one()
                        self.username_taken_flag = True
                    except:
                        pass

                    # password must be > 8 character
                    # if (len(self.register_password_editable.getText()) <= 8):
                    #     short_password_flag = True

                    # passwords must match
                    if (self.register_password_confirm_editable.getText() != self.register_password_editable.getText()):
                        self.bad_password_flag = True

                    # if no flags raised, user can register
                    if (not self.bad_password_flag and not self.username_taken_flag and not self.short_password_flag):
                        user = self.createUser(self.register_username_editable.getText())

                        if user == False:
                            # TODO issue creating user
                            continue

                        shapes = self.session.query(Shape).filter(Shape.owner_id == int(user.id)).all()
                        return user, shapes
                    
        return None

    def drawScreenElements(self, events):
        # draw + update all elements

        # flip the display, get mouse position
        pygame.display.flip()
        mouse_pos = pygame.mouse.get_pos()

        # draw the background and title
        self.screen.blit(self.background, (0, 0))
        self.screen.blit(self.title_text.surface, self.title_text.rect)
        
        # if any flags have been raised, display the warning
        if self.username_taken_flag: self.screen.blit(self.username_taken_text.surface, self.username_taken_text.rect)
        elif self.short_password_flag: self.screen.blit(self.short_password_text.surface, self.short_password_text.rect)
        elif self.bad_password_flag: self.screen.blit(self.bad_password_text.surface, self.bad_password_text.rect)
        
        # update and draw all editable text elements
        for editable in self.editable_texts:
            editable.update(events)
            self.screen.blit(editable.surface, editable.rect)

        # update and draw all clickable elements
        for clickable in self.clickables:
            clickable.update(mouse_pos)
            self.screen.blit(clickable.surface, clickable.rect)

        # center and draw cursor
        self.cursor_rect.center = mouse_pos
        self.screen.blit(self.cursor, self.cursor_rect)

    # additional functions

    def createUser(self, username):
        try:
            user = User(username)
            self.session.add(user)
            self.session.commit()
            return user
        except:
            self.session.rollback()
            return False
