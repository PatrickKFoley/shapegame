import pygame, pygame_textinput
from pygame.locals import MOUSEBUTTONDOWN
from .screenelement import ScreenElement

SHRINK_AMOUNT = 0.25

class EditableText(ScreenElement):
    def __init__(self, text, size, x, y, alignment = "center", max_chars = 15):
        super().__init__(x, y)
        self.text = text
        self.size = size
        self.alignment = alignment
        self.max_chars = max_chars

        self.manager = pygame_textinput.TextInputManager()
        self.manager.value = text
        self.manager.cursor_pos = len(text)

        self.input = pygame_textinput.TextInputVisualizer(self.manager, pygame.font.Font("assets/misc/font.ttf", size))
        self.input.font_color = "black"
        self.input.cursor_color = "black"
        self.input.cursor_width = -1

        self.manager_selected = pygame_textinput.TextInputManager()
        self.manager_selected.value = text
        self.manager_selected.cursor_pos = len(text)

        self.input_selected = pygame_textinput.TextInputVisualizer(self.manager_selected, pygame.font.Font("assets/misc/font.ttf", size))
        self.input_selected.font_color = "darkgray"
        self.input_selected.cursor_color = "darkgray"
        self.input_selected.cursor_width = -1

        self.surface = self.input.surface
        self.rect = self.surface.get_rect()
        self.align()

    def getText(self):
        return self.input.value[len(self.text):]


    def update(self, events, rel_mouse_pos):
        super().update(events, rel_mouse_pos)

        if self.disabled: return
        self.hovered = self.rect.collidepoint(rel_mouse_pos)  
        
        if self.selected:
            # Store previous values before update
            prev_input_value = self.input.value
            prev_input_selected_value = self.input_selected.value
            
            self.input.update(events)
            self.input_selected.update(events)

            # Check if input exceeds max chars and revert if needed
            if len(self.input.value) - len(self.text) > self.max_chars:
                self.input.value = prev_input_value 
                self.input_selected.value = prev_input_selected_value
                return

            # Only allow alphanumeric characters
            if not (self.input.value[-1].isalnum() or self.input.value[-1] == ' '):
                self.input.value = self.input.value[:-1]
                self.input_selected.value = self.input_selected.value[:-1]

            if len(self.input.value) < len(self.text):
                self.input.value = self.text

            if self.manager.cursor_pos < len(self.text):
                self.manager.cursor_pos = len(self.text)

            if len(self.input_selected.value) < len(self.text):
                self.input_selected.value = self.text

            if self.manager_selected.cursor_pos < len(self.text):
                self.manager_selected.cursor_pos = len(self.text)

            self.rect = self.input.surface.get_rect()
            self.align()

            self.surface = self.input_selected.surface

        else: 
            if self.hovered: self.surface = self.input_selected.surface
            else: self.surface = self.input.surface

        for event in events:
            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                if not self.rect.collidepoint(rel_mouse_pos):
                    self.deselect()
                else: self.select()

    def reset(self):
        self.manager = pygame_textinput.TextInputManager()
        self.manager.value = self.text
        self.manager.cursor_pos = len(self.text)

        self.input = pygame_textinput.TextInputVisualizer(self.manager, pygame.font.Font("assets/misc/font.ttf", self.size))
        self.input.font_color = "black"
        self.input.cursor_color = "black"

        self.rect = self.input.surface.get_rect()
        self.align()

        self.surface = self.input.surface
