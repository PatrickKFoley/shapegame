import pygame, numpy, sys, os
from pygame.locals import *
from pygame.image import load
import sys
import math
import random
from createdb import Shape
from code.game.circledata import *
from threading import Thread
from code.game.powerup2 import Powerup
import time

import numpy as np
from scipy.io import wavfile
from scipy.signal import resample
import librosa
import soundfile as sf

from createdb import User, Shape as ShapeData
from code.game.circledata import colors as color_data
from code.game.circledata import powerup_data
from code.game.gamedata import color_data
from pygame.sprite import Group

from code.game.shape import Shape
from code.game.game2 import Game2
from code.menu.menu import Menu, CollectionWindow


from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from createdb import User, Shape as DbShape
from code.game.gamedata import color_names, shape_names

pygame.init()
pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.mixer.set_num_channels(16)
pygame.mouse.set_visible(False)

def game2():
    user1 = User("Camille", 'password')
    user2 = User("Patrick", 'password')
    shape_data = ShapeData(1, user1, 'rhombus', 0, 0, 1, 10, 40, 50, 100, 1, 1, 10, "", "guy", "")
    shape_data2 = ShapeData(2, user2, 'spiral', 0, 1, 1, 10, 40, 50, 100, 1, 1, 10, "", "dude", "")
    
    screen = pygame.display.set_mode((1920, 1080), pygame.NOFRAME)
    Game2(screen, shape_data, shape_data2, user1, user2).play()

def menu2(username = None, password = None):
    
    Menu().play(username, password)
    pygame.quit()

def generateEssenceSounds():
    

    input_filename = "sounds/clanks/0.wav"
    output_filename_template = "sounds/clanks/{}.wav"

    # Load the original sound file
    y, sr = librosa.load(input_filename, sr=None)

    # Set the pitch shift interval (in semitones)
    semitone_increase = 1  # Adjust this for more noticeable shifts
    num_files = 28

    for i in range(num_files):
        print(i)
        # Apply pitch shift by `i * semitone_increase` semitones
        y_shifted = librosa.effects.pitch_shift(y=y, sr=sr, n_steps=(i * semitone_increase))
        
        # Save the output file
        sf.write(output_filename_template.format(i), y_shifted, sr)
   
def generateNotificationShimmer():
    pygame.init()
    
    shimmer = pygame.image.load('assets/backgrounds/sticker shimmer/color shimmer.png')
    spot = pygame.image.load('assets/backgrounds/sticker shimmer/spot.png')
    mask = pygame.image.load('assets/backgrounds/sticker shimmer/mask.png')

    len = 349
    spot_len = 349
    
    start_x = -spot_len
    stop_x = 349
    
    cur_x = start_x
    
    count = 0
    max = 0
    
    while cur_x < stop_x:
        print(cur_x)
        
        image = pygame.Surface([len, 170], pygame.SRCALPHA, 32)
        
        for x in range(image.get_size()[0]):
            for y in range(image.get_size()[1]):
                
                if x+cur_x < 0 or x+cur_x >= len or mask.get_at([x, y])[3] == 0:
                    intensity = 0
                else:
                    intensity = min(spot.get_at([x+cur_x, y])[3] * 1.75, 255)
                    
                if intensity > max:
                    max = intensity
                
                if intensity == 0:
                    color = [0, 0, 0, 0]
                else:
                    color = [
                        shimmer.get_at([x, y])[0],
                        shimmer.get_at([x, y])[1],
                        shimmer.get_at([x, y])[2],
                        intensity
                    ]
                
                
                image.set_at([x, y], color)
                
        pygame.image.save(image, f'assets/backgrounds/sticker shimmer/{count}.png')
        
        cur_x += 20
        count += 1
    print(max)
  
def generateShapeBackgrounds():
    
    for shape in shape_names:
        
        directory = f'assets/shapes/backgrounds/{shape}'
        if not os.path.exists(directory):
            os.makedirs(directory)
            
            print(f'{shape} directory created, needs source image')
            continue
        
        shape_source = load(f'assets/shapes/backgrounds/{shape}/source.png')
        
        for color in color_names:
            
            color_source = load(f'assets/shapes/colors/{color}.png')
            new_image = pygame.Surface([shape_source.get_size()[0], shape_source.get_size()[1]], pygame.SRCALPHA, 32)
            
            for x in range(new_image.get_size()[0]):
                for y in range(new_image.get_size()[1]):
                    
                    
                    pixel = [
                        color_source.get_at([x, y])[0],
                        color_source.get_at([x, y])[1],
                        color_source.get_at([x, y])[2],
                        shape_source.get_at([x, y])[3]
                    ]
                
                    new_image.set_at((x, y), pixel)
                    
            pygame.image.save(new_image, f'assets/shapes/backgrounds/{shape}/{color}.png')
    
if len(sys.argv) > 1: 
    if sys.argv[1] == 'menu': 
        if len(sys.argv) < 4:
            menu2()
        elif len(sys.argv) == 4:
            menu2(sys.argv[2], sys.argv[3])
    elif sys.argv[1] == 'game': game2()
    elif sys.argv[1] == 'gen_shapes': generateShapeBackgrounds()