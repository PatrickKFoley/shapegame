import pygame, pygame_textinput

SHRINK_AMOUNT = 0.25

class EditableText:
    def __init__(self, text, size, x, y, alignment = "center"):
        self.x = x
        self.y = y
        self.y_init = y
        self.y_scroll = 0
        self.text = text
        self.size = size
        self.alignment = alignment 
        self.selected = False
        self.growing = False
        self.shrinking = False

        self.manager = pygame_textinput.TextInputManager()
        self.manager.value = text
        self.manager.cursor_pos = len(text)
        

        self.input = pygame_textinput.TextInputVisualizer(self.manager, pygame.font.Font("backgrounds/font.ttf", size))
        self.input.font_color = "white"
        self.input.cursor_color = "white"
        self.input.cursor_width = -1

        self.surface = pygame.transform.smoothscale(self.input.surface, (self.input.surface.get_size()[0] - 10, self.input.surface.get_size()[1] - 10))
        self.rect = self.surface.get_rect()
        self.align()


        self.width, self.height = self.surface.get_size()
        self.shrink_amount = 10

    def getText(self):
        return self.input.value[len(self.text):]

    def update(self, events):
        if self.selected:

            self.input.update(events)

            if len(self.input.value) < len(self.text):
                self.input.value = self.text

            if self.manager.cursor_pos < len(self.text):
                self.manager.cursor_pos = len(self.text)

            self.rect = self.input.surface.get_rect()
            self.align()

            self.surface = self.input.surface

            if self.growing:
                self.shrink_amount -= SHRINK_AMOUNT
                self.change_size()

                if self.shrink_amount == 0.0:
                    self.growing = False
                    self.shrinking = True

            else:
                self.shrink_amount += SHRINK_AMOUNT
                self.change_size()

                if self.shrink_amount == 10.0:
                    self.shrinking = False
                    self.growing = True

        
        # if you are no longer selected, but > standard size, shrink
        else:
            if self.shrink_amount != 10:
                self.shrink_amount += SHRINK_AMOUNT
                self.change_size()

                if self.shrink_amount == 10:
                    self.shrinking = False

    def change_size(self):
        w = self.input.surface.get_size()[0] - int(self.shrink_amount)
        h = self.input.surface.get_size()[1] - int(self.shrink_amount)

        self.surface = pygame.transform.smoothscale(self.input.surface, (w, h))
        
        self.rect = self.surface.get_rect()
        self.align()

    def select(self):
        self.selected = True
        self.growing = True
        self.shrinking = False

    def deselect(self):
        self.selected = False
        self.growing = False
        self.shrinking = True

    def reset(self):
        self.manager = pygame_textinput.TextInputManager()
        self.manager.value = self.text
        self.manager.cursor_pos = len(self.text)

        self.input = pygame_textinput.TextInputVisualizer(self.manager, pygame.font.Font("backgrounds/font.ttf", self.size))
        self.input.font_color = "white"
        self.input.cursor_color = "white"

        self.rect = self.input.surface.get_rect()
        self.align()

        self.surface = self.input.surface

    def scroll(self, amount):
        self.y_scroll += amount

        self.y = self.y_scroll + self.y_init
        self.align()

    def align(self):
        if self.alignment == "center":
            self.rect.center = [self.x, self.y]
        
        elif self.alignment == "topleft":
            self.rect.topleft = [self.x, self.y]

        elif self.alignment == "topright":
            self.rect.topright = [self.x, self.y]


