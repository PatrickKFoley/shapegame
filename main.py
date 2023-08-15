import pygame, os, sqlite3
from pygame.locals import *
from circledata import *
from menu import Menu

def generateAllCircles():
    print("GENERATING ALL CIRCLES - THIS WILL TAKE A MOMENT ON FIRST RUN\n")
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

def createDatabase():
    connection = sqlite3.connect("shapegame.db")
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER,
            username TEXT PRIMARY KEY
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS shapes (
            id INTEGER PRIMARY KEY,
            owner_id INTEGER
        )
    """)

    # cursor.execute("""
    #     INSERT INTO users VALUES
    #         (1, "Pat"),
    #         (2, "Aiden")         
    # """)

    # cursor.execute("""
    #     INSERT INTO shapes VALUES
    #         (1, 1),
    #         (2, 1),
    #         (3, 2),
    #         (4, 2)       
    # """)

    connection.commit()
    connection.close()

def main():
    # print(pygame.font.get_fonts()); exit
    generateAllCircles()
    # createDatabase()

    pygame.init()
    pygame.mixer.pre_init(44100, -16, 2, 512)
    pygame.mouse.set_visible(False)
    Menu().start()
    pygame.quit()

main()