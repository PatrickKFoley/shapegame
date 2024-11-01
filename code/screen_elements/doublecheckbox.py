import pygame


class DoubleCheckbox:
    def __init__(self, text, size, x, y):
        self.y = y
        self.x = x
        self.text = self.createText(text, size)

        self.self_checked = False
        self.opp_checked = False

        self.checked_img = pygame.transform.smoothscale(pygame.image.load("assets/misc/box_checked.png"), (self.text.get_size()[1] - int(self.text.get_size()[1]/10), self.text.get_size()[1]- int(self.text.get_size()[1]/10)))
        self.unchecked_img = pygame.transform.smoothscale(pygame.image.load("assets/misc/box_unchecked.png"), (self.text.get_size()[1] - int(self.text.get_size()[1]/10), self.text.get_size()[1] - int(self.text.get_size()[1]/10)))

        self.length = self.text.get_size()[0] + self.checked_img.get_size()[0]*2
        self.width = self.text.get_size()[1]

        self.surface_false_false = pygame.Surface((self.length, self.width), pygame.SRCALPHA, 32)
        self.surface_false_false.blit(self.unchecked_img, [0, 0])
        self.surface_false_false.blit(self.unchecked_img, [self.length - self.checked_img.get_size()[1], 0])
        self.surface_false_false.blit(self.text, [self.length/2 - self.text.get_size()[0]/2, 0])

        self.surface_true_false = pygame.Surface((self.length, self.width), pygame.SRCALPHA, 32)
        self.surface_true_false.blit(self.checked_img, [0, 0])
        self.surface_true_false.blit(self.unchecked_img, [self.length - self.checked_img.get_size()[1], 0])
        self.surface_true_false.blit(self.text, [self.length/2 - self.text.get_size()[0]/2, 0])

        self.surface_false_true = pygame.Surface((self.length, self.width), pygame.SRCALPHA, 32)
        self.surface_false_true.blit(self.unchecked_img, [0, 0])
        self.surface_false_true.blit(self.checked_img, [self.length - self.checked_img.get_size()[1], 0])
        self.surface_false_true.blit(self.text, [self.length/2 - self.text.get_size()[0]/2, 0])

        self.surface_true_true = pygame.Surface((self.length, self.width), pygame.SRCALPHA, 32)
        self.surface_true_true.blit(self.checked_img, [0, 0])
        self.surface_true_true.blit(self.checked_img, [self.length - self.checked_img.get_size()[1], 0])
        self.surface_true_true.blit(self.text, [self.length/2 - self.text.get_size()[0]/2, 0])

        self.surface = self.surface_false_false

        self.rect = self.surface.get_rect()
        self.rect.center = [x, y]


    @staticmethod
    def createText(text, size):
        font_small = pygame.font.Font("assets/misc/font.ttf", size)
        text_unselected = font_small.render(text, True, "white")

        return text_unselected

    def toggle(self):
        self.self_checked = not self.self_checked
        self.buildSurface()

    def oppToggle(self):
        self.opp_checked = not self.opp_checked
        self.buildSurface()
    
    def buildSurface(self):
        if self.self_checked and self.opp_checked:
            self.surface = self.surface_true_true

        elif self.self_checked and not self.opp_checked:
            self.surface = self.surface_true_false

        elif not self.self_checked and self.opp_checked:
            self.surface = self.surface_false_true

        elif not self.self_checked and not self.opp_checked:
            self.surface = self.surface_false_false


    def getValue(self):
        if self.surface == self.surface_true_true or self.surface == self.surface_true_false: return 1
        else: return 0
