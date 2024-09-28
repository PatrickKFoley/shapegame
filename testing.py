import pygame
from pygame.locals import *
import sys
import math
import random
from game_files.game import Game
from createdb import Shape
from game_files.circledata import *
from threading import Thread
from game_files.powerup2 import Powerup
from screen_elements.friendswindow import FriendsWindow
from screen_elements.notificationswindow import NotificationsWindow

from createdb import User, Shape as ShapeData
from game_files.circledata import colors as color_data
from game_files.circledata import powerup_data
from pygame.sprite import Group

from game_files.shape import Shape

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from createdb import User, Shape as DbShape

def circle():
    pygame.init()

    # Set up the window
    window_width = 800
    window_height = 600
    window = pygame.display.set_mode((window_width, window_height))
    pygame.display.set_caption("Dot in Circle")

    # Define circle parameters
    circle_radius = 100
    circle_center = (window_width // 2, window_height // 2)

    # Function to draw a dot in a circle
    def draw_dot_in_circle(radius, center, angle):
        x = int(center[0] + radius * math.cos(math.radians(angle)))
        y = int(center[1] + radius * math.sin(math.radians(angle)))
        pygame.draw.circle(window, (255, 255, 255), (x, y), 5)  # Draw dot



    # Main loop
    clock = pygame.time.Clock()
    while True:
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()


        angle = random.randint(0, 180)
        draw_dot_in_circle(circle_radius, circle_center, angle)

        # Update the display
        pygame.display.flip()



        # Cap the frame rate
        clock.tick(60)

def createShape(self, owner_id = -1):
    face_id = random.randint(0, 4)
    color_id = random.randint(0, len(colors)-1)

    base = circles_unchanged[face_id]

    density = base["density"]
    velocity = base["velocity"] + random.randint(-3, 3)
    radius_min = base["radius_min"] + random.randint(-3, 3)
    radius_max = base["radius_max"] + random.randint(-3, 3)
    health = base["health"] + random.randint(-100, 100)
    dmg_multiplier = round(base["dmg_multiplier"] + round((random.randint(-10, 10) / 10), 2), 2)
    luck = round(base["luck"] + round((random.randint(-10, 10) / 10), 2), 2)
    team_size = base["team_size"] + random.randint(-3, 3)

    if owner_id != -1:
        try:
            shape = Shape(owner_id, face_id, color_id, density, velocity, radius_min, radius_max, health, dmg_multiplier, luck, team_size)
            self.session.add(shape)
            self.session.commit()
            return shape
        except:
            self.session.rollback()
            return False
    else:
        shape = Shape(owner_id, face_id, color_id, density, velocity, radius_min, radius_max, health, dmg_multiplier, luck, team_size)
        return shape

def get2Shapes():
    shape1 = Shape(-1, 0, 0, 1, 3, 30, 45, 260, 1.7, 8, 15)
    shape2 = Shape(-1, 0, 0, 1, 3, 30, 45, 260, 1.7, 8, 15)

    game_shape1 = {}
    game_shape1["group_id"] = 0
    game_shape1["circle_id"] = 0
    game_shape1["face_id"] = shape1.face_id
    game_shape1["color"] = colors[shape1.color_id]
    game_shape1["density"] = shape1.density
    game_shape1["velocity"] = shape1.velocity
    game_shape1["radius_min"] = shape1.radius_min
    game_shape1["radius_max"] = shape1.radius_max
    game_shape1["health"] = shape1.health
    game_shape1["dmg_multiplier"] = shape1.dmg_multiplier
    game_shape1["luck"] = shape1.luck
    game_shape1["team_size"] = shape1.team_size

    game_shape2 = {}
    game_shape2["group_id"] = 1
    game_shape2["circle_id"] = 0
    game_shape2["face_id"] = shape2.face_id
    game_shape2["color"] = colors[shape2.color_id]
    game_shape2["density"] = shape2.density
    game_shape2["velocity"] = shape2.velocity
    game_shape2["radius_min"] = shape2.radius_min
    game_shape2["radius_max"] = shape2.radius_max
    game_shape2["health"] = shape2.health
    game_shape2["dmg_multiplier"] = shape2.dmg_multiplier
    game_shape2["luck"] = shape2.luck
    game_shape2["team_size"] = shape2.team_size

    return game_shape1, game_shape2

def simulate():
    game_shape1, game_shape2 = get2Shapes()

    print(Game(game_shape1, game_shape2, "team 0", "team 1", None, False, False).play_game())

def play_game():
    pygame.init()
    pygame.mixer.pre_init(44100, -16, 2, 512)
    pygame.mouse.set_visible(False)

    screen = pygame.display.set_mode((1920, 1080), pygame.NOFRAME)
    game_shape1, game_shape2 = get2Shapes()

    print(Game(game_shape1, game_shape2, "team 0", "team 1", screen).play_game())

def countTo5():
    i = 0
    while i < 5:
        i += 1
        print(i)

def thread():
    print("STARTING")

    thread = Thread(target=countTo5)
    thread.start()
    # thread.join()

    # threa2 = Thread(target=countTo5)
    # threa2.start()
    # threa2.join()

    print("DONE")

def friends():
    # database session
    engine = create_engine("postgresql://postgres:postgres@172.105.8.221/root/shapegame/shapegame/database.db", echo=False)
    SessionMaker = sessionmaker(bind=engine)
    session = SessionMaker()

    user = session.query(User).filter(User.username == "a").one()

    print(user.favorite_id)

    pygame.init()
    screen = pygame.display.set_mode((1920, 1080))
    friends_window = FriendsWindow(user, session)
    notifications_window = NotificationsWindow(user, session)

    running = True
    while running:
        events = pygame.event.get()
        mouse_pos = pygame.mouse.get_pos()

        for event in events:
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_TAB:
                    friends_window.toggle()
                elif event.key == pygame.K_SPACE:
                    notifications_window.toggle()

        friends_window.update(mouse_pos, events)
        notifications_window.update(mouse_pos, events)
        screen.blit(friends_window.surface, friends_window.rect)
        screen.blit(notifications_window.surface, notifications_window.rect)

        # Update the display
        pygame.display.flip()
        

    # Quit Pygame
    pygame.quit()
    sys.exit()

def shape2():

    pygame.init()
    screen = pygame.display.set_mode((1920, 1080))
    clock = pygame.time.Clock()
    frames = 0

    shape_images = []
    hud_images = []
    powerup_images = []
    shape_data = ShapeData(-1, User(""), 1, 11, 1, 0, 90, 100, 100, 1, 1, 1, "", "", "")
    shape_data2 = ShapeData(-1, User(""), 1, 11, 1, 0, 50, 60, 100, 1, 1, 1, "", "", "")

    healthbar_img = pygame.image.load("backgrounds/healthbar.png")
    
    for powerup in powerup_data:
        image = pygame.image.load(powerup_data[powerup][0])
        hud_images.append(pygame.transform.smoothscale(image, (20, 20)))
        powerup_images.append(pygame.transform.smoothscale(image, (40, 40)))

    for i in range(0, 4):
        shape_images.append(pygame.transform.smoothscale(pygame.image.load("circles/{}/{}/{}.png".format(shape_data.face_id, color_data[shape_data.color_id][0], i)), (shape_data.radius_max + 100, shape_data.radius_max + 100)))
        

    shape = Shape(shape_data, 1, 1, shape_images, hud_images, healthbar_img)
    # shape2 = Shape(shape_data2, 3, 1, shape_images, hud_images, healthbar_img)
    group = Group()
    group.add(shape)
    # group.add(shape2)

# Main loop

    running = True
    while running:
        events = pygame.event.get()
        mouse_pos = pygame.mouse.get_pos()
        frames += 1

        for event in events:
            if event.type == pygame.QUIT:
                running = False

            if event.type == MOUSEBUTTONDOWN:

                shape.collectPowerup(Powerup("resurrect", powerup_images[3], (100, 100)))

        screen.fill((0, 0, 0))

        if frames >= 20:
            shape.takeDamage(1)
                
                # shape2.takeDamage(2)

        group.update()
        group.draw(screen)
        

        
        pygame.display.flip()
        clock.tick(60)
        

    # Quit Pygame
    pygame.quit()
    sys.exit()


def point_on_arc(percent, square_size):
    """
    Returns the (x, y) point on an arc that bulges from the bottom left to the top left of a square.
    
    Parameters:
    - percent: A value between 0 and 100 representing the position along the arc.
    - square_size: The size of the square (assumed to be square, so width = height = side length).
    
    Returns:
    - A tuple (x, y) representing the point on the arc.
    """
    # Calculate the radius of the arc (the side length of the square)
    radius = square_size
    
    # Map percent (0-100) to angle (270° to 180°)
    start_angle = 270
    end_angle = 180
    angle = math.radians(start_angle - (start_angle - end_angle) * (percent / 100))
    
    # The center of the quarter-circle (bottom-left corner of the square)
    center_x = 0
    center_y = square_size
    
    # Calculate the x, y coordinates on the arc
    x = center_x + radius * math.cos(angle)
    y = center_y + radius * math.sin(angle)
    
    return (square_size-x*-1, y)

print(point_on_arc(90, 10))

# shape2()

# while True:
#     simulate()
# play_game()
# thread()