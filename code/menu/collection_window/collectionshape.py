from pygame.locals import *
from pygame.transform import smoothscale
from pygame.surface import Surface
from pygame.image import load
import pygame, pytz

from createdb import Shape as ShapeData
from ...screen_elements.text import Text
from ...game.gamedata import color_data, shape_data as shape_model_data
from sqlalchemy import func


class CollectionShape(pygame.sprite.Sprite):
    def __init__(self, shape_data: ShapeData, position: int, num_shapes: int, session, new = False, opponent = False):
        super().__init__()

        self.shape_data = shape_data
        self.position = position
        self.num_shapes = num_shapes
        self.session = session
        self.new = new
        self.opponent = opponent
        self.frames = 0
        self.frame_died = 0
        self.x_selected = 705
        self.x = self.x_selected + position * 220
        self.y = 250
        self.next_y = self.y
        self.next_x = self.x
        self.v = 0
        self.a = 1.5
        self.alpha = 0 if new else 255
        self.alpha_lock = False

        self.generateSurfaces()

    def reposition(self, position: int, num_shapes: int):
        self.position = position
        self.num_shapes = num_shapes
        self.x = self.x_selected + position * 220
        self.next_x = self.x

        self.rect.center = self.x, self.y

        self.redrawPosition(position, num_shapes)

    def redrawPosition(self, position: int, num_shapes: int):
        self.position = position
        self.num_shapes = num_shapes

        # erase last three elements of texts
        self.eraseTextFromBackground(self.stats_surface, self.texts.pop())
        self.eraseTextFromBackground(self.stats_surface, self.texts.pop())
        self.eraseTextFromBackground(self.stats_surface, self.texts.pop())

        text1 = Text(str(self.position+1), 40, 475, 280)
        text2 = Text('/', 40, 490, 300)
        text3 = Text(str(self.num_shapes), 40, 515, 310, color=('red' if self.num_shapes==30 else 'black'))

        self.texts.append(text1)
        self.texts.append(text2)
        self.texts.append(text3)

        text1.draw(self.stats_surface)
        text2.draw(self.stats_surface)
        text3.draw(self.stats_surface)

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
        self.stats_alpha = 255
        self.next_stats_alpha = 255

        # determine all differences in shape value -> baseline shape value
        d_v = round(self.shape_data.velocity - shape_model_data[self.shape_data.type].velocity, 1)
        d_r = round(self.shape_data.radius_min - shape_model_data[self.shape_data.type].radius_min, 1)
        d_hp = round(self.shape_data.health - shape_model_data[self.shape_data.type].health, 1)
        d_dmg = round(self.shape_data.dmg_multiplier - shape_model_data[self.shape_data.type].dmg_multiplier, 1)
        d_luck = round(self.shape_data.luck - shape_model_data[self.shape_data.type].luck, 1)
        d_ts = round(self.shape_data.team_size - shape_model_data[self.shape_data.type].team_size, 1)

        # format strings for differences
        d_v_s = f'{d_v}' if d_v < 0 else f'+{d_v}'
        d_r_s = f'{d_r}' if d_r < 0 else f'+{d_r}'
        d_hp_s = f'{d_hp}' if d_hp < 0 else f'+{d_hp}'
        d_dmg_s = f'{d_dmg}' if d_dmg < 0 else f'+{d_dmg}'
        d_luck_s = f'{d_luck}' if d_luck < 0 else f'+{d_luck}'
        d_ts_s = f'{d_ts}' if d_ts < 0 else f'+{d_ts}'

        text_color = 'white' if self.opponent else 'black'
        
        self.texts = [
            # name
            Text(f'{self.shape_data.title} {self.shape_data.name}', 60, 245, 45, color=color_data[self.shape_data.color_id].text_color, outline_color=text_color),

            # labels
            Text('level:', 40, 193, 90, 'topright', text_color),
            Text('wins:', 40, 350, 90, 'topright', text_color),
            Text('velocity:', 32, 193, 128, 'topright', text_color),
            Text('radius:', 32, 193, 157, 'topright', text_color),
            Text('health:', 32, 193, 188, 'topright', text_color),
            Text('damage x:', 32, 193, 219, 'topright', text_color),
            Text('luck:', 32, 193, 249, 'topright', text_color),
            Text('team size:', 32, 193, 279, 'topright', text_color),

            # values
            Text(f'{self.shape_data.level}', 38, 213, 90, 'topleft', text_color),
            Text(f'{self.shape_data.num_wins}', 38, 380, 90, 'topleft', text_color),
            Text(f'{self.shape_data.velocity}', 30, 213, 128, 'topleft', text_color),
            Text(f'{self.shape_data.radius_min} - {self.shape_data.radius_max}', 30, 213, 157, 'topleft', text_color),
            Text(f'{self.shape_data.health}', 30, 213, 188, 'topleft', text_color),
            Text(f'{self.shape_data.dmg_multiplier}', 30, 213, 219, 'topleft', text_color),
            Text(f'{self.shape_data.luck}', 30, 213, 249, 'topleft', text_color),
            Text(f'{self.shape_data.team_size}', 30, 213, 279, 'topleft', text_color),

            # addition/subtraction
            Text(d_v_s, 30, 400, 128, 'topright', 'red' if d_v < 0 else 'green'),
            Text(d_r_s, 30, 400, 157, 'topright', 'red' if d_r < 0 else 'green'),
            Text(d_hp_s, 30, 400, 188, 'topright', 'red' if d_hp < 0 else 'green'),
            Text(d_dmg_s, 30, 400, 219, 'topright', 'red' if d_dmg < 0 else 'green'),
            Text(d_luck_s, 30, 400, 249, 'topright', 'red' if d_luck < 0 else 'green'),
            Text(d_ts_s, 30, 400, 279, 'topright', 'red' if d_ts < 0 else 'green'),

            # position KEEP THESE AS LAST 3 ELEMENTS
            Text(str(self.position+1), 40, 475, 280, color=text_color),
            Text('/', 40, 490, 300, color=text_color),
            Text(str(self.num_shapes), 40, 515, 310, color=text_color)
        ]

        for text in self.texts:
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
            Text(f'this shape is 1 of {count}', 32, 250, 250),
        ]

        for text in texts:
            self.info_surface.blit(text.surface, text.rect)

        self.info_surface.set_alpha(0)
        
    def regenerateStats(self):
        # stats surface
        self.stats_surface = Surface([580, 340], pygame.SRCALPHA, 32)
        self.stats_rect = self.stats_surface.get_rect()
        self.stats_rect.center = [450, 267]
        self.stats_alpha = 255
        self.next_stats_alpha = 255

        # determine all differences in shape value -> baseline shape value
        d_v = round(self.shape_data.velocity - shape_model_data[self.shape_data.type].velocity, 1)
        d_r = round(self.shape_data.radius_min - shape_model_data[self.shape_data.type].radius_min, 1)
        d_hp = round(self.shape_data.health - shape_model_data[self.shape_data.type].health, 1)
        d_dmg = round(self.shape_data.dmg_multiplier - shape_model_data[self.shape_data.type].dmg_multiplier, 1)
        d_luck = round(self.shape_data.luck - shape_model_data[self.shape_data.type].luck, 1)
        d_ts = round(self.shape_data.team_size - shape_model_data[self.shape_data.type].team_size, 1)

        # format strings for differences
        d_v_s = f'{d_v}' if d_v < 0 else f'+{d_v}'
        d_r_s = f'{d_r}' if d_r < 0 else f'+{d_r}'
        d_hp_s = f'{d_hp}' if d_hp < 0 else f'+{d_hp}'
        d_dmg_s = f'{d_dmg}' if d_dmg < 0 else f'+{d_dmg}'
        d_luck_s = f'{d_luck}' if d_luck < 0 else f'+{d_luck}'
        d_ts_s = f'{d_ts}' if d_ts < 0 else f'+{d_ts}'

        text_color = 'white' if self.opponent else 'black'
        
        self.texts = [
            # name
            Text(f'{self.shape_data.title} {self.shape_data.name}', 60, 245, 45, color=color_data[self.shape_data.color_id].text_color, outline_color=text_color),

            # labels
            Text('level:', 40, 193, 90, 'topright', text_color),
            Text('wins:', 40, 350, 90, 'topright', text_color),
            Text('velocity:', 32, 193, 128, 'topright', text_color),
            Text('radius:', 32, 193, 157, 'topright', text_color),
            Text('health:', 32, 193, 188, 'topright', text_color),
            Text('damage x:', 32, 193, 219, 'topright', text_color),
            Text('luck:', 32, 193, 249, 'topright', text_color),
            Text('team size:', 32, 193, 279, 'topright', text_color),

            # values
            Text(f'{self.shape_data.level}', 38, 213, 90, 'topleft', text_color),
            Text(f'{self.shape_data.num_wins}', 38, 380, 90, 'topleft', text_color),
            Text(f'{self.shape_data.velocity}', 30, 213, 128, 'topleft', text_color),
            Text(f'{self.shape_data.radius_min} - {self.shape_data.radius_max}', 30, 213, 157, 'topleft', text_color),
            Text(f'{self.shape_data.health}', 30, 213, 188, 'topleft', text_color),
            Text(f'{self.shape_data.dmg_multiplier}', 30, 213, 219, 'topleft', text_color),
            Text(f'{self.shape_data.luck}', 30, 213, 249, 'topleft', text_color),
            Text(f'{self.shape_data.team_size}', 30, 213, 279, 'topleft', text_color),

            # addition/subtraction
            Text(d_v_s, 30, 400, 128, 'topright', 'red' if d_v < 0 else 'green'),
            Text(d_r_s, 30, 400, 157, 'topright', 'red' if d_r < 0 else 'green'),
            Text(d_hp_s, 30, 400, 188, 'topright', 'red' if d_hp < 0 else 'green'),
            Text(d_dmg_s, 30, 400, 219, 'topright', 'red' if d_dmg < 0 else 'green'),
            Text(d_luck_s, 30, 400, 249, 'topright', 'red' if d_luck < 0 else 'green'),
            Text(d_ts_s, 30, 400, 279, 'topright', 'red' if d_ts < 0 else 'green'),

            # position KEEP THESE AS LAST 3 ELEMENTS
            Text(str(self.position+1), 40, 475, 280, text_color),
            Text('/', 40, 490, 300, text_color),
            Text(str(self.num_shapes), 40, 515, 310, text_color)
        ]

        for text in self.texts:
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
            Text(f'this shape is 1 of {count}', 32, 250, 250),
        ]

        for text in texts:
            self.info_surface.blit(text.surface, text.rect)

        self.info_surface.set_alpha(0)
        
        self.redrawPosition(self.position, self.num_shapes)

    def eraseTextFromBackground(self, background: Surface, text: Text):
        '''erase the given text from the given background by setting all pixels beneath the text's rect to transparent '''
        
        if text == None: return

        x_offset, y_offset = text.rect.topleft

        for x in range(text.rect.width):
            for y in range(text.rect.height):
                x_abs, y_abs = x_offset + x, y_offset + y
                background.set_at((x_abs, y_abs), (0, 0, 0, 0))

        del text

    def moveLeft(self):
        self.next_x -= 220

    def moveRight(self):
        self.next_x += 220

    def update(self):

        self.frames += 1

        if self.frames - self.frame_died > 60 and self.frame_died != 0:
            self.kill()

        # adjust stats transparenct
        if self.stats_alpha != self.next_stats_alpha:

            if self.stats_alpha > self.next_stats_alpha:
                self.stats_alpha = max(self.stats_alpha - 10, 0)
            else:
                self.stats_alpha = min(self.stats_alpha + 10, 255)

            self.stats_surface.set_alpha(self.stats_alpha)

        # adjust transparency
        if self.next_x < self.x_selected and self.x < self.x_selected and self.alpha > 0 and not self.alpha_lock:
            self.alpha = max(self.alpha - 10 - abs(min(self.v, 25)), 0)

        elif self.next_x > self.x_selected-220 and self.x >= self.x_selected-220 and self.alpha < 255 and not self.alpha_lock:
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
