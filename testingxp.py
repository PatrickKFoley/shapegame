import pygame
from xpbar import XpBar
import sys

# Initialize Pygame
pygame.init()

# Set up the display
width, height = 1920, 1080
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("White Screen")
clock = pygame.time.Clock()

bar = XpBar([300, 300], 6, 5)
bar.animating = True
bar_group = pygame.sprite.Group()
bar_group.add(bar)

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
