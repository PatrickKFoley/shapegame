import pygame
import sys
import math
import random
from game_files.game import Game
from server_files.database_shape import Shape
from game_files.circledata import *
from threading import Thread
from screen_elements.friendswindow import FriendsWindow

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
    pygame.init()
    screen = pygame.display.set_mode((1920, 1080))
    friends_window = FriendsWindow()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_TAB:
                    friends_window.toggle()

        friends_window.update()
        screen.blit(friends_window.surface, friends_window.rect)

        # Update the display
        pygame.display.flip()
        

    # Quit Pygame
    pygame.quit()
    sys.exit()

friends()

# while True:
#     simulate()
# play_game()
# thread()