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
        self.next_index = self.current_index
        self.current_image = self.images[self.current_index]
        self.moving_direction = None # or 'up' or 'down'

        self.shown_essence = round(float(self.user.shape_essence % 1), 2)
        self.new_essence = self.shown_essence
        self.changing = False
        self.frames = 0
        
    def loadImagesAndSounds(self):
        # load all images
        # extra elements on the front to properly handle empty bar
        # extra elements on the back to properly line up a 50% full bar
        self.images: list[Surface] = [Surface([10, 10], pygame.SRCALPHA, 32), Surface([10, 10], pygame.SRCALPHA, 32)]
        for i in range(25, 0, -1):

            # if opponent essence bar, rotate images by 180 degrees
            image = load(f'assets/misc/shape_essence/shape_essence-{i}.png').convert_alpha()
            if self.opponent: image = pygame.transform.rotate(pygame.transform.flip(image, True, False), 180)
            self.images.append(image)

        padding_image = load(f'assets/misc/shape_essence/shape_essence-1.png').convert_alpha()
        if self.opponent: padding_image = pygame.transform.rotate(pygame.transform.flip(padding_image, True, False), 180)
        self.images.append(padding_image)
        self.images.append(padding_image)

        self.rect = self.images[0].get_rect()
        self.rect.center = [40, 180] if not self.opponent else [40, 60]
        
        # load all sounds
        self.sounds = [
            Sound(numpy.zeros(80000, dtype=numpy.int16)),
            Sound(numpy.zeros(80000, dtype=numpy.int16)),
        ]
        for i in range(27):
            sound = Sound(f'assets/sounds/clanks/{i}.wav')
            sound.set_volume(0.05)
            self.sounds.append(sound)

        self.pop_sound = Sound('assets/sounds/pop.wav')
    
    def increaseEssenceBy(self, amount: float):
        if amount == 0: return
        
        self.new_essence += amount
        self.moving_direction = 'up' if amount > 0 else 'down'
        
        percent = (self.new_essence % 1) * 100
        self.next_index = min(int(percent * (len(self.images) - 1) / 100), len(self.images) - 1)
        
    def updateCurrentIndex(self):
        before_index = self.current_index
        
        percent = (self.shown_essence % 1) * 100
        self.current_index = min(int(percent * (len(self.images) - 1) / 100), len(self.images) - 1)
        
        if self.current_index != before_index:
            self.sounds[self.current_index % len(self.sounds)].play()
        
    def update(self):
        '''update an essence bar which is responsible for making db calls if not opponent'''

        max_index = 27
        frames_per_update = 2
        essence_change_amount= 0.01

        self.frames += 1
        
        if self.frames % frames_per_update != 0: return
        
        if self.moving_direction != None:
            self.changing = True
            
            if self.moving_direction == 'up':
                self.shown_essence += essence_change_amount
                if self.shown_essence + essence_change_amount >= self.new_essence:
                    self.moving_direction = None
                    self.changing = False
            
            else:
                self.shown_essence -= essence_change_amount
                if self.shown_essence - essence_change_amount <= self.new_essence:
                    self.moving_direction = None
                    self.changing = False
                    
            self.updateCurrentIndex()
            
                

       

class EssenceBar:
    def __init__(self, user: User, opponent = False):
        self.user = user
        self.opponent = opponent
        self.changing = False
        self.frames = 0

        # self.starting_essence = self.user.shape_essence
        # self.starting_tokens = self.user.shape_tokens

        # load all images
        # extra elements on the front to properly handle empty bar
        # extra elements on the back to properly line up a 50% full bar
        self.images: list[Surface] = [Surface([10, 10], pygame.SRCALPHA, 32), Surface([10, 10], pygame.SRCALPHA, 32)]
        for i in range(25, 0, -1):

            # if opponent essence bar, rotate images by 180 degrees
            image = load(f'assets/misc/shape_essence/shape_essence-{i}.png').convert_alpha()
            if self.opponent: image = pygame.transform.rotate(pygame.transform.flip(image, True, False), 180)
            self.images.append(image)

        padding_image = load(f'assets/misc/shape_essence/shape_essence-1.png').convert_alpha()
        if self.opponent: padding_image = pygame.transform.rotate(pygame.transform.flip(padding_image, True, False), 180)
        self.images.append(padding_image)
        self.images.append(padding_image)

        self.rect = self.images[0].get_rect()
        self.rect.center = [40, 180] if not self.opponent else [40, 60]

        percent = (self.user.shape_essence % 1) * 100
        self.current_index = min(int(percent * (len(self.images) - 1) / 100), len(self.images) - 1)
        self.next_index = self.current_index
        self.current_image = self.images[self.current_index]

        self.current_essence = round(float(self.user.shape_essence), 2)
        self.new_essence = round(float(self.current_essence), 2) # for use of opponent essence bar
        self.loops = 0

        self.sounds = [
            Sound(numpy.zeros(80000, dtype=numpy.int16)),
            Sound(numpy.zeros(80000, dtype=numpy.int16)),
        ]
        for i in range(27):
            sound = Sound(f'assets/sounds/clanks/{i}.wav')
            sound.set_volume(0.05)
            self.sounds.append(sound)

        self.pop_sound = Sound('assets/sounds/pop.wav')
        
    def update(self):
        '''update an essence bar which is responsible for making db calls if not opponent'''

        max_index = 27
        frames_per_update = 5

        self.frames += 1

        # loop
        while self.loops > 0:
            self.next_index = max_index

            if self.frames % frames_per_update == 0: 
                self.current_index += 1
                self.sounds[self.current_index % len(self.sounds)].play()

            # if bar is full, empty
            if self.current_index == self.next_index and self.frames % frames_per_update == 0: 
                self.pop_sound.play()
                self.current_index = 0
                self.next_index = 1

                if self.opponent:
                    self.loops -= 1
                    self.new_essence -= 1
                else:
                    self.loops -= 1
                    self.user.shape_tokens += 1
                    self.user.shape_essence -= 1

                self.pop_sound.play()
                return 'fake' if self.opponent else 'real'

            return

        # check if the user deleted a shape
        current_essence = self.new_essence if self.opponent else self.user.shape_essence
        if self.current_essence != current_essence:
            self.changing = True

            # check if we need to loop the bar, if so, start looping immediately
            if current_essence >= 1:
                self.loops = math.floor(current_essence)
                self.current_essence = current_essence
                return 
            
            percent = (current_essence % 1) * 100
            self.next_index = max(min(int(percent * (len(self.images) - 1) / 100), len(self.images) - 1), 1)
            self.current_essence = current_essence

        # check if image has to change
        if self.current_index != self.next_index:
            if self.frames % frames_per_update == 0: 
                
                # change image, play sound
                self.current_index += 1
                self.sounds[self.current_index % len(self.sounds)].play()

        else: self.changing = False

        # if bar is full, empty
        if self.current_index == max_index and self.frames % frames_per_update == 0:
            self.current_index = 0
            self.next_length = 1
            self.pop_sound.play()

            if self.opponent:
                self.new_essence -= 1
                return 'fake'
            else:
                self.user.shape_tokens += 1
                self.user.shape_essence -= 1
                return 'real'