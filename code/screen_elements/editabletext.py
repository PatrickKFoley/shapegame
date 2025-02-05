import pygame, pygame_textinput
from pygame.locals import MOUSEBUTTONDOWN
from .screenelement import ScreenElement

SHRINK_AMOUNT = 0.25
MAX_GROWTH = 5

class EditableText(ScreenElement):
    def __init__(self, text, size, x, y, alignment = "center", max_chars = 15, outline_color = None):
        super().__init__(x, y)
        self.text = text
        self.size = size
        self.alignment = alignment
        self.max_chars = max_chars
        self.outline_color = outline_color
        
        # Add growth tracking
        self.growth_amount = 0
        self.base_size = size

        self.manager = pygame_textinput.TextInputManager()
        self.manager.value = text
        self.manager.cursor_pos = len(text)

        self.buildSurface(size)

    def buildSurface(self, size):
        '''build the surface of the editable text'''

        # create the input visualizer
        self.input = pygame_textinput.TextInputVisualizer(self.manager, pygame.font.Font("assets/misc/font.ttf", size))
        self.input.font_color = "black"
        self.input.cursor_color = "black"
        self.input.cursor_width = -1

        if self.outline_color is None:
            self.surface = self.input.surface
        else:
            # Create outline effect
            outline_input = pygame_textinput.TextInputVisualizer(self.manager, pygame.font.Font("assets/misc/font.ttf", size))
            outline_input.font_color = self.outline_color
            outline_input.cursor_color = self.outline_color
            outline_input.cursor_width = -1

            diff = max(2, int(size / 38))
            
            self.surface = pygame.Surface((self.input.surface.get_size()[0] + diff, self.input.surface.get_size()[1]), pygame.SRCALPHA, 32)
            self.surface.blit(outline_input.surface, [0, 0])
            self.surface.blit(self.input.surface, [diff, 0])

        self.rect = self.surface.get_rect()
        self.align()

    def getText(self):
        return self.input.value[len(self.text):]
    
    def handleGrowth(self):
        # determine growth amount
        target_growth = MAX_GROWTH if (self.hovered or self.selected) else 0
        
        # grow
        if self.growth_amount < target_growth:
            self.growth_amount += 1
            self.resize()

        # shrink
        elif self.growth_amount > target_growth:
            self.growth_amount -= 1
            self.resize()

    def update(self, events, rel_mouse_pos):
        if not self.selected: 
            super().update(events, rel_mouse_pos)
            # print('updating')
        if self.disabled: return
        
        self.hovered = self.rect.collidepoint(rel_mouse_pos)
        self.handleGrowth()

        # if selected, update the input and pulse in/out
        if self.selected:
            # Store previous values before update
            prev_input_value = self.input.value
            self.input.update(events)

            # Check if input exceeds max chars and revert if needed
            if len(self.input.value) - len(self.text) > self.max_chars:
                self.input.value = prev_input_value 
                return

            # Only allow alphanumeric characters
            if not (self.input.value[-1].isalnum() or self.input.value[-1] == ' '):
                self.input.value = self.input.value[:-1]

            # don't let the user delete the default text
            if len(self.input.value) < len(self.text):
                self.input.value = self.text
            if self.manager.cursor_pos < len(self.text):
                self.manager.cursor_pos = len(self.text)

            # update the surface
            self.buildSurface(self.base_size + self.growth_amount)

            # pulse opacity when selected
            if self.fading_out:
                self.alpha = max(self.alpha - 3, 100)
                self.surface.set_alpha(self.alpha)

                if self.alpha == 100:
                    self.fading_out = False
            else:
                self.alpha = min(self.alpha + 3, 255)
                self.surface.set_alpha(self.alpha)

                if self.alpha == 255:
                    self.fading_out = True

        # handle mouse events
        for event in events:
            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                if not self.rect.collidepoint(rel_mouse_pos): 
                    self.deselect()
                else: self.select()

    def select(self):
        super().select()
        self.fading_out = True

    def deselect(self):
        super().deselect()
        self.fading_out = False

    def reset(self):
        self.manager = pygame_textinput.TextInputManager()
        self.manager.value = self.text
        self.manager.cursor_pos = len(self.text)

        self.buildSurface(self.size)
        self.align()

    def resize(self):
        # Update with new font size
        current_size = self.base_size + self.growth_amount
        self.buildSurface(current_size)
        self.align()
