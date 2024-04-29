import pygame
from pygame.image import load
from screen_elements.text import Text

# how many pixels per frame the window moves
STEP_SIZE = 20

class FriendsWindow:
    def __init__(self):
        self.width = int(1920/4)
        self.height = 1080

        self.x = 0 - self.width
        self.next_x = 0 - self.width
        self.selected = False

        self.surface = pygame.transform.smoothscale(load("backgrounds/BG0.png"), (self.width, self.height))
        self.surface.set_alpha(220)
        self.rect = self.surface.get_rect()

        self.friends_text = Text("friends", 150, self.width/2, 100)

        self.surface.blit(self.friends_text.surface, self.friends_text.rect)

        self.align()

    # toggle the window being opened or closed
    def toggle(self):
        if self.selected:
            self.selected = False
            self.next_x = 0 - self.width
        else:
            self.selected = True
            self.next_x = 0

    def update(self):
        # window should move to the right
        if self.selected and self.x < self.next_x:
            self.x += STEP_SIZE

            # don't let it go too far
            if self.x > self.next_x: self.x = self.next_x

            self.align()

        # window should move to the left
        elif not self.selected and self.x > self.next_x:
            self.x -= STEP_SIZE

            # don't let it go too far
            if self.x < self.next_x: self.x = self.next_x

            self.align()

                

    def align(self):
        self.rect.topleft = [self.x, 0]