import pygame
from pygame import Surface

titles = ["Rookie", "Novice", "Adept", "Veteran", "Master", "Champion", "Legend", "Hero", "Mythical", "Titan", "Demigod", "Immortal", "Warlord", "Overlord", "Conqueror", "Tyrant", "Sovereign", "Emperor", "Supreme", "Almighty", "Invincible", "Colossus", "Behemoth", "Dreadnought", "Archon", "Ascendant", "Godlike"]
names = ["Zippy", "Bixie", "Jazzy", "Quirk", "Fizzy", "Zazzy", "Pixel", "Zippy", "Jazzy", "Fizzy", "Quixy", "Vixen", "Zesty", "Pixel", "Zilch", "Zonky", "Flick", "Quirk", "Zappy", "Zippy", "Pixel", "Bixby", "Zilch", "Vixen", "Jazzy", "Zesty", "Fizzy", "Bixby", "Pixel", "Quixy", "Zilch", "Zappy", "Flick", "Zesty", "Zippy", "Quirk", "Jazzy", "Pixel", "Bixie", "Fizzy", "Quixy", "Zappy", "Vixen", "Jazzy", "Pixel", "Flick", "Bixie", "Zilch", "Quirk", "Zesty", "Jazzy", "Pixel", "Zappy", "Bixie", "Flick", "Quixy", "Zilch", "Vixen", "Zesty", "Fizzy", "Bixby", "Pixel", "Zappy", "Zippy", "Jazzy", "Quixy", "Flick", "Zilch", "Pixel", "Zappy", "Bixie", "Fizzy", "Jazzy", "Quirk", "Zesty", "Pixel", "Flick", "Bixie", "Zappy", "Quixy", "Zilch", "Jazzy", "Fizzy", "Zesty", "Pixel", "Zappy", "Bixby", "Quirk", "Flick", "Zilch", "Jazzy", "Quixy", "Pixel", "Fizzy", "Bixie", "Zappy", "Zesty", "Jazzy", "Quirk", "Flick", "Zok", "Fip", "Zim", "Zat", "Qip", "Dax", "Zin", "Kip", "Zor", "Qik", "Piz", "Tix", "Zab", "Wop", "Qoz", "Dib", "Zep", "Fop", "Zem", "Jip", "Qub", "Vex", "Zed", "Qet", "Wix", "Zin", "Joz", "Zim", "Fex", "Qix", "Zep", "Wox", "Piz", "Qub", "Zun", "Jex", "Zil", "Qop", "Vip", "Zeb", "Qix", "Vom", "Zit", "Zuv", "Qol", "Zok", "Jip", "Qub", "Zet", "Piz", "Qat", "Zim", "Qab", "Zuz", "Qip", "Zeb", "Fiz", "Qix", "Zun", "Pov", "Zat", "Qor", "Zep", "Qux", "Zol", "Qix", "Zem", "Juz", "Qab", "Zet", "Zix", "Qox", "Zop", "Qut", "Zun", "Qix", "Zex", "Qob", "Zit", "Jix", "Qiz", "Zup", "Qix", "Zem", "Zat", "Qop", "Zob", "Qix", "Zat", "Qid", "Zux", "Qub", "Zut", "Qix", "Zem", "Qod", "Zex", "Qip", "Zop", "Qiz"]

class ShapeData():
    def __init__(self, type: str, v: int, r_min: int, r_max: int, dmg_x: float, health: int, luck: int, team_size: int):
        self.type = type
        self.velocity = v
        self.radius_min = r_min
        self.radius_max = r_max
        self.health = health
        self.dmg_multiplier = dmg_x
        self.luck = luck
        self.team_size = team_size

class ColorData():
    def __init__(self, id: int, name: str, text_color: list[int]):
        self.id = id
        self.name = name
        self.text_color = text_color
        self.circle_image = pygame.image.load(f'assets/shapes/backgrounds/circle/{name}.png')
        self.square_image = pygame.image.load(f'assets/shapes/backgrounds/square/{name}.png')
        self.triangle_image = pygame.image.load(f'assets/shapes/backgrounds/triangle/{name}.png')
        self.rhombus_image = pygame.image.load(f'assets/shapes/backgrounds/rhombus/{name}.png')
        self.spiral_image = pygame.image.load(f'assets/shapes/backgrounds/spiral/{name}.png')

        self.shape_backgrounds = {
            'circle': self.circle_image,
            'square': self.square_image,
            'triangle': self.triangle_image,
            'rhombus': self.rhombus_image,
            'spiral': self.spiral_image
        }

shape_data = {
    'circle':   ShapeData('circle', 8, 40, 50, 1.2, 150, 10, 10),
    'triangle': ShapeData('triangle', 10, 50, 60, 1.1, 150, 9, 8),
    'square':   ShapeData('square', 6, 55, 65, 1.0, 200, 7, 6),
    'rhombus':  ShapeData('rhombus', 10, 80, 90, 1.1, 300, 9, 4),
    'spiral':   ShapeData('spiral', 5, 75, 85, 1.5, 500, 9, 3)
}

color_names = [
    "blue", "gray", "green", "lemonlime",
    "orange", "pink", "sprite", "tan", 'black'
]

shape_names = [
    "circle", "triangle", "square",
    "rhombus", "spiral"
]

shape_weights = [
    30, 25, 25, 15, 5
]

color_data = [
    ColorData(0, "blue", [82, 207, 250]),
    ColorData(1, "gray", [165, 165, 165]),
    ColorData(2, "green", [46, 139, 41]),
    ColorData(3, 'lemonlime', [163, 248, 36]),
    ColorData(4, 'orange', [243, 115, 11]),
    ColorData(5, 'pink', [255, 10, 210]),
    ColorData(6, 'sprite', [104, 224, 186]),
    ColorData(7, 'tan', [199, 170, 134])
]

