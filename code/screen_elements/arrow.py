# import pygame
# from .screenelement import ScreenElement

# MAX_GROWTH = 15

# class Arrow(ScreenElement):
#     def __init__(self, x, y, direction = "->", length = 75, width = 50, growth = 15):
#         super().__init__(x, y)
        
#         self.center = [x, y]
#         self.direction = direction
#         self.length = length
#         self.width = width
#         self.growth = growth
#         self.growth_amount = 0

#         if direction == "->": self.image = pygame.image.load("assets/misc/arrow_right.png").convert_alpha()
#         else: self.image = pygame.image.load("assets/misc/arrow_left.png").convert_alpha()

#         self.buildSurface()


#     def update(self, events, mouse_pos):
#         super().update(events, mouse_pos)


#     def buildSurface(self):
#         self.surface = pygame.transform.smoothscale(self.image, (self.length + self.growth_amount, self.width + self.growth_amount))
#         self.rect = self.surface.get_rect()
#         self.rect.center = self.center