import pygame, random
from code.game.circledata import *
from createdb import User, Shape

def createText(text, size, color = "white"):
    font = pygame.font.Font("assets/misc/font.ttf", size) 

    if type(text) == type("string"):
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()

        return text_surface, text_rect
    
    elif type(text) == type(["array"]):
        text_surfaces = []
        for element in text:
            text_surfaces.append(font.render(element, True, color))

        max_line_length = max(surface.get_size()[0] for surface in text_surfaces)
        line_height = text_surfaces[0].get_size()[1]

        surface = pygame.Surface((max_line_length, (len(text_surfaces) + 1) * line_height), pygame.SRCALPHA, 32)

        for i, text_surface in enumerate(text_surfaces):
            surface.blit(text_surface, [max_line_length/2 - text_surface.get_size()[0]/2, line_height * (i+1)])

        return surface, surface.get_rect()
    
def clearSurfaceBeneath(surface, rect):
    # Lock the surface to directly modify pixel data
    surface.lock()
    
    # Iterate over each pixel in the Rect area
    for x in range(rect.left, rect.right):
        for y in range(rect.top, rect.bottom):
            # Set each pixel within the Rect to fully transparent
            surface.set_at((x, y), (0, 0, 0, 0))
    
    # Unlock the surface
    surface.unlock()
    
def createShape(owner_id = -1, session = None, username = "no one"):
    # decrement number of shape tokens
    face_id = random.randint(0, 4)
    color_id = random.randint(0, len(colors)-1)

    base = circles_unchanged[face_id]

    density = base["density"]
    velocity = base["velocity"] + random.randint(0, 3)
    radius_min = base["radius_min"] + random.randint(-3, 3)
    radius_max = base["radius_max"] + random.randint(-3, 3)
    health = base["health"] + random.randint(-100, 100)
    dmg_multiplier = round(base["dmg_multiplier"] + (random.randint(-10, 10) / 10), 2)
    luck = round(base["luck"] + (random.randint(-10, 10) / 10), 2)
    team_size = base["team_size"] + random.randint(-3, 3)
    name = names[random.randint(0, len(names)-1)]
    title = titles[0]

    # DON'T LET RAD_MIN > RAD_MAX
    while radius_min >= radius_max:
        radius_min = base["radius_min"] + random.randint(-3, 3)
        radius_max = base["radius_max"] + random.randint(-3, 3)

    # DON'T LET DMGX == 0
    while dmg_multiplier == 0.0:
        dmg_multiplier = round(base["dmg_multiplier"] + (random.randint(-10, 10) / 10), 2)

    if owner_id != -1:
        try:
            owner = session.query(User).filter(User.id == owner_id).one()
            shape = Shape(owner_id, owner, face_id, color_id, density, velocity, radius_min, radius_max, health, dmg_multiplier, luck, team_size, username, name, title)
            session.add(shape)
            session.commit()


            # set default favorite shape id
            if owner.num_shapes == 0:
                session.query(User).filter(User.id == owner_id).update({'favorite_id': shape.id})

            session.query(User).filter(User.id == owner_id).update({'num_shapes': User.num_shapes + 1})
            session.query(User).filter(User.id == owner_id).update({'shape_tokens': User.shape_tokens - 1})
            session.commit()

            return shape
        except Exception as e:
            session.rollback()
            print(e)
            return False
    else:
        shape = Shape(owner_id, None, face_id, color_id, density, velocity, radius_min, radius_max, health, dmg_multiplier, luck, team_size, username, name, title)
        return shape

def getEssenceCost(level):
    return round(0.25 * (1.35 ** level), 2)
