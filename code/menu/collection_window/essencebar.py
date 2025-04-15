from pygame.locals import *
from pygame.mixer import Sound
from pygame.surface import Surface
from pygame.image import load
import pygame, math, numpy

from createdb import User

class EssenceBar2:
    def __init__(self, user: User, opponent = False):
        self.user = user
        self.opponent = opponent

        self.loadImagesAndSounds()
        
        # set initial values for bar control
        percent = (self.user.shape_essence % 1) * 100
        self.current_index = min(int(percent * (len(self.images) - 1) / 100), len(self.images) - 1)
        self.current_image = self.images[self.current_index]
        self.moving_direction = None # or 'up' or 'down'

        self.shown_essence = round(float(self.user.shape_essence), 2)
        self.new_essence = self.shown_essence
        self.changing = False
        self.frames = 0
        self.frames_moving = 0
        
    def loadImagesAndSounds(self):
        # load all images
        # extra elements on the front to properly handle empty bar
        # extra elements on the back to properly line up a 50% full bar
        self.images: list[Surface] = [Surface([10, 10], pygame.SRCALPHA, 32).convert_alpha()]
        for i in range(25, 0, -1):
            # if opponent essence bar, rotate images by 180 degrees
            image = load(f'assets/misc/shape_essence/shape_essence-{i}.png').convert_alpha()
            if self.opponent: image = pygame.transform.rotate(pygame.transform.flip(image, True, False), 180)
            self.images.append(image)

        padding_image = load(f'assets/misc/shape_essence/shape_essence-1.png').convert_alpha()
        if self.opponent: padding_image = pygame.transform.rotate(pygame.transform.flip(padding_image, True, False), 180)
        self.images.append(padding_image)

        self.rect = self.images[0].get_rect()
        self.rect.center = [40, 180] if not self.opponent else [40, 60]
        
        # load all sounds
        self.sounds = []
        for i in range(27):
            sound = Sound(f'assets/sounds/clanks/{i}.wav')
            sound.set_volume(0.05)
            self.sounds.append(sound)

        self.pop_sound = Sound('assets/sounds/pop.wav')
    
    def increaseEssenceBy(self, amount: float):
        if amount == 0: return
        
        self.new_essence += amount
        self.moving_direction = 'up' if amount > 0 else 'down'

    def updateCurrentIndex(self):
        before_index = self.current_index
        
        percent = (self.shown_essence % 1) * 100
        self.current_index = min(int(percent * (len(self.images) - 1) / 100), len(self.images) - 1)
        
        if self.current_index != before_index:
            self.sounds[self.current_index % len(self.sounds)].play()
        
    def update(self):
        '''update an essence bar which is responsible for making db calls if not opponent'''
        self.frames += 1

        frames_per_update = 2
        max_change = 0.08   
        base_change = 0.01  
        acceleration_rate = 0.0004
        
        if self.frames % frames_per_update != 0: return
        
        if self.moving_direction != None:
            
            self.changing = True
            self.frames_moving += 1

            # update the shown essence with some acceleration
            difference = abs(self.new_essence - self.shown_essence)
            time_based_speed = min(base_change + (self.frames_moving * acceleration_rate), max_change)
            essence_change_amount = max(base_change, time_based_speed * min(difference, 1.0))

            if self.moving_direction == 'up':
                self.shown_essence = min(self.shown_essence + essence_change_amount, self.new_essence)
                
                if self.shown_essence == self.new_essence:
                    self.moving_direction = None
                    self.changing = False
                    self.frames_moving = 0
            
            elif self.moving_direction == 'down':
                self.shown_essence = max(self.shown_essence - essence_change_amount, self.new_essence)
                
                if self.shown_essence <= self.new_essence:
                    self.moving_direction = None
                    self.changing = False
                    self.frames_moving = 0

            self.updateCurrentIndex()