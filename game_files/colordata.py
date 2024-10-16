import pygame
from pygame import Surface

class ColorData():
    def __init__(self, id: int, name: str):
        self.id = id
        self.name = name
        self.circle_image = pygame.image.load(f'shape_images/backgrounds/circle/{name}.png')
        self.square_image = pygame.image.load(f'shape_images/backgrounds/square/{name}.png')
        self.triangle_image = pygame.image.load(f'shape_images/backgrounds/triangle/{name}.png')


color_data = [
    ColorData(0, "blue"),
    ColorData(1, "green"),
    # ColorData(2, "lemonlime"),
    # ColorData(3, "orange"),
]

