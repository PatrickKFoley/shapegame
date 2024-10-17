import pygame, numpy
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
from game_files.colordata import color_data
from pygame.sprite import Group

from game_files.shape import Shape
from game_files.game2 import Game2
from game_files.game3 import Game3


from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from createdb import User, Shape as DbShape

def determineCollisionBrokenAlso(self, shape_1: Shape, shape_2: Shape):
    # 1: get relative v and pos
    v1 = numpy.array(shape_1.getV())
    v2 = numpy.array(shape_2.getV())
    v_rel = v2 - v1

    p1 = numpy.array(shape_1.getXY())
    p2 = numpy.array(shape_2.getXY())
    pos_rel = p2 - p1

    # 2: calculate time of closest approach
    v_rel_sqr = numpy.dot(v_rel, v_rel)

    # if relative vel is below 0, no collision will occur
    # if v_rel_sqr == 0: return False

    # time of closest approach
    t_closest = -numpy.dot(pos_rel, v_rel) / v_rel_sqr

    # 3: check if closest approach is within this frame
    if 0 <= t_closest <= 1:

        # calculate positions at t_closest
        future_p1 = p1 + t_closest * v1
        future_p2 = p2 + t_closest * v2

        # print(f'{p1} -> {future_p1}')
        # print(f'{p2} -> {future_p2}')

        # temp move collision mask
        shape_1.collision_mask_rect.center = future_p1
        shape_2.collision_mask_rect.center = future_p2

        # 4: determine if collision is taking place
        collision = shape_1.collision_mask.overlap(shape_2.collision_mask, [int(shape_2.collision_mask_rect.x - shape_1.collision_mask_rect.x), int(shape_2.collision_mask_rect.y - shape_1.collision_mask_rect.y)])

        # move collision mask back
        shape_1.collision_mask_rect.center = p1
        shape_2.collision_mask_rect.center = p2

        return bool(collision)
    
    # ?: check if overlapping at the end of this frame

    p1f = p1 + v1
    p2f = p2 + v2

    # temp move collision mask
    shape_1.collision_mask_rect.center = p1f
    shape_2.collision_mask_rect.center = p2f

    # 4: determine if collision is taking place
    collision = shape_1.collision_mask.overlap(shape_2.collision_mask, [int(shape_2.collision_mask_rect.x - shape_1.collision_mask_rect.x), int(shape_2.collision_mask_rect.y - shape_1.collision_mask_rect.y)])

    # move collision mask back
    shape_1.collision_mask_rect.center = p1
    shape_2.collision_mask_rect.center = p2

    return bool(collision)

    def determineCollisionBroken(self, shape_1: Shape, shape_2: Shape):
        '''implementation of Continuous Collision Detection (CCD)'''
        
        # 1. Get the current positions, velocities, and dimensions of the shapes
        v1 = numpy.array(shape_1.getV())  # Velocity of shape_1
        v2 = numpy.array(shape_2.getV())  # Velocity of shape_2
        v_rel = v2 - v1  # Relative velocity
        
        p1 = numpy.array([shape_1.collision_mask_rect.x, shape_1.collision_mask_rect.y])  # Position (top-left corner) of shape_1
        p2 = numpy.array([shape_2.collision_mask_rect.x, shape_2.collision_mask_rect.y])  # Position (top-left corner) of shape_2

        size_1 = numpy.array([shape_1.collision_mask.get_size()[0], shape_1.collision_mask.get_size()[1]])  # Size of shape_1's bounding box
        size_2 = numpy.array([shape_2.collision_mask.get_size()[0], shape_2.collision_mask.get_size()[1]])  # Size of shape_2's bounding box

        # 2. Define boundaries of each shape (AABB boundaries)
        p1_min = p1  # top-left corner of shape_1
        p1_max = p1 + size_1  # bottom-right corner of shape_1
        p2_min = p2  # top-left corner of shape_2
        p2_max = p2 + size_2  # bottom-right corner of shape_2

        # 3. Calculate time of collision along both x and y axes
        def axis_collision(p1_min, p1_max, p2_min, p2_max, v_rel_axis):
            # Calculate t_enter (time when they start overlapping) and t_exit (time when they stop overlapping)
            if v_rel_axis > 0:
                t_enter = (p2_min - p1_max) / v_rel_axis
                t_exit = (p2_max - p1_min) / v_rel_axis
            elif v_rel_axis < 0:
                t_enter = (p2_max - p1_min) / v_rel_axis
                t_exit = (p2_min - p1_max) / v_rel_axis
            else:  # If velocity along the axis is 0, they won't collide on that axis
                if p1_max < p2_min or p2_max < p1_min:
                    return -float('inf'), float('inf')  # No overlap
                return 0, 1  # Overlap for the entire frame

            return t_enter, t_exit

        # 4. Calculate times of collision along the x-axis
        t_enter_x, t_exit_x = axis_collision(p1_min[0], p1_max[0], p2_min[0], p2_max[0], v_rel[0])

        # 5. Calculate times of collision along the y-axis
        t_enter_y, t_exit_y = axis_collision(p1_min[1], p1_max[1], p2_min[1], p2_max[1], v_rel[1])

        # 6. Find the latest time of entering and the earliest time of exiting
        t_enter = max(t_enter_x, t_enter_y)
        t_exit = min(t_exit_x, t_exit_y)

        # 7. If t_enter <= t_exit and 0 <= t_enter <= 1, a collision will happen within this frame
        if 0 <= t_enter <= t_exit <= 1:
            # Calculate positions at t_enter (time of collision)
            future_p1 = p1 + t_enter * v1
            future_p2 = p2 + t_enter * v2

            try:
                future_p1 = [int(future_p1[0]), int(future_p1[1])]
                future_p2 = [int(future_p2[0]), int(future_p2[1])]
            except:
                return False

            print(future_p1, future_p2)
            if future_p1[1] < -1000 or future_p2[1] < -1000: return False

            # Move the collision masks to the future positions for accurate detection
            shape_1.collision_mask_rect.topleft = future_p1
            shape_2.collision_mask_rect.topleft = future_p2

            # Check for overlap using the collision masks
            collision = shape_1.collision_mask.overlap(shape_2.collision_mask, [
                int(shape_2.collision_mask_rect.x - shape_1.collision_mask_rect.x),
                int(shape_2.collision_mask_rect.y - shape_1.collision_mask_rect.y)
            ])

            # Move collision masks back to original positions
            shape_1.collision_mask_rect.topleft = p1
            shape_2.collision_mask_rect.topleft = p2

            return bool(collision)

        return False

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

    print(Game(game_shape1, game_shape2, "team 0", "team 1", None, False, False).playGame())

def play_game():
    pygame.init()
    pygame.mixer.pre_init(44100, -16, 2, 512)
    pygame.mouse.set_visible(False)

    screen = pygame.display.set_mode((1920, 1080), pygame.NOFRAME)
    game_shape1, game_shape2 = get2Shapes()

    print(Game(game_shape1, game_shape2, "team 0", "team 1", screen).playGame())

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
    shape_data = ShapeData(-1, User(""), 1, 0, 1, 0, 130, 160, 100, 1, 1, 1, "", "", "")
    shape_data2 = ShapeData(-1, User(""), 1, 0, 1, 0, 50, 60, 100, 1, 1, 1, "", "", "")

    healthbar_images = []
    for i in range(0, 17):
        healthbar_images.append(pygame.image.load(f'shape_images/health/{i}.png').convert_alpha())
    
    for powerup in powerup_data:
        image = pygame.image.load(powerup_data[powerup][0])
        hud_images.append(pygame.transform.smoothscale(image, (20, 20)))
        powerup_images.append(pygame.transform.smoothscale(image, (40, 40)))

    face_images = []
    for i in range(0, 4):
        face_images.append(pygame.image.load(f'shape_images/0/{i}.png').convert_alpha())

    shape = Shape(shape_data, color_data[shape_data.color_id], 6, 1, face_images, hud_images, healthbar_images)
    group = Group()
    group.add(shape)

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

                if event.button == 1:
                    shape.state = 'growing'


        screen.fill((0, 0, 0))


        # if frames >= 40:
        #     shape.takeDamage(0.025)
           
        #     if frames <= 240:
        #         shape.r += 1
        #         shape.sections_to_render.append('all')

        group.update()
        group.draw(screen)
        

        
        pygame.display.flip()
        clock.tick()
        # print(clock.get_fps())
        

    # Quit Pygame
    pygame.quit()
    sys.exit()

def point_on_arc(percent, square_size):
    # Calculate the radius of the arc (the side length of the square)
    radius = square_size
    
    # Map percent (0-100) to angle (270° to 180°)
    start_angle = 270
    end_angle = 180
    angle = math.radians(start_angle - (start_angle - end_angle) * (percent / 100))
    
    # Calculate the x, y coordinates on the arc
    x = center_x + radius * math.cos(angle)
    y = center_y + radius * math.sin(angle)
    
    return (square_size-x*-1, y)

def newArt():
    pygame.init()
    screen = pygame.display.set_mode((1920, 1080))
    clock = pygame.time.Clock()
    frames = 0


    blue = pygame.image.load("shape_images/blue.png").convert_alpha()
    orange = pygame.image.load("shape_images/orange.png").convert_alpha()
    green = pygame.image.load("shape_images/green.png").convert_alpha()
    lemonlime = pygame.image.load("shape_images/lemonlime.png").convert_alpha()
    f0 = pygame.image.load("shape_images/0/0.png").convert_alpha()
    f1 = pygame.image.load("shape_images/0/1.png").convert_alpha()
    f2 = pygame.image.load("shape_images/0/2.png").convert_alpha()
    f3 = pygame.image.load("shape_images/0/3.png").convert_alpha()


    blue.blit(f0, [0, 0])
    orange.blit(f1, [0, 0])
    green.blit(f2, [0, 0])
    lemonlime.blit(f3, [0, 0])
    blue = pygame.transform.smoothscale(blue, [200, 200])
    orange = pygame.transform.smoothscale(orange, [200, 200])
    green = pygame.transform.smoothscale(green, [200, 200])
    lemonlime = pygame.transform.smoothscale(lemonlime, [200, 200])



    running = True
    while running:
        events = pygame.event.get()
        mouse_pos = pygame.mouse.get_pos()
        frames += 1

        for event in events:
            if event.type == pygame.QUIT:
                running = False

        screen.fill((0, 0, 0))

        screen.blit(blue, [0, 0])
        screen.blit(orange, [200, 0])
        screen.blit(green, [400, 0])
        screen.blit(lemonlime, [600, 0])


        pygame.display.flip()
        clock.tick(60)

def cleanImages(path, num_images):
    num_pixels = 0

    for i in range(num_images):
        image = pygame.image.load(f'{path}{i}.png')

        for x in range(0, image.get_size()[0]):
            for y in range(0, image.get_size()[1]):
                pixel = image.get_at((x, y))
            
                if x == 0 and y == 0: print(pixel)

                if pixel[3] <= 100:
                    image.set_at((x, y), (0, 0, 0, 0))
                    num_pixels += 1

        pygame.image.save(image, f'{path}new/{i}.png')

    print(num_pixels)

def game2():
    user1 = User("Camille")
    user2 = User("Patrick")
    # shape_data = ShapeData(1, user1, 'triangle', 0, 0, 1, 10, 40, 50, 100, 1, 1, 15, "", "dumbass", "")
    # shape_data2 = ShapeData(2, user2, 'circle', 0, 1, 1, 10, 40, 50, 100, 1, 1, 15, "", "dickhead", "")

    shape_data = ShapeData(1, user1, 'circle', 0, 0, 1, 3, 100, 110, 100, 1, 1, 1, "", "dumbass", "")
    shape_data2 = ShapeData(2, user2, 'circle', 0, 1, 1, 3, 50, 70, 100, 1, 1, 1, "", "dickhead", "")
    
    pygame.init()
    pygame.mixer.pre_init(44100, -16, 2, 512)
    screen = pygame.display.set_mode((1920, 1080))
    Game2(screen, shape_data, shape_data2, user1, user2).play()

def game3():
    user1 = User("Camille")
    user2 = User("Patrick")
    shape_data = ShapeData(1, user1, 'square', 0, 0, 1, 3, 12, 15, 100, 1, 1, 24, "", "", "")
    shape_data2 = ShapeData(2, user2, 'circle', 0, 1, 1, 3, 17, 20, 100, 1, 1, 24, "", "", "")
    
    pygame.init()
    screen = pygame.display.set_mode((1920, 1080))
    Game3(screen, shape_data, shape_data2, user1, user2).play()

def killfeed():
    user1 = User("Camille")
    user2 = User("Patrick")
    shape_data = ShapeData(1, user1, 'square', 0, 0, 1, 10, 30, 40, 100, 1, 1, 15, "", "", "")
    shape_data2 = ShapeData(2, user2, 'circle', 0, 1, 1, 10, 30, 40, 100, 1, 1, 15, "", "", "")

    # shape_data = ShapeData(1, user1, 'square', 0, 0, 1, 10, 100, 110, 100, 1, 1, 1, "", "dumbass", "")
    # shape_data2 = ShapeData(2, user2, 'circle', 0, 1, 1, 10, 100, 110, 100, 1, 1, 1, "", "dickhead", "")

    pygame.init()
    screen = pygame.display.set_mode((1920, 1080))
    clock = pygame.time.Clock()
    frames = 0

    # Main loop

    running = True
    while running:
        events = pygame.event.get()
        mouse_pos = pygame.mouse.get_pos()
        frames += 1

        for event in events:
            if event.type == pygame.QUIT:
                running = False

        screen.fill((0, 0, 0))
        
        
        pygame.display.flip()
        clock.tick()
        # print(clock.get_fps())
        

    # Quit Pygame
    pygame.quit()
    sys.exit()

# newArt()
# generateHealthBars()
# shape2()
# cleanImages('shape_images/healthbars/triangle/', 18)
game2()
# killfeed
# game3()
