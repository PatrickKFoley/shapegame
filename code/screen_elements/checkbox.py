import pygame


class Checkbox:
    def __init__(self, text, size, x, y):
        self.y = y
        self.x = x
        self.text = self.createText(text, size)

        checked = pygame.transform.smoothscale(pygame.image.load("assets/misc/box_checked.png"), (self.text.get_size()[1] - 10, self.text.get_size()[1]- 10))
        unchecked = pygame.transform.smoothscale(pygame.image.load("assets/misc/box_unchecked.png"), (self.text.get_size()[1] - 10, self.text.get_size()[1] - 10))

        self.surface_unchecked = pygame.Surface((self.text.get_size()[0] + 100, self.text.get_size()[1]), pygame.SRCALPHA, 32)
        self.surface_unchecked.blit(unchecked, [0, 5])
        self.surface_unchecked.blit(self.text, [checked.get_size()[0] + 5, 0])

        self.surface_checked = pygame.Surface((self.text.get_size()[0] + 100, self.text.get_size()[1]), pygame.SRCALPHA, 32)
        self.surface_checked.blit(checked, [0, 5])
        self.surface_checked.blit(self.text, [checked.get_size()[0] + 5, 0])

        self.surface = self.surface_unchecked

        self.rect = self.surface.get_rect()
        self.rect.center = [x, y]


    @staticmethod
    def createText(text, size):
        font_small = pygame.font.Font("assets/misc/font.ttf", size)
        text_unselected = font_small.render(text, True, "white")

        return text_unselected

    def toggle(self):
        if self.surface == self.surface_unchecked: self.surface = self.surface_checked
        else: self.surface = self.surface_unchecked

    def getValue(self):
        if self.surface == self.surface_checked: return 1
        else: return 0