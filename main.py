import pygame
from menu_files.menu import Menu

def main():
    pygame.init()
    pygame.mixer.pre_init(44100, -16, 2, 512)
    pygame.mouse.set_visible(False)
    
    Menu().start()
    pygame.quit()

main()