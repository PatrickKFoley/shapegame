# whatt

import pygame, os
from pygame.locals import *
from game_files.circledata import *
from menu_files.menu import Menu

def generateAllCircles():
    for color in colors:
        for id in range(0, 5):
            if os.path.isdir("circles/{}/{}".format(id, color[0])):
                pass
            else:
                print("Generating all {} images".format(color[0]))
                # check for any special colors
                if type(color[0]) == type("string"):
                    os.mkdir("circles/{}/{}".format(id, color[0]))
                    for face in range(0, 4):
                        path = "circles/{}/{}.png".format(id, face)
                        image = pygame.image.load(path)

                        background = pygame.image.load("circles/{}".format(color[1]))

                        # loop through image, replace green pixels
                        for j in range(0, image.get_size()[0]):
                            for k in range(0, image.get_size()[1]):
                                pixel = image.get_at((j, k))
                                if pixel[0] <= 100 and pixel[1] >= 150 and pixel[2] <= 100:
                                    image.set_at((j, k), background.get_at((j, k)))
                                elif pixel[0] <= 100 and 100 <= pixel[1] <= 150 and pixel[2] <= 100:
                                    image.set_at((j, k), color[2])
                                elif 100 <= pixel[0] <= 150 and pixel[1] >= 200 and 100 <= pixel[2] <= 150:
                                    image.set_at((j, k), background.get_at((j, k)))

                        pygame.image.save(image, "circles/{}/{}/{}.png".format(id, color[0], face))

                # generate shapes as normal
                else:
                    os.mkdir("circles/{}/{}".format(id, color[0]))
                    for face in range(0, 4):
                        path = "circles/{}/{}.png".format(id, face)
                        image = pygame.image.load(path)

                        # loop through image, replace green pixels
                        for j in range(0, image.get_size()[0]):
                            for k in range(0, image.get_size()[1]):
                                pixel = image.get_at((j, k))
                                if pixel[0] <= 100 and pixel[1] >= 150 and pixel[2] <= 100:
                                    image.set_at((j, k), color[1])
                                elif pixel[0] <= 100 and 100 <= pixel[1] <= 150 and pixel[2] <= 100:
                                    image.set_at((j, k), color[3])
                                elif 100 <= pixel[0] <= 150 and pixel[1] >= 200 and 100 <= pixel[2] <= 150:
                                    image.set_at((j, k), color[2])

                        pygame.image.save(image, "circles/{}/{}/{}.png".format(id, color[0], face))

def main():
    pygame.init()
    pygame.mixer.pre_init(44100, -16, 2, 512)
    pygame.mouse.set_visible(False)
    
    Menu().start()
    pygame.quit()

# generateAllCircles()
main()