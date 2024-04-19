import pygame
from circledata import *

GRAVITY = 0.1  # Acceleration due to gravity
JUMP_FORCE = -2.5  # Initial force of the jump
MAX_JUMP_HEIGHT = 100  # Maximum height the character can jump

class PostGameShape(pygame.sprite.Sprite):
    def __init__(self, shape, yours = True, victory = False, keeps = False):
        super().__init__()
        self.shape = shape
        self.y = 1080/2

        if victory: face_img = 0
        else: face_img = 3

        self.image_full =  pygame.image.load("circles/{}/{}/{}.png".format(shape.face_id, colors[shape.color_id][0], face_img))
        self.image = pygame.transform.smoothscale(self.image_full, (301, 301))
        
        self.size = 301
        self.next_size = self.size
        self.pause = 0
        
        self.victory = victory
        self.velocity = 0

        if keeps: x = 275
        else: x = 450

        if yours: self.x = x
        else: self.x = 1920 - x

        self.next_x = self.x
        self.og_y = self.y
        self.rect = self.image.get_rect()
        self.rect.center = [self.x, self.y]

        self.grow_sound = pygame.mixer.Sound("sounds/grow.wav")
        self.shrink_sound = pygame.mixer.Sound("sounds/shrink.wav")


    def moveTo(self, x):
        self.next_x = x
        self.next_size = 1

        self.shrink_sound.play()

    def update(self):
        change_flag = False

        if self.size > self.next_size:
            self.size -= 10

            if self.size == 1:
                self.x = self.next_x
                self.next_size = 301
                self.pause = 60

            change_flag = True
            
        elif self.pause > 0:
            self.pause -= 1

            if self.pause == 0: self.grow_sound.play()

        elif self.size < self.next_size:
            self.size += 10
            change_flag = True

        if self.victory:
            self.velocity += GRAVITY

            if self.y >= self.og_y:
                self.velocity = 0
                self.y = self.og_y

                self.velocity = JUMP_FORCE

            self.y = int(self.y + self.velocity)

            if self.y < self.og_y - MAX_JUMP_HEIGHT:
                self.y = self.og_y - MAX_JUMP_HEIGHT

            change_flag = True

        if change_flag:
            self.image = pygame.transform.smoothscale(self.image_full, (self.size, self.size))
            self.rect = self.image.get_rect()
            self.rect.center = [self.x, self.y]

