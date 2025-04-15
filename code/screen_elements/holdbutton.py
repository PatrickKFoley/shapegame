import pygame, time
from pygame.transform import smoothscale
from pygame.surface import Surface
from .screenelement import ScreenElement 
from pygame.image import load
from pygame.mixer import Sound
from sharedfunctions import clearSurfaceBeneath

class HoldButton(ScreenElement):
    def __init__(self, icon_name: str, center: list[int], fast_off = False):
        super().__init__(center[0], center[1])

        self.icon_name = icon_name
        icon_size = 40
        self.icon = smoothscale(load(f'assets/icons/{icon_name}_icon.png').convert_alpha(), [icon_size, icon_size])
        self.icon_alpha = 255
        self.icon_rect = self.icon.get_rect()
        self.icon_rect.center = [20, 70]
        
        surface_w, surface_h = 275, 90
        self.surface = Surface((surface_w, surface_h), pygame.SRCALPHA, 32).convert_alpha()
        self.rect = self.surface.get_rect()
        self.rect.center = center

        self.text_surface = Surface((230, 70), pygame.SRCALPHA, 32).convert_alpha()
        pygame.draw.rect(self.text_surface, 'black', [0, 0, 230, 70], border_radius=10)
        pygame.draw.rect(self.text_surface, 'white', [3, 3, 224, 64], border_radius=8)
        self.text_rect = self.text_surface.get_rect()
        self.text_rect.topleft = [45, 0]
        self.text_alpha = 0
        self.text_surface.set_alpha(self.text_alpha)

        self.hovered = False
        self.clicked = False
        self.disable_override = False # used to stop the text surface from being rendered when the essence bar is changing

        self.surface.blit(self.text_surface, self.text_rect)
        self.surface.blit(self.icon, self.icon_rect)

        if fast_off: self.fastOff()

        self.stretch_sound = Sound('assets/sounds/stretch_and_pop.wav')
        self.sound_start_time = None

    def checkIconHover(self, mouse_pos):

        # check if the mouse is hovering over the icon for additional text transparency
        if self.icon_rect.collidepoint(mouse_pos) and not self.disable_override:
            self.hovered = True

            if not self.clicked:
                self.icon_alpha = 50
                self.icon.set_alpha(self.icon_alpha)

                clearSurfaceBeneath(self.surface, self.icon_rect)
                self.surface.blit(self.icon, self.icon_rect)
        else: 
            self.hovered = False

            if self.icon_alpha < 255:
                self.icon_alpha = 255
                self.icon.set_alpha(self.icon_alpha)
                self.surface.blit(self.icon, self.icon_rect)

    def handleInputs(self, events, mouse_pos):

        no_events = True
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:

                if event.button == 1 and self.icon_rect.collidepoint(mouse_pos) and not self.disabled:
                    self.clicked = True
                    self.sound_start_time = time.time()
                    self.stretch_sound.play()

            elif event.type == pygame.MOUSEBUTTONUP:
                self.clicked = False
                self.stopStretchSound()

    def stopStretchSound(self):
        if self.sound_start_time == None: return

        if time.time() - self.sound_start_time < 1.5:
            self.stretch_sound.fadeout(100)

    def updateInfoAlpha(self):
        step = 25
        if self.hovered and self.text_alpha < 255:
            self.text_alpha = min(self.text_alpha + step, 255)
            self.text_surface.set_alpha(self.text_alpha)

            clearSurfaceBeneath(self.surface, self.text_rect)
            self.surface.blit(self.text_surface, self.text_rect)
        elif not self.hovered and self.text_alpha > 0:
            self.text_alpha = max(self.text_alpha - step, 0)
            self.text_surface.set_alpha(self.text_alpha)

            clearSurfaceBeneath(self.surface, self.text_rect)
            self.surface.blit(self.text_surface, self.text_rect)

    def updateIconAlpha(self):
        step = 2
        if self.clicked and self.icon_alpha < 255 and not self.disabled:
            self.icon_alpha = min(self.icon_alpha + step, 255)
            self.icon.set_alpha(self.icon_alpha)

            clearSurfaceBeneath(self.surface, self.icon_rect)
            self.surface.blit(self.icon, self.icon_rect)

    def update(self, events, mouse_pos):
        rel_mouse_pos = [mouse_pos[0] - self.rect.x, mouse_pos[1] - self.rect.y]
        
        self.checkIconHover(rel_mouse_pos)

        self.handleInputs(events, rel_mouse_pos)

        self.updateInfoAlpha()

        self.updateIconAlpha()
        
    def checkIfFullyClickedAndEnabled(self):
        return self.clicked and self.icon_alpha == 255 and not self.disabled
