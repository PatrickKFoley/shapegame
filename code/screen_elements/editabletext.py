import pygame, pygame_textinput
from pygame.locals import MOUSEBUTTONDOWN
from .screenelement import ScreenElement

SHRINK_AMOUNT = 0.25
MAX_GROWTH = 5

class EditableText(ScreenElement):
    def __init__(self, text, size, x, y, alignment = "center", max_chars = 15):
        super().__init__(x, y)
        self.text = text
        self.size = size
        self.alignment = alignment
        self.max_chars = max_chars
        
        # Add growth tracking
        self.growth_amount = 0
        self.base_size = size

        self.manager = pygame_textinput.TextInputManager()
        self.manager.value = text
        self.manager.cursor_pos = len(text)

        self.input = pygame_textinput.TextInputVisualizer(self.manager, pygame.font.Font("assets/misc/font.ttf", size))
        self.input.font_color = "black"
        self.input.cursor_color = "black"
        self.input.cursor_width = -1
        self.fading_out = False

        self.surface = self.input.surface
        self.rect = self.surface.get_rect()
        self.align()

    def getText(self):
        return self.input.value[len(self.text):]

    def update(self, events, rel_mouse_pos):
        if not self.selected: super().update(events, rel_mouse_pos)


        if self.disabled: return
        self.hovered = self.rect.collidepoint(rel_mouse_pos)  
        
        # Handle growth/shrink
        target_growth = MAX_GROWTH if (self.hovered or self.selected) else 0
        if self.growth_amount < target_growth:
            self.growth_amount += 1
            self._update_text_size()
        elif self.growth_amount > target_growth:
            self.growth_amount -= 1
            self._update_text_size()

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

            if len(self.input.value) < len(self.text):
                self.input.value = self.text

            if self.manager.cursor_pos < len(self.text):
                self.manager.cursor_pos = len(self.text)

            self.rect = self.input.surface.get_rect()
            self.align()

            self.surface = self.input.surface

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

        else: 
            self.surface = self.input.surface

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

        self.input = pygame_textinput.TextInputVisualizer(self.manager, pygame.font.Font("assets/misc/font.ttf", self.size))
        self.input.font_color = "black"
        self.input.cursor_color = "black"

        self.rect = self.input.surface.get_rect()
        self.align()

        self.surface = self.input.surface

    def _update_text_size(self):
        # Update both input visualizers with new font size
        current_size = self.base_size + self.growth_amount
        self.input.font_object = pygame.font.Font("assets/misc/font.ttf", current_size)
        
        # Update surfaces and alignment
        self.rect = self.input.surface.get_rect()
        self.align()
