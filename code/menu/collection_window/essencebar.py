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

        self.loadAssets()
        
        # current essence bar image
        percent = (self.user.shape_essence % 1) * 100
        self.current_index = min(int(percent * (len(self.images) - 1) / 100), len(self.images) - 1)
        self.current_image = self.images[self.current_index]
        
        # essence values, new is updated by increaseEssenceBy(), shown is updated by update() to always move towards new
        self.shown_essence = round(float(self.user.shape_essence), 2)
        self.new_essence = self.shown_essence

        # misc attributes
        self.moving_direction = None # or 'up' or 'down'
        self.changing = False
        self.frames = 0
        self.frames_moving = 0
        
    def loadAssets(self):
        '''load all images and sounds for the essence bar. images loaded for opponent are rotated by 180 degrees'''

        # extra element on the front to properly handle empty bar
        # extra element on the back to properly line up a 50% full bar
        self.images: list[Surface] = [Surface([10, 10], pygame.SRCALPHA, 32).convert_alpha()]
        
        # load all essence images
        num_essence_images = 25
        for i in range(num_essence_images, 0, -1):  
            
            image = load(f'assets/misc/shape_essence/shape_essence-{i}.png').convert_alpha()
            if self.opponent: image = pygame.transform.rotate(pygame.transform.flip(image, True, False), 180)
            self.images.append(image)

        # load padding image
        padding_image = load(f'assets/misc/shape_essence/shape_essence-1.png').convert_alpha()
        if self.opponent: padding_image = pygame.transform.rotate(pygame.transform.flip(padding_image, True, False), 180)
        self.images.append(padding_image)

        # set essence bar position
        self.rect = self.images[0].get_rect()
        self.rect.center = [40, 180] if not self.opponent else [40, 60]
        
        # load all sounds
        
        # essence "chime" sounds
        self.sounds = []
        for i in range(27):
            sound = Sound(f'assets/sounds/clanks/{i}.wav')
            sound.set_volume(0.05)
            self.sounds.append(sound)

        # "pop" sound, for when the essence passes a new bar threshold
        self.pop_sound = Sound('assets/sounds/pop.wav')
    
    # ---- ESSENCE BAR CONTROL ----

    def increaseEssenceBy(self, amount: float):
        '''increase the essence bar by a given amount. sets moving_direction'''

        if amount == 0: return
        
        self.new_essence += amount
        self.moving_direction = 'up' if amount > 0 else 'down'

    def updateCurrentIndex(self):
        '''update the current image index of the essence bar. plays a sound when the index changes'''

        before_index = self.current_index
        
        # update current index
        percent = (self.shown_essence % 1) * 100
        self.current_index = min(int(percent * (len(self.images) - 1) / 100), len(self.images) - 1)
        
        # play sound if index has changed
        if self.current_index != before_index:
            self.sounds[self.current_index % len(self.sounds)].play()
        
    def update(self):

        self.frames += 1

        frames_per_update = 2
        if self.frames % frames_per_update != 0: return

        
        # update the shown essence with some acceleration
        if self.moving_direction != None:

            # values for speed of essence bar change
            max_change = 0.08   
            base_change = 0.01  
            acceleration_rate = 0.0004
            
            # update state regarding movement
            self.changing = True
            self.frames_moving += 1 

            # calculate the amount to change the essence by
            difference = abs(self.new_essence - self.shown_essence)
            time_based_speed = min(base_change + (self.frames_moving * acceleration_rate), max_change)
            essence_change_amount = max(base_change, time_based_speed * min(difference, 1.0))

            # perform the change, stop movement if the shown essence has reached the new essence
            if self.moving_direction == 'up':
                self.shown_essence = min(self.shown_essence + essence_change_amount, self.new_essence)
                
                if self.shown_essence == self.new_essence:
                    self.moving_direction = None
                    self.changing = False
                    self.frames_moving = 0
            
            else:
                self.shown_essence = max(self.shown_essence - essence_change_amount, self.new_essence)
                
                if self.shown_essence <= self.new_essence:
                    self.moving_direction = None
                    self.changing = False
                    self.frames_moving = 0

            self.updateCurrentIndex()