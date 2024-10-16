import pygame, random
from typing import Union
from pygame.surface import Surface
from game_files.shape import Shape
from screen_elements.text import Text 

class Killfeed(pygame.sprite.Sprite):
    def __init__(self, count: int, left: Shape, action: str, action_img: Surface, background_imgs: list[Surface], tape_imgs: list[Surface], right: Shape = False):
        super().__init__()

        self.count = count
        self.left = left
        self.action = action
        self.action_img = action_img
        self.background_imgs = background_imgs
        self.tape_imgs = tape_imgs
        self.right = right
        self.frames = 0

        self.x = 1753
        self.y = 450 + (165 * count)
        self.next_y = self.y
        self.velocity = 0
        self.acceleration = 1
        self.alpha = 255

        # create surfaces
        self.background = self.background_imgs[1] if right else self.background_imgs[0]
        self.tape = self.tape_imgs[random.choice([1, 2, 3]) if right else random.choice([0, 2, 3])]

        self.image = Surface([self.background.get_size()[0] + 20, self.background.get_size()[1] + 20], pygame.SRCALPHA, 32)
        self.rect = self.image.get_rect()
        self.rect.center = [self.x, self.y]

        self.left_img = pygame.transform.smoothscale(self.left.shape_images[self.left.current_shape_image_id], [75, 75])
        self.left_rect = self.left_img.get_rect()
        self.left_rect.center = [90, 65] if right else [90, 70]

        if right:
            self.right_img = pygame.transform.smoothscale(self.right.shape_images[self.right.current_shape_image_id], [75, 75])
            self.right_rect = self.right_img.get_rect()
            self.right_rect.center = [245, 65]

        self.action_rect = self.action_img.get_rect()
        self.action_rect.center = [170, 70] if right else [180, 70]

        self.text = Text(self.getBlurb(), 19, self.background.get_size()[0]/2 + 10, 122, color='black')
        
        # draw surfaces
        self.image.blit(self.background, [10, 10])
        self.image.blit(self.left_img, self.left_rect)
        self.image.blit(self.action_img, self.action_rect)
        if right: self.image.blit(self.right_img, self.right_rect)
        self.image.blit(self.text.surface, self.text.rect)
        self.image.blit(self.tape, [self.background.get_size()[0]/2 - self.tape.get_size()[0]/2 + 10, 0])

    def getBlurb(self):
        '''generate some text to be displayed at the bottom of the killfeed'''

        kill_synonyms = 'clobbered destroyed annihilated smashed bonked ganked'.split(' ')
        kill_remarks = ['you should have seen it.', 'it was brutal.', 'shit was based.', 'call the amberlamps!', 'he need some milk!']
        warning_remarks = ['watch out!', 'stay clear!', 'neat.']
        healed_remarks = ['good as new.', 'that\'ll come in use.', 'all better :)']
        resurrect_remaks = ['praise god!', 'unbelievable.', 'hallelujah']
        left_name = f'{self.left.shape_data.name} {self.left.shape_id}'
        right_name = f'{self.right.shape_data.name} {self.right.shape_id}' if self.right else None

        if self.action.startswith('kill'):
            return [
                f'{left_name} {random.choice(kill_synonyms)} {right_name}.',
                random.choice(kill_remarks)
            ]
        elif self.action.startswith('pickup'):
            return [
                f'{left_name} picked up a',
                f'{self.action[7:].replace("_", " ")}. {random.choice(warning_remarks)}'
            ]
        elif self.action.startswith('heal'):
            return [
                f'{left_name} was healed.',
                f'{random.choice(healed_remarks)}'
            ]
        elif self.action.startswith('resurrect'):
            return [
                f'{left_name} resurrected {right_name}.',
                f'{random.choice(resurrect_remaks)}'
            ]
        
    def cycle(self, ):
        self.next_y -= 165
    
    def update(self, cycle = False):
        self.frames += 1 

        # if another killfeed element has disappeared 
        if cycle: self.cycle()
            
        # move if your position has changed
        if self.y != self.next_y:
            distance = abs(self.y - self.next_y)

            if distance > 50:
                self.velocity += self.acceleration
            else:
                self.velocity = max(1, distance * 0.2)

            self.y -= self.velocity

            if self.y < self.next_y:
                self.y = self.next_y

            # check if you are moving above the sticky note, if so, fade quickly
            if self.y < 450:
                self.alpha -= (450 - self.y) / 2
                
                if self.alpha <= 1: self.kill(); return 2
                
                self.image.set_alpha(self.alpha)

            self.rect.center = [self.x, self.y]

        # fade over time
        if self.frames >= 300 and self.alpha > 0:
            self.alpha -= 1
            
            if self.alpha <= 0: self.alpha = 0; self.kill(); return 1

            self.image.set_alpha(self.alpha)

        return 0
