import pygame
# from screen_elements.xpbar import XpBar
from createdb import User, Shape as ShapeData
from game_files.circledata import colors as color_data
import sys

# Initialize Pygame
pygame.init()

# Set up the display
width, height = 1920, 1080
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("White Screen")
clock = pygame.time.Clock()

shape_images = []
hud_images = []
shape_data = ShapeData(-1, User(""), 1, 1, 1, 1, 50, 60, 100, 1, 1, 1, "", "", "")


for i in range(0, 4):
    # TODO assuming 100px extra on the radius will be plenty for now, confirm somehow later
    shape_images.append(pygame.transform.smoothscale(pygame.image.load("circles/{}/{}/{}.png".format(shape_data.face_id, color_data[shape_data.color_id][0], i)), (shape_data.radius_max + 100, shape_data.radius_max + 100)))
        

# Main loop
while True:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            break

    # Fill the screen with white color
    screen.fill((0,0,0))

    bar_group.update()
    bar_group.draw(screen)

    # Update the display
    pygame.display.flip()
    # clock.tick(60)
