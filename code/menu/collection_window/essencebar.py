from pygame.locals import *
from pygame.mixer import Sound
from pygame.surface import Surface
from pygame.image import load
import pygame, math, numpy

from createdb import User


class EssenceBar:
    def __init__(self, user: User):
        self.user = user
        self.changing = False
        self.frames = 0

        # load all images
        # extra elements on the front to properly handle empty bar
        # extra elements on the back to properly line up a 50% full bar
        self.images: list[Surface] = [Surface([10, 10], pygame.SRCALPHA, 32), Surface([10, 10], pygame.SRCALPHA, 32)]
        for i in range(25, 0, -1):
            self.images.append(load(f'assets/misc/shape_essence/shape_essence-{i}.png').convert_alpha())
        self.images.append(load(f'assets/misc/shape_essence/shape_essence-1.png').convert_alpha())
        self.images.append(load(f'assets/misc/shape_essence/shape_essence-1.png').convert_alpha())

        self.rect = self.images[0].get_rect()
        self.rect.center = [40, 180]

        percent = (self.user.shape_essence % 1) * 100
        self.current_index = min(int(percent * (len(self.images) - 1) / 100), len(self.images) - 1)
        self.next_index = self.current_index
        self.current_image = self.images[self.current_index]

        self.current_essence = self.user.shape_essence
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

                self.loops -= 1
                self.user.shape_tokens += 1
                self.user.shape_essence -= 1
                return True

            return

        # check if the user deleted a shape
        if self.current_essence != self.user.shape_essence:
            self.changing = True

            # check if we need to loop the bar, if so, start looping immediately
            if self.user.shape_essence >= 1:
                self.loops = math.floor(self.user.shape_essence)
                self.current_essence = self.user.shape_essence
                return 
            
            percent = (self.user.shape_essence % 1) * 100
            self.next_index = max(min(int(percent * (len(self.images) - 1) / 100), len(self.images) - 1), 1)
            self.current_essence = self.user.shape_essence

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

            self.user.shape_tokens += 1
            self.user.shape_essence -= 1
            self.pop_sound.play()

            return True
