from pygame.locals import *
import pygame.mouse
from pygame.sprite import Group
from pygame.mixer import Sound
from pygame.transform import smoothscale
from pygame.surface import Surface
from pygame.image import load
import pygame, itertools, pytz, math, numpy, random

from createdb import User, Shape as ShapeData
from ..screen_elements.text import Text
from ..screen_elements.clickabletext import ClickableText
from ..screen_elements.arrow import Arrow
from ..screen_elements.button import Button
from ..game.gamedata import color_data, shape_data as shape_model_data, names, titles
from sqlalchemy import func, delete
from sqlalchemy.orm import Session


def generateRandomShape(user: User, session: Session):
    '''returns randomly generated ShapeData'''

    type = random.choices(['circle', 'triangle', 'square'], weights=[40, 40, 20], k=1)[0]
    face_id = 0
    color_id = random.randint(0, len(color_data)-1)
    density = 1
    velocity = shape_model_data[type].velocity + random.randint(-3, 3)
    radius_min = shape_model_data[type].radius_min + random.randint(-10, 10)
    radius_max = shape_model_data[type].radius_max + random.randint(-10, 10)
    health = shape_model_data[type].health + random.randint(-50, 50)
    dmg_x = round(shape_model_data[type].dmg_multiplier + (random.random() * random.choice([-1, 1])), 1)
    luck = shape_model_data[type].luck + random.randint(-5, 5)
    team_size = shape_model_data[type].team_size + random.randint(-3, 3)
    name = random.choice(names)
    title = titles[0]

    shape_data = ShapeData(user.id, user, type, face_id, color_id, density, velocity, radius_min, radius_max, health, dmg_x, luck, team_size, user.username, name, title)

    user.shape_tokens -= 1
    user.num_shapes += 1

    session.add(shape_data)
    session.commit()

    return shape_data

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


class CollectionShape(pygame.sprite.Sprite):
    def __init__(self, shape_data: ShapeData, position: int, session, new = False):
        super().__init__()

        self.shape_data = shape_data
        self.position = position
        self.session = session
        self.new = new
        
        self.x_selected = 705
        self.x = self.x_selected + position * 220
        self.y = 250
        self.next_y = self.y
        self.next_x = self.x
        self.v = 0
        self.a = 1.5
        self.alpha = 0 if new else 255

        self.generateSurfaces()

    def generateSurfaces(self):
        '''generate the surfaces for window stats, additional info, and shape image'''

        # shape image
        self.face_image = smoothscale(load(f'assets/shapes/faces/{self.shape_data.type}/{self.shape_data.face_id}/0.png').convert_alpha(), [190, 190])
        self.image = smoothscale(load(f'assets/shapes/backgrounds/{self.shape_data.type}/{color_data[self.shape_data.color_id].name}.png').convert_alpha(), [190, 190])

        self.image.blit(self.face_image, [0, 0])

        self.rect = self.image.get_rect()
        self.rect.center = [self.x, self.y]

        # stats surface
        self.stats_surface = Surface([580, 340], pygame.SRCALPHA, 32)
        self.stats_rect = self.stats_surface.get_rect()
        self.stats_rect.center = [450, 267]

        # determine all differences in shape value -> baseline shape value
        d_v = round(self.shape_data.velocity - shape_model_data[self.shape_data.type].velocity, 1)
        d_r = round(self.shape_data.radius_min - shape_model_data[self.shape_data.type].radius_min, 1)
        d_hp = round(self.shape_data.health - shape_model_data[self.shape_data.type].health, 1)
        d_dmg = round(self.shape_data.dmg_multiplier - shape_model_data[self.shape_data.type].dmg_multiplier, 1)
        d_luck = round(self.shape_data.luck - shape_model_data[self.shape_data.type].luck, 1)
        d_ts = round(self.shape_data.team_size - shape_model_data[self.shape_data.type].team_size, 1)
        
        texts = [
            # name
            Text(f'{self.shape_data.title} {self.shape_data.name}', 60, 245, 45, color=color_data[self.shape_data.color_id].text_color),

            # labels
            Text('level:', 40, 193, 90, 'topright'),
            Text('wins:', 40, 350, 90, 'topright'),
            Text('velocity:', 32, 193, 128, 'topright'),
            Text('radius:', 32, 193, 157, 'topright'),
            Text('health:', 32, 193, 188, 'topright'),
            Text('damage x:', 32, 193, 219, 'topright'),
            Text('luck:', 32, 193, 249, 'topright'),
            Text('team size:', 32, 193, 279, 'topright'),

            # values
            Text(f'{self.shape_data.level}', 38, 213, 90, 'topleft'),
            Text(f'{self.shape_data.num_wins}', 38, 380, 90, 'topleft'),
            Text(f'{self.shape_data.velocity}', 30, 213, 128, 'topleft'),
            Text(f'{self.shape_data.radius_min} - {self.shape_data.radius_max}', 30, 213, 157, 'topleft'),
            Text(f'{self.shape_data.health}', 30, 213, 188, 'topleft'),
            Text(f'{self.shape_data.dmg_multiplier}', 30, 213, 219, 'topleft'),
            Text(f'{self.shape_data.luck}', 30, 213, 249, 'topleft'),
            Text(f'{self.shape_data.team_size}', 30, 213, 279, 'topleft'),

            # addition/subtraction
            Text(str(d_v) if d_v < 0 else f'+{d_v}', 30, 400, 128, 'topright', 'red' if d_v < 0 else 'green'),
            Text(str(d_r) if d_r < 0 else f'+{d_r}', 30, 400, 157, 'topright', 'red' if d_r < 0 else 'green'),
            Text(str(d_hp) if d_v < 0 else f'+{d_hp}', 30, 400, 188, 'topright', 'red' if d_hp < 0 else 'green'),
            Text(str(d_dmg) if d_v < 0 else f'+{d_dmg}', 30, 400, 219, 'topright', 'red' if d_dmg < 0 else 'green'),
            Text(str(d_luck) if d_v < 0 else f'+{d_luck}', 30, 400, 249, 'topright', 'red' if d_luck < 0 else 'green'),
            Text(str(d_ts) if d_ts < 0 else f'+{d_ts}', 30, 400, 279, 'topright', 'red' if d_ts < 0 else 'green'),
        ]

        for text in texts:
            self.stats_surface.blit(text.surface, text.rect)

        # additional info
        self.info_surface = Surface([510, 300], pygame.SRCALPHA, 32)
        self.info_rect = self.info_surface.get_rect()
        self.info_rect.center = [1095, 250]

        utc_timezone = pytz.timezone('UTC')
        est_timezone = pytz.timezone('US/Eastern')

        obtained_on_datetime = utc_timezone.localize(self.shape_data.obtained_on).astimezone(est_timezone)
        created_on_datetime = utc_timezone.localize(self.shape_data.created_on).astimezone(est_timezone)
        count = self.session.query(func.count(ShapeData.id)).filter(ShapeData.type == self.shape_data.type, ShapeData.color_id == self.shape_data.color_id).scalar()

        texts = [
            Text(['obtained on:', f'{obtained_on_datetime.strftime("%m/%d/%Y, %H:%M")}'], 35, 250, 40),
            Text(['created on:', f'{created_on_datetime.strftime("%m/%d/%Y, %H:%M")}'], 35, 250, 110),
            Text(f'number of owners: {self.shape_data.num_owners}', 32, 250, 180),
            Text(f'created by: {self.shape_data.created_by}', 32, 250, 215),
            Text(f'your shape is 1 of {count}', 32, 250, 250),
        ]

        for text in texts:
            self.info_surface.blit(text.surface, text.rect)

        self.info_surface.set_alpha(0)
        
    def moveLeft(self):
        self.next_x -= 220

    def moveRight(self):
        self.next_x += 220

    def update(self):
        # adjust transparency
        if self.next_x < self.x_selected and self.x < self.x_selected and self.alpha > 0:
            self.alpha = max(self.alpha - 10 - abs(min(self.v, 25)), 0)

        elif self.next_x > self.x_selected-220 and self.x >= self.x_selected-220 and self.alpha < 255:
            self.alpha = min(self.alpha + 10 + abs(min(self.v, 25)), 255)

        if self.image.get_alpha() != self.alpha: self.image.set_alpha(self.alpha)

        # move down 
        if self.y != self.next_y:
            self.y += 10
            self.alpha = max(self.alpha - 20, 0)
            self.image.set_alpha(self.alpha)
            self.rect.center = [self.x, self.y]

            if self.alpha == 0:
                self.kill()

        # move into place
        if self.x == self.next_x: return

        # calculate the remaining distance to the target
        distance = abs(self.x - self.next_x)

        # apply acceleration while far from the target, decelerate when close
        if distance > 50:
            self.v += self.a
        else:
            self.v = max(1, distance * 0.2)

        # move the window towards the target position, snap in place if position is exceeded
        if self.x > self.next_x:
            self.x -= self.v

            if self.x < self.next_x:
                self.x = self.next_x

        elif self.x < self.next_x:
            self.x += self.v
            
            if self.x > self.next_x:
                self.x = self.next_x 

        # reset the velocity when the window reaches its target
        if self.x == self.next_x:
            self.v = 0

        self.rect.center = [self.x, self.y]

    def delete(self):
        self.next_y = 1000


class Selection(pygame.sprite.Sprite):
    def __init__(self, shape: ShapeData, position: int, num_shapes: int):
        super().__init__()
        
        self.shape_type = shape.type
        self.shape = shape
        self.position = position
        self.num_shapes = num_shapes
        
        self.surface_size = 40
        self.min_size = 25
        self.max_size = 35
        
        self.selected = position == 0
        self.hovered = False
        self.size = self.max_size if self.selected else self.min_size
        self.next_size = self.size
        
        self.image = Surface((self.surface_size, self.surface_size), pygame.SRCALPHA, 32)
        self.selected_surface = Surface((self.surface_size, self.surface_size), pygame.SRCALPHA, 32)
        self.unselected_surface = Surface((self.surface_size, self.surface_size), pygame.SRCALPHA, 32)
        self.rect = self.image.get_rect()
        
        width = max(self.num_shapes * 50, 75)
        self.x = (position + 1)* (width / (num_shapes + 1))
        self.rect.center = [self.x, 30]
        
        if self.shape_type == 'triangle':
            pygame.draw.polygon(self.selected_surface, 'black', [[self.surface_size/2, 0], [self.surface_size, self.surface_size], [0, self.surface_size]])
            pygame.draw.polygon(self.unselected_surface, 'gray', [[self.surface_size/2, 0], [self.surface_size, self.surface_size], [0, self.surface_size]])
        
        elif self.shape_type == 'square':
            self.selected_surface.fill('black')
            self.unselected_surface.fill('gray')
        
        elif self.shape_type == 'circle':
            pygame.draw.circle(self.selected_surface, 'black', [self.surface_size/2, self.surface_size/2], self.surface_size/2)
            pygame.draw.circle(self.unselected_surface, 'gray', [self.surface_size/2, self.surface_size/2], self.surface_size/2)

        shape_image = smoothscale(self.selected_surface if self.selected or self.hovered else self.unselected_surface, [self.size, self.size])
        rect = shape_image.get_rect()
        rect.center = self.surface_size/2, self.surface_size/2
        self.image.blit(shape_image, rect)

    def update(self):
        
        # check if a shape was added
        width = max(self.num_shapes * 50, 75)
        if self.x != (self.position + 1)* (width / (self.num_shapes + 1)): 
            self.x = (self.position + 1)* (width / (self.num_shapes + 1))
            
            self.rect.center = self.x, 30
        
        # shrink to unselected size if not hovered or selected
        if not self.hovered and not self.selected and self.next_size != 25:
            self.next_size = self.min_size
        
        # change size to match status
        if self.size != self.next_size:
            # print(self.position, self.size, self.next_size)
            # print('changing size')
            
            # grow
            if self.size < self.next_size:
                self.size = min(self.size + 1, self.next_size)
            # shrink
            else:
                self.size = max(self.size - 1, self.next_size)
                
            # reset surface
            self.image = Surface((self.surface_size, self.surface_size), pygame.SRCALPHA, 32)
            shape_image = smoothscale(self.selected_surface if self.selected or self.hovered else self.unselected_surface, [self.size, self.size])
            rect = shape_image.get_rect()
            rect.center = self.surface_size/2, self.surface_size/2
            self.image.blit(shape_image, rect)
        
        
class Selector:
    def __init__(self, shapes: list[ShapeData], center: list[int]):
        self.shapes = shapes
        self.num_shapes = len(shapes)
        self.center = center
        self.topleft = [850, 377]
        self.selected_index = 0
        
        self.w = max(max(self.num_shapes * 50, 75), 75)
        self.h = 60
        self.next_w = self.w
        
        self.surface = Surface((self.w, 60), pygame.SRCALPHA, 32)
        self.rect = self.surface.get_rect()
        # self.rect.center = center
        self.rect.topleft = self.topleft
        pygame.draw.rect(self.surface, 'black', [0, 0, self.w, self.h], border_radius=10)
        pygame.draw.rect(self.surface, 'white', [3, 3, self.w-6, self.h-6], border_radius=10)
        self.selections = Group()
        
        for count, shape in enumerate(self.shapes):
            self.selections.add(Selection(shape, count, self.num_shapes))
        
    def addShape(self, shape: ShapeData):
        self.selections.sprites()[self.selected_index].selected = False
        self.selected_index = 0
        self.num_shapes += 1
        
        for sprite in self.selections.sprites():
            sprite.position += 1
            sprite.num_shapes += 1
        
        selections_copy = self.selections.sprites()
        
        self.selections.empty()
        self.selections.add(Selection(shape, 0, self.num_shapes))
        self.selections.add(selections_copy)
        
        self.redrawSurface()
        
    def removeShape(self):
        
        removed_shape = self.selections.sprites()[self.selected_index]
        for sprite in self.selections.sprites():
            if sprite.position > removed_shape.position:
                sprite.position -= 1
        self.selections.remove(removed_shape)
        self.num_shapes -= 1
        
        if removed_shape.position == self.num_shapes: 
            self.selected_index -= 1
        
        new_selected = self.selections.sprites()[self.selected_index]
        new_selected.selected = True
        new_selected.next_size = new_selected.max_size
        
        
        
        self.redrawSurface()
        
    def redrawSurface(self):
        self.next_w = max(self.num_shapes * 50, 75)
        self.surface = Surface((self.w, 60), pygame.SRCALPHA, 32)
        # self.surface.fill((255, 255, 255))
        self.rect = self.surface.get_rect()
        # self.rect.center = self.center
        self.rect.topleft = self.topleft
        pygame.draw.rect(self.surface, 'black', [0, 0, self.w, self.h], border_radius=10)
        pygame.draw.rect(self.surface, 'white', [3, 3, self.w-6, self.h-6], border_radius=10)

    def update(self, mouse_pos, events):
        rel_mouse_pos = [mouse_pos[0] - self.rect.x, mouse_pos[1] - self.rect.y]
        
        for sprite in self.selections.sprites():
            if sprite.rect.collidepoint(rel_mouse_pos):
                sprite.hovered = True
                sprite.next_size = sprite.max_size
            else:
                sprite.hovered = False
        
        for event in events:
            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                for sprite in self.selections.sprites():
                    if sprite.rect.collidepoint(rel_mouse_pos):
                        # print('select')
                        print(sprite.position)
                        self.selected_index = sprite.position
                        
                        sprite.selected = True
                        sprite.next_size = sprite.max_size
                        
                        for sprite2 in self.selections.sprites():
                            if sprite.position != sprite2.position: 
                                # print('ya')
                                sprite2.selected = False
                                sprite2.hovered = False
                        
        if self.w != self.next_w:
            if self.w < self.next_w:
                self.w = min(self.w + 5, self.next_w)
            else:
                self.w = max(self.w - 5, self.next_w)
            
            self.surface = Surface((self.w, 60), pygame.SRCALPHA, 32)
            self.rect = self.surface.get_rect()
            self.rect.topleft = self.topleft
            # self.rect.center = self.center
        
        pygame.draw.rect(self.surface, 'black', [0, 0, self.w, self.h], border_radius=10)
        pygame.draw.rect(self.surface, 'white', [3, 3, self.w-6, self.h-6], border_radius=10)
        self.selections.draw(self.surface)
        self.selections.update()
        
        
class CollectionWindow:
    def __init__(self, user: User, session: Session):
        self.user = user
        self.session = session

        self.initCollectionWindow()
        self.initCollectionGroup()
        
        self.selector = Selector(self.user.shapes, [1200, 400])

    def initCollectionWindow(self):
        '''create the bottom collection window'''
        self.surface = Surface([1920, 493], pygame.SRCALPHA, 32)
        self.rect = self.surface.get_rect()
        self.rect.topleft = [0, 1030]

        # delete shape surface
        self.delete_surface = load('assets/paper/additional_shape_data.png').convert_alpha()
        self.delete_rect = self.delete_surface.get_rect()
        self.delete_rect.center = [1130, 250]

        self.delete_tape = load('assets/paper/tape_0_xl.png').convert_alpha()
        self.delete_tape_rect = self.delete_tape.get_rect()
        self.delete_tape_rect.center = [1140, 110]

        self.confirm_text = Text('delete shape?', 80, 1130, 175)
        self.warning = Text(['this action cannot', 'be undone'], 40, 1130, 240)
        self.yes_clickable = ClickableText('yes', 100, 1000, 325, color=[0, 200, 0])
        self.no_clickable = ClickableText('no', 100, 1260, 325, color=[255, 0, 0])

        self.shapes_button = Button('shapes', 50, [25, 25])
        self.question_button = Button('question', 40, [780, 131])
        self.question_button.disable()
        self.add_button = Button('add', 90, [81, 226])
        self.del_button = Button('trash', 40, [205, 131])
        self.heart_button = Button('heart', 40, [780, 400])

        # disable add button if user has no shape tokens
        if self.user.shape_tokens == 0: self.add_button.disable()

        self.clickables = [
            self.shapes_button, self.question_button, 
            self.add_button,    self.del_button, 
            self.yes_clickable, self.no_clickable,
            self.heart_button
        ]

        self.background = load('assets/backgrounds/collection_window.png').convert_alpha()
        self.background_rect = self.background.get_rect()
        self.background_rect.topleft = [0, 1080]
        
        self.paper = load('assets/paper/additional_shape_data.png').convert_alpha()
        self.paper_rect = self.paper.get_rect()
        self.paper_rect.center = [1095, 250]

        self.tape_surface = load('assets/paper/tape_0_xl.png')
        self.tape_rect = self.tape_surface.get_rect()
        self.tape_rect.center = [1105, 110]

        self.shape_token_text = Text(f'{self.user.shape_tokens}', 35 if self.user.shape_tokens < 10 else 30, 108, 200, color=('black' if self.user.shape_tokens > 0 else 'red'))

        # essence bar 
        self.essence_bar = EssenceBar(self.user)

        self.y = 1080
        self.next_y = 1080
        self.v = 0
        self.a = 1.5
        self.opened = False
        self.info_alpha = 0

        self.selected_index = 0
        self.selected_shape: ShapeData | None = None
        self.collection_shapes = Group()
        self.deleted_shapes = Group()

        self.delete_clicked = False
        
        self.woosh_sound = Sound('assets/sounds/woosh.wav')

    def initCollectionGroup(self):
        '''create Collection shapes for newly logged in user'''

        for count, shape_data in enumerate(self.user.shapes):
            new_shape = CollectionShape(shape_data, count, self.session)
            self.collection_shapes.add(new_shape)
            
            # set selected shape if user logs in with shapes
            if count == 0: 
                self.selected_shape = new_shape
                self.heart_button.selected = self.selected_shape.shape_data.id = self.user.favorite_id

        # if user has 1 or 0 shapes, disable delete button and arrows
        if self.user.num_shapes <= 1:
            self.del_button.disable()

        # if user has at least 1 shape, enable question button
        if self.user.num_shapes >= 1: self.question_button.enable()

    def positionWindow(self):
        # update window positions
        if self.y != self.next_y:
        
            # calculate the remaining distance to the target
            distance = abs(self.y - self.next_y)

            # apply acceleration while far from the target, decelerate when close
            if distance > 50:
                self.v += self.a
            else:
                self.v = max(1, distance * 0.2)

            # move the window towards the target position, snap in place if position is exceeded
            if self.y > self.next_y:
                self.y -= self.v

                if self.y < self.next_y:
                    self.y = self.next_y

            elif self.y < self.next_y:
                self.y += self.v
                
                if self.y > self.next_y:
                    self.y = self.next_y 

            # reset the velocity when the window reaches its target
            if self.y == self.next_y:
                self.v = 0

            self.rect.topleft = [0, self.y - 50]

    def userGenerateShape(self):
        '''handle the user adding a shape to their collection'''
        if self.user.shape_tokens == 0: return

        # move all shapes to original position
        while self.selected_index != 0:
            self.selected_index -= 1

            for shape in self.collection_shapes:
                shape.moveRight()

        # create shape in database
        shape_data = generateRandomShape(self.user, self.session)

        # add new collection shape to the front of the list
        new_shape = CollectionShape(shape_data, -1, self.session, True)
        collection_shapes_copy = self.collection_shapes.sprites()
        self.collection_shapes.empty()
        self.collection_shapes.add(itertools.chain([new_shape, collection_shapes_copy]))

        # adjust selected shape and shape positions to introduce new shape from the right
        self.selected_shape = new_shape
        for shape in self.collection_shapes:
            shape.moveRight()

        # recreate shape tokens text
        self.shape_token_text = Text(f'{self.user.shape_tokens}', 35 if self.user.shape_tokens < 10 else 30, 108, 200, color=('black' if self.user.shape_tokens > 0 else 'red'))

        # disable add button if user used last token
        if self.user.shape_tokens == 0: self.add_button.disable()

        # enable buttons
        if self.user.num_shapes > 1: 
            self.del_button.enable()

        if self.user.num_shapes >= 1: self.question_button.enable()
        
        # add shape to selector
        self.selector.addShape(shape_data)
        
        self.heart_button.selected = self.selected_shape.shape_data.id == self.user.favorite_id

    def deleteSelectedShape(self):
        # don't let user delete their only shape
        if self.user.num_shapes == 1: return

        # remove shape from sprites first
        removed = False
        for count, sprite in enumerate(self.collection_shapes.sprites()):
            
            # found the shape to delete
            if count == self.selected_index and not removed:
                self.selector.removeShape()

                # delete db entry
                self.user.num_shapes -= 1
                self.user.shape_essence += sprite.shape_data.level * 0.25

                self.session.execute(delete(ShapeData).where(ShapeData.id == sprite.shape_data.id))
                self.session.commit()

                # remove from sprite group
                self.collection_shapes.remove(sprite)
                self.deleted_shapes.add(sprite)

                sprite.delete()

                removed = True

                # if the right-most shape was deleted, move all shapes to the right
                if count == self.user.num_shapes:
                    print()
                    for sprite in self.collection_shapes.sprites():
                        sprite.moveRight()

                    self.selected_index -= 1
                
                self.selected_shape = self.collection_shapes.sprites()[self.selected_index]
                self.heart_button.select = self.selected_shape.shape_data.id == self.user.favorite_id
                
                
            
            elif removed: sprite.moveLeft()

        # close the delete window
        self.delete_clicked = False

        # if user now has one shape, disable delete button
        if self.user.num_shapes == 1: 
            self.del_button.disable()


    def handleInputs(self, mouse_pos, events):
        mouse_pos = [mouse_pos[0], mouse_pos[1] - self.y + 50]

        # update icons

        for clickable in self.clickables:
            clickable.update(mouse_pos)

        # check if the user is hovering over the question mark on collection window
        if not self.question_button.disabled:
            if self.question_button.rect.collidepoint(mouse_pos) and self.info_alpha < 254: 
                self.info_alpha += 15
                self.info_alpha = min(self.info_alpha, 255)

            elif self.question_button.rect.collidepoint(mouse_pos) and self.info_alpha == 255: pass

            elif self.info_alpha > 0: 
                self.info_alpha -= 15
                self.info_alpha = max(self.info_alpha, 0)

        # handle events
        for event in events:
            if event.type != MOUSEBUTTONDOWN: return

            if self.shapes_button.rect.collidepoint(mouse_pos):
                self.toggle()

            # if the window is closed the only inputs we want to accept are the open button
            if not self.opened: return

            elif self.add_button.rect.collidepoint(mouse_pos):
                self.userGenerateShape()
                self.woosh_sound.play()

            # show the delete confirmation screen
            elif self.del_button.rect.collidepoint(mouse_pos) and not self.del_button.disabled:
                self.delete_clicked = not self.delete_clicked

            elif self.delete_clicked and self.yes_clickable.rect.collidepoint(mouse_pos):
                self.deleteSelectedShape()
                self.woosh_sound.play()

            elif self.heart_button.rect.collidepoint(mouse_pos):
                self.markSelectedFavorite()

            # if user clicks anywhere, close delete screen
            else:
                self.delete_clicked = False

    def markSelectedFavorite(self):
        
        self.heart_button.selected = True
        
        self.session.query(User).filter(User.id == self.user.id).update({User.favorite_id: self.selected_shape.shape_data.id})

        self.session.commit()

    def update(self, mouse_pos, events):
        '''update position of the collection window'''
        rel_mouse_pos = [mouse_pos[0], mouse_pos[1] - self.y + 50]
        
        # check if the selector has changed
        if self.selected_index != self.selector.selected_index:
            print(self.selected_index, self.selector.selected_index)
            while (self.selected_index > self.selector.selected_index):
                # move right, index -
                self.selected_index -= 1
                for sprite in self.collection_shapes.sprites():
                    sprite.moveRight()
                    
            while (self.selected_index < self.selector.selected_index):
                # move right, index -
                self.selected_index += 1
                for sprite in self.collection_shapes.sprites():
                    sprite.moveLeft()
                    
            print(self.selected_index, self.selector.selected_index)
            print(self.collection_shapes.sprites())
            self.selected_shape = self.collection_shapes.sprites()[self.selected_index]
            
            self.heart_button.selected = self.selected_shape.shape_data.id == self.user.favorite_id

        # update returns true when shape essence amount is altered, needing commit
        if self.essence_bar.update(): 
            self.session.commit()
            self.shape_token_text = Text(f'{self.user.shape_tokens}', 35 if self.user.shape_tokens < 10 else 30, 108, 200, color=('black' if self.user.shape_tokens > 0 else 'red'))

        if self.essence_bar.changing and not self.del_button.disabled:
            self.del_button.disable()
        elif not self.essence_bar.changing and self.del_button.disabled and self.user.num_shapes > 1:
            self.del_button.enable()

        self.handleInputs(mouse_pos, events)

        self.collection_shapes.update()
        self.deleted_shapes.update()
        self.selector.update(rel_mouse_pos, events)
        
        self.positionWindow()

        self.renderSurface()

    def toggle(self):
        self.opened = not self.opened

        if self.opened: self.next_y = 1080 - self.background.get_size()[1]
        else: self.next_y = 1080

    def renderSurface(self):
        self.surface.blit(self.background, [0, 50])

        # draw buttons
        [self.surface.blit(clickable.surface, clickable.rect) for clickable in self.clickables if clickable not in [self.yes_clickable, self.no_clickable]]

        # sprites
        self.collection_shapes.draw(self.surface)
        self.deleted_shapes.draw(self.surface)

        # shape tokens
        self.surface.blit(self.shape_token_text.surface, self.shape_token_text.rect)

        # render essence bar
        self.surface.blit(self.essence_bar.images[self.essence_bar.current_index], self.essence_bar.rect)

        # render delete surface
        if self.delete_clicked:
            self.surface.blit(self.delete_surface, self.delete_rect)

            self.surface.blit(self.confirm_text.surface, self.confirm_text.rect)
            self.surface.blit(self.warning.surface, self.warning.rect)
            self.surface.blit(self.yes_clickable.surface, self.yes_clickable.rect)
            self.surface.blit(self.no_clickable.surface, self.no_clickable.rect)

            # tape overtop writing
            self.surface.blit(self.delete_tape, self.delete_tape_rect)
            
        # render selector
        self.surface.blit(self.selector.surface, self.selector.rect)
        
        # draw additional info (self.info_alpha increased on hover)
        if self.info_alpha >= 0: 
            if self.paper.get_alpha() != self.info_alpha:
                self.paper.set_alpha(self.info_alpha)
                self.tape_surface.set_alpha(self.info_alpha)
                
                if self.selected_shape != None: self.selected_shape.info_surface.set_alpha(self.info_alpha)

            self.surface.blit(self.paper, self.paper_rect)
            self.surface.blit(self.tape_surface, self.tape_rect)
        
        # if we have a selected shape, show its information
        if self.selected_shape != None: 
            self.surface.blit(self.selected_shape.info_surface, self.selected_shape.info_rect)
            self.surface.blit(self.selected_shape.stats_surface, self.selected_shape.stats_rect)

