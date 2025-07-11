from pygame.locals import *
from pygame.sprite import Group
from pygame.mixer import Sound
from pygame.surface import Surface
from pygame.image import load
import pygame, itertools
from sqlalchemy import func, delete
from sqlalchemy.orm import Session

from createdb import User, Shape as ShapeData, generateRandomShape
from ...screen_elements.text import Text
from ...screen_elements.clickabletext import ClickableText
from ...screen_elements.button import Button
from .lvlupbutton import LvlUpButton
from .deletebutton import DeleteButton

from .collectionshape import CollectionShape
from .selector import Selector
from .essencebar import EssenceBar2 as EssenceBar
from ...screen_elements.networknameplate import NetworkNameplate
from ...server.connectionmanager import ConnectionManager
from sharedfunctions import clearSurfaceBeneath, getEssenceCost
from code.game.gamedata import titles

COLLECTION = "COLLECTION"
NETWORK = "NETWORK"
TRANSITION = "TRANSITION"

class CollectionWindow:
    def __init__(self, user: User, session: Session, opponent = False):
        self.user = user
        self.session = session
        self.is_opponent = opponent
        '''True if collection belongs to an opponent'''

        self.initCollectionWindow()
        self.initCollectionGroup()

    def initCollectionWindow(self):
        '''load all assets and initialize attributes for the window itself'''
        
        self.mode = COLLECTION if not self.is_opponent else NETWORK
        self.connection_manager: None | ConnectionManager = None

        # main surface
        self.surface = Surface([1920, 493], pygame.SRCALPHA, 32).convert_alpha()
        self.rect = self.surface.get_rect()
        self.rect.topleft = [0, 1030]

        # load screen elements
        self.essence_bar = EssenceBar(self.user, self.is_opponent)
        self.nameplate = NetworkNameplate(self.user, self.is_opponent)

        self.button = Button('shapes', 50, [25, 25], fast_off=True)
        self.question_button = Button('question_inverted' if self.is_opponent else 'question', 40, [780, 131])
        self.up_button = LvlUpButton([710, 105], self.lvlUpSelectedShape)
        self.add_button = Button('add', 90, [81, 226] if not self.is_opponent else [81, 292])
        self.del_button = DeleteButton([315, 105], self.deleteSelectedShape)
        self.heart_button = Button('heart', 40, [780, 400])

        self.lvl_increase_text = Text('+1', 30, 385, 175, color='yellow', outline_color='black', fast_off=True, align='topleft')
        self.hp_increase_text = Text('+5', 30, 560, 275, color='yellow', outline_color='black', fast_off=True, align='topleft')
        self.dmg_increase_text = Text('+0.1', 30, 560, 305, color='yellow', outline_color='black', fast_off=True, align='topleft')
        self.luck_increase_text = Text('+0.1', 30, 560, 335, color='yellow', outline_color='black', fast_off=True, align='topleft')
        self.team_increase_text = Text('+1', 30, 560, 365, color='yellow', outline_color='black', fast_off=True, align='topleft')
        self.shape_token_text = Text("", 1, 1, 1)
        self.updateShapeTokenText()

        self.screen_elements = [
            self.button,                self.question_button, 
            self.add_button,            self.del_button,
            self.heart_button,          self.up_button, 
            self.hp_increase_text,      self.dmg_increase_text, 
            self.luck_increase_text,    self.team_increase_text,
            self.lvl_increase_text,     self.shape_token_text
        ]

        # disable add shape button if user has no shape tokens
        if int(self.user.shape_essence) == 0: 
            self.add_button.disable()
            # TODO: ensure this case is handled fine by up button
            # self.up_button.disable()

        # load background images
        side = 'top' if self.is_opponent else 'bottom'
        self.background = load(f'assets/backgrounds/collection_window/{side}.png').convert_alpha()
        self.background_hearts = load(f'assets/backgrounds/collection_window/{side}_hearts.png').convert_alpha()
        self.background_rect = self.background.get_rect()
        self.background_rect.topleft = [0, 1080]
        
        # load images for additional shape information
        self.info_alpha = 0
        self.paper = load('assets/paper/additional_shape_data.png').convert_alpha()
        self.paper_rect = self.paper.get_rect()
        self.paper_rect.center = [1095, 250]

        self.tape_surface = load('assets/paper/tape_0_xl.png').convert_alpha()
        self.tape_rect = self.tape_surface.get_rect()
        self.tape_rect.center = [1105, 110]

        # window positioning attributes
        self.opened_y = (1080 - self.background.get_size()[1]) if not self.is_opponent else 0
        self.closed_y = 1080 if not self.is_opponent else - self.background.get_size()[1]
        self.y = self.closed_y
        self.next_y = self.y
        self.v = 0
        self.a = 1.5
        
        # window state attributes
        self.opened = False
        self.fully_closed = True if not self.is_opponent else False
        self.fully_opened = False
        self.essence_bar_changing = self.essence_bar.changing

        # attributes for shape selection
        self.selected_index = 0
        self.selected_shape: ShapeData | None = None
        
        # sprite groups
        self.collection_shapes = Group()
        self.deleted_shapes = Group()
        
        # load sounds
        self.woosh_sound = Sound('assets/sounds/woosh.wav')
        self.lvl_up_sound = Sound('assets/sounds/levelup.wav')
        self.lvl_up_sound.set_volume(0.5)

    def initCollectionGroup(self):
        '''initalize Collection shapes for window's user'''

        # clear sprite group if it holds any sprites
        self.collection_shapes.empty()

        # sort shapes to have favorite at the front
        shapes: list[ShapeData] = list(self.user.shapes)
        sorted_shapes = sorted(
            shapes,
            key=lambda obj: (obj.id != self.user.favorite_id, obj.id)
        )

        # create sprites
        for count, shape_data in enumerate(sorted_shapes):
            new_shape = CollectionShape(shape_data, count, self.user.num_shapes, self.session, opponent=self.is_opponent)
            self.collection_shapes.add(new_shape)

        # set selected shape to first shape in group
        self.selected_shape = None if len(self.collection_shapes) == 0 else self.collection_shapes.sprites()[0]

        # initialize selector
        self.selector = Selector(self.collection_shapes, [1200, 400], inverted=self.is_opponent)

        # update elements based on selected shape
        if self.selected_shape == None: self.del_button.disable()
        
        else:

            # update the level up cost for the selected shape
            self.up_button.updateCost(getEssenceCost(self.selected_shape.shape_data.level), self.user.shape_essence)

            # update button states if selected shape is favorite
            if self.selected_shape.shape_data.id == self.user.favorite_id:
                self.del_button.disable()
                self.heart_button.select()

    # ---- USER ACTION HELPERS ----

    def userGenerateShape(self):
        '''handle the user adding a shape to their collection'''

        # don't let user generate shape if they have no essence or have max shapes
        if int(self.user.shape_essence) == 0 or self.user.num_shapes == 30: return

        # move all shapes to original position
        while self.selected_index != 0:
            self.selected_index -= 1

            for shape in self.collection_shapes:
                shape.moveRight()

        # create shape in database
        shape_data = generateRandomShape(self.user, self.session)
        self.essence_bar.increaseEssenceBy(-1)

        # add new collection shape to the front of the list
        new_shape = CollectionShape(shape_data, -1, self.user.num_shapes, self.session, True)
        collection_shapes_copy = self.collection_shapes.sprites()
        self.collection_shapes.empty()
        self.collection_shapes.add(itertools.chain([new_shape, collection_shapes_copy]))

        # adjust selected shape and shape positions to introduce new shape from the right
        self.selected_shape = new_shape
        for shape in self.collection_shapes:
            shape.moveRight()

        # disable add button if user used last token
        if int(self.user.shape_essence) == 0: 
            self.add_button.disable()
            self.up_button.disable()

        # enable question button if it was disabled
        if self.question_button.disabled: self.question_button.enable()
        
        # add shape to selector
        self.selector.addShape(shape_data)
        
        # toggle heart button
        self.heart_button.selected = self.selected_shape.shape_data.id == self.user.favorite_id
        if self.mode == COLLECTION: 
            # disable delete button if selected shape is favorite or user has only one shape
            # keep disabled if in network mode
            self.del_button.disable() if self.selected_shape.shape_data.id == self.user.favorite_id or self.user.num_shapes == 1 else self.del_button.enable()

        # reposition shapes
        [sprite.redrawPosition(position, self.user.num_shapes) for position, sprite in enumerate(self.collection_shapes.sprites())]

    def removeSelectedShape(self):
        '''called when a loser loses their shape after a network match'''

        # remove shape from sprites first
        removed = False
        for count, sprite in enumerate(self.collection_shapes.sprites()):
            sprite: CollectionShape
            
            # found the shape to delete
            if count == self.selected_index and not removed:

                self.selector.removeShape()

                # remove from sprite group
                self.collection_shapes.remove(sprite)
                self.deleted_shapes.add(sprite)

                sprite.moveLeft()
                sprite.frame_died = sprite.frames

                removed = True

                # if the right-most shape was deleted, move all shapes to the right
                if count == len(self.collection_shapes):
                    for sprite in self.collection_shapes.sprites():
                        sprite.moveRight()

                    self.selected_index -= 1
                
                # update selected shape and button states
                if self.selected_index >= 0:
                    self.selected_shape = self.collection_shapes.sprites()[self.selected_index]
                    if self.mode == COLLECTION: self.del_button.disable() if self.selected_shape.shape_data.id == self.user.favorite_id else self.del_button.enable()
            
                else:
                    self.selected_shape = None
                    if self.mode == COLLECTION: self.del_button.disable()

            # if a sprite has already been removed, you move to the left
            elif removed: sprite.moveLeft()

        # redraw positions of shapes
        [sprite.redrawPosition(position, self.user.num_shapes) for position, sprite in enumerate(self.collection_shapes.sprites())]

    def deleteSelectedShape(self):
        '''called when user deletes shape while looking at their collection'''
        
        # stop the button from being clicked again immediately
        self.del_button.clicked = False

        # don't let user delete their only shape
        if self.user.num_shapes == 1: return

        # remove shape from sprites first
        removed = False
        for count, sprite in enumerate(self.collection_shapes.sprites()):
            sprite: CollectionShape
            
            # found the shape to delete
            if count == self.selected_index and not removed:
                
                removed = True

                # reward user with essence
                essence_amount = max(sprite.shape_data.level * 0.25, 0.15)
                self.user.shape_essence += essence_amount
                self.essence_bar.increaseEssenceBy(essence_amount)

                # delete shape from db
                self.user.num_shapes -= 1
                self.session.execute(delete(ShapeData).where(ShapeData.id == sprite.shape_data.id))
                self.session.commit()

                # remove from sprites from groups
                self.collection_shapes.remove(sprite)
                self.deleted_shapes.add(sprite)
                sprite.delete()
                self.selector.removeShape()

                # if the right-most shape was deleted, move all shapes to the right
                if count == self.user.num_shapes:
                    for sprite in self.collection_shapes.sprites():
                        sprite.moveRight()

                    self.selected_index -= 1
                
                # update selected shape and button states
                self.selected_shape = self.collection_shapes.sprites()[self.selected_index]
                self.heart_button.selected = self.selected_shape.shape_data.id == self.user.favorite_id
                if self.mode == COLLECTION: self.del_button.disable() if self.selected_shape.shape_data.id == self.user.favorite_id or self.user.num_shapes == 1 else self.del_button.enable()
                
            # if a sprite has already been removed, you move to the left
            elif removed: sprite.moveLeft()

        # if user now has one shape, disable delete button
        if self.user.num_shapes == 1: 
            self.del_button.disable()

        # reposition shapes
        [sprite.redrawPosition(position, self.user.num_shapes) for position, sprite in enumerate(self.collection_shapes.sprites())]

    def lvlUpSelectedShape(self):
        '''called when user levels up a shape'''

        # stop the button from being clicked again immediately
        self.up_button.clicked = False

        # get cost of level up
        cost = getEssenceCost(self.selected_shape.shape_data.level)

        # update essence bar and user's essence
        self.essence_bar.increaseEssenceBy(-cost)
        self.user.shape_essence -= cost

        # update shape data
        self.selected_shape.shape_data.level += 1
        self.selected_shape.shape_data.title = 'god' if self.selected_shape.shape_data.level > len(titles) else titles[self.selected_shape.shape_data.level]
        
        # update shape stats
        self.selected_shape.shape_data.health += 5
        self.selected_shape.shape_data.dmg_multiplier = round(self.selected_shape.shape_data.dmg_multiplier + 0.1, 1)
        self.selected_shape.shape_data.luck = round(self.selected_shape.shape_data.luck + 0.1, 1)

        # update text elements showing stat increases
        # if the text is already visible, update the text to increase the value
        # otherwise, set the text to the initial value
        if self.lvl_increase_text.alpha > 0:
            self.lvl_increase_text.updateText(f'+{int(self.lvl_increase_text.text) + 1}')
            self.hp_increase_text.updateText(f'+{int(self.hp_increase_text.text) + 5}')
            self.dmg_increase_text.updateText(f'+{round(float(self.dmg_increase_text.text) + 0.1, 1)}')
            self.luck_increase_text.updateText(f'+{round(float(self.luck_increase_text.text) + 0.1, 1)}')
        else:
            self.lvl_increase_text.updateText(f'+1')
            self.hp_increase_text.updateText(f'+5')
            self.dmg_increase_text.updateText(f'+0.1')
            self.luck_increase_text.updateText(f'+0.1')

        # turn on text elements for a duration
        on_duration = 300
        self.lvl_increase_text.turnOnFor(on_duration)
        self.hp_increase_text.turnOnFor(on_duration)
        self.dmg_increase_text.turnOnFor(on_duration)
        self.luck_increase_text.turnOnFor(on_duration)

        # every 5 levels increase team size
        if self.selected_shape.shape_data.level % 5 == 0:
            self.selected_shape.shape_data.team_size += 1
            self.team_increase_text.turnOnFor(on_duration)

        self.session.commit()

        # update stats and cost surfaces
        self.collection_shapes.sprites()[self.selected_index].generateStats()
        self.up_button.updateCost(getEssenceCost(self.selected_shape.shape_data.level), self.user.shape_essence)

        # disable add button if user used last token
        if int(self.user.shape_essence) == 0: self.add_button.disable()
        self.lvl_up_sound.play()

    def markSelectedFavorite(self):
        '''called when user marks a shape as their favorite'''

        # don't let user mark a favorite if they have no shapes
        if self.selected_shape == None: return
        
        # update heart button and delete button states
        self.heart_button.selected = True
        self.del_button.disable()
        
        # update user's favorite shape in db
        self.session.query(User).filter(User.id == self.user.id).update({User.favorite_id: self.selected_shape.shape_data.id})
        self.session.commit()

        # rerender nameplate
        self.nameplate.rerenderName()

    def updateShapeTokenText(self, text: str = None):
        '''update the shape token text to reflect the current essence'''

        if text == None:
            text = str(int(self.essence_bar.shown_essence))

        self.shape_token_text.updateText(
            text, 
            (('white' if self.is_opponent else 'black') if int(self.user.shape_essence) > 0 else 'red'),
            35 if int(self.essence_bar.shown_essence) < 10 else 30, 
            108, 
            200 if not self.is_opponent else 320,
        )

    # ---- GROUP MANAGEMENT HELPERS ----

    def sortGroup(self):
        '''sort collection group oldest (first) - youngest, favorite at the front'''

        group: list[CollectionShape] = list(self.collection_shapes)
        sorted_group = sorted(
            group,
            key=lambda obj: (obj.shape_data.id != self.user.favorite_id, obj.shape_data.id)
        )
        self.collection_shapes.empty()
        self.collection_shapes.add(sorted_group)

    def renumberGroup(self):
        '''redraw the positions of the shapes in the group to reflect their current positions'''

        num_shapes = len(self.collection_shapes.sprites())

        for count, shape in enumerate(self.collection_shapes.sprites()):
            shape: CollectionShape

            shape.redrawPosition(count, num_shapes)

    def moveSpritesHome(self):
        '''move sprites to their original positions (all the way to the right)'''

        # set selector index to 0
        self.selector.selected_index = 0

        # move sprites to the right until they are all at the right-most position
        while (self.selected_index > self.selector.selected_index):
                
            self.selected_index -= 1
            for sprite in self.collection_shapes.sprites():
                sprite.moveRight()

        # update selected shape
        self.selected_shape = None if len(self.collection_shapes) == 0 else self.collection_shapes.sprites()[self.selected_index]
        
        # determine button states given the selected shape
        self.heart_button.selected = False if self.selected_shape == None else self.selected_shape.shape_data.id == self.user.favorite_id
        if self.mode == COLLECTION: 
            if self.selected_shape == None or self.selected_shape.shape_data.id == self.user.favorite_id:
                self.del_button.disable()
            else:
                self.del_button.enable()

        self.woosh_sound.play()

    # ---- WINDOW MANAGEMENT HELPERS ----

    def toggle(self):
        '''toggle the collection window opened or closed'''

        self.opened = not self.opened

        if self.opened: 
            self.fully_closed = False

            self.next_y = self.opened_y
        else: 
            self.fully_opened = False
            self.next_y = self.closed_y

    def close(self):
        '''set attributes to close the collection window'''

        self.opened = False
        self.next_y = 1080

    def isButtonHovered(self, mouse_pos):
        '''check if the toggle button is hovered'''

        rel_mouse_pos = [mouse_pos[0], mouse_pos[1] - self.y + 50]

        return self.button.rect.collidepoint(rel_mouse_pos)
    
    def changeModeNetwork(self, connection_manager: ConnectionManager):
        '''prepare the collection window for a network match'''

        # set attributes
        self.mode = NETWORK
        self.connection_manager = connection_manager

        # update screen element states
        self.del_button.fastOff()
        self.add_button.disable()
        self.up_button.fastOff()
        self.heart_button.fastOff()
        self.nameplate.turnOn()

        # prevent some buttons from being rendered
        for button in [self.del_button, self.heart_button, self.add_button]:
            button.alpha = 0
            button.disabled = True
            button.on = False

            button.surface.set_alpha(button.alpha)

        # clear sprite group and reinitialize collection group
        self.collection_shapes.empty()
        self.initCollectionGroup()

        self.toggle()

    def changeModeCollection(self):
        '''prepare the collection window for the main menu'''

        # set attributes
        self.mode = COLLECTION
        self.connection_manager = None
        
        self.moveSpritesHome()

        # reset nameplate buttons for next time
        for button in self.nameplate.buttons:
            button.selected = False
            button.update()
        self.nameplate.renderSurface()  

        self.nameplate.turnOff()
        self.del_button.turnOn()
        self.heart_button.turnOn()
        self.add_button.enable()
        self.up_button.turnOn()

    def changeModeTransition(self):
        '''prepare the collection window for a transition'''
        self.mode = TRANSITION

    # ---- RENDERING HELPERS ----

    def renderSurface(self):
        '''render the entire collection window surface'''

        # clear surface
        # self.surface.fill((0, 0, 0, 0))
        
        # draw proper background depending on selected shape
        self.surface.blit(self.background if self.selected_shape == None or self.selected_shape.shape_data.id != self.user.favorite_id else self.background_hearts, [0, 50])

        # draw nameplate depending on mode
        if self.mode == NETWORK or self.mode == TRANSITION: self.nameplate.draw(self.surface)

        # sprites
        self.collection_shapes.draw(self.surface)
        self.deleted_shapes.draw(self.surface)

        # render essence bar and selector
        self.surface.blit(self.essence_bar.images[self.essence_bar.current_index], self.essence_bar.rect)
        self.selector.draw(self.surface)
        
        # draw additional shape info
        if self.info_alpha >= 0: 

            # update alpha values of info surfaces
            if self.paper.get_alpha() != self.info_alpha:
                self.paper.set_alpha(self.info_alpha)
                self.tape_surface.set_alpha(self.info_alpha)
                
                if self.selected_shape != None: self.selected_shape.info_surface.set_alpha(self.info_alpha)

            # draw info surfaces
            self.surface.blit(self.paper, self.paper_rect)
            self.surface.blit(self.tape_surface, self.tape_rect)
        
        # if we have a selected shape, show its information
        if self.selected_shape != None: 
            self.surface.blit(self.selected_shape.info_surface, self.selected_shape.info_rect)
            self.surface.blit(self.selected_shape.stats_surface, self.selected_shape.stats_rect)

        # draw screen elements
        [screen_element.draw(self.surface) for screen_element in self.screen_elements]

    def draw(self, surface):
        '''draw the collection window on a surface'''

        surface.blit(self.surface, self.rect)

    def positionWindow(self):
        '''update the position of the collection window if it is not already at its target position'''

        if self.y == self.next_y: return
        
        # calculate the remaining distance to the target
        distance = abs(self.y - self.next_y)

        # apply acceleration while far from the target, decelerate when close
        if distance > 50:
            self.v += self.a
        else:
            self.v = max(1, distance * 0.2)

        # move the window towards the target position, snap in place if position is exceeded
        if self.y > self.next_y:
            self.y = max(self.y - self.v, self.next_y)

        elif self.y < self.next_y:
            self.y = min(self.y + self.v, self.next_y)

        # reset the velocity when the window reaches its target
        if self.y == self.next_y:
            self.v = 0

        # update position
        self.rect.topleft = [0, self.y - 50]

        # determine closed status
        if self.y == self.closed_y:
            self.fully_closed = True
            
        if self.y == self.opened_y:
            self.fully_opened = True

    # ---- WINDOW STATE HELPERS ----

    def idle(self, mouse_pos, events):
        ''' replaces update() when window is fully closed
            only accepts inputs to and draws toggle button
        '''

        # if no inputs, opponent collection
        if not mouse_pos: return

        self.button.update(events, mouse_pos)
        self.surface.blit(self.button.surface, self.button.rect)

        for event in events: 
            if event.type == MOUSEBUTTONDOWN and event.button == 1 and self.button.rect.collidepoint(mouse_pos) and not self.button.disabled:
                self.toggle()

    def update(self, mouse_pos, events):
        '''update position of the collection window'''
        rel_mouse_pos = [mouse_pos[0], mouse_pos[1] - self.y + 50]

        clearSurfaceBeneath(self.surface, self.button.rect)

        # if the window is fully closed, idle
        if self.fully_closed:
            self.idle(rel_mouse_pos, events)
            return
        
        # update essence bar, check if shape_token_text needs to be updated
        self.essence_bar.update()    
        if self.shape_token_text.text != str(int(self.essence_bar.shown_essence)):
            current_text = self.shape_token_text.text

            if int(current_text) > int(self.essence_bar.shown_essence):
                current_text = str(int(current_text) - 1)
            else:
                current_text = str(int(current_text) + 1)

            self.shape_token_text.updateText(current_text)
            self.essence_bar.pop_sound.play()

        # keep track of the the state of the essence bar per-frame
        # pass change to hold buttons
        if self.essence_bar.changing and not self.essence_bar_changing:
            self.essence_bar_changing = True
            self.up_button.disable_override = True
            self.del_button.disable_override = True

        elif not self.essence_bar.changing and self.essence_bar_changing:
            self.essence_bar_changing = False
            self.up_button.disable_override = False
            self.del_button.disable_override = False

            self.up_button.updateCost(getEssenceCost(self.selected_shape.shape_data.level), self.user.shape_essence)

        # toggle buttons when essence bar is changing
        if self.mode == COLLECTION:
            if self.essence_bar.changing:
                self.del_button.disable()
                self.add_button.disable()
                self.up_button.disable()
                      
            else:
                if self.user.num_shapes > 1 and not self.selected_shape.shape_data.id == self.user.favorite_id:
                    self.del_button.enable()
            
                if self.user.num_shapes < 30 and int(self.user.shape_essence) > 0:
                    self.add_button.enable()
        
                # if self.selected_shape != None:
                #     self.up_button.enable()
        
        self.handleInputs(rel_mouse_pos, events)

        # check if the selector has changed
        if self.selected_index != self.selector.selected_index:
            while (self.selected_index > self.selector.selected_index):
                
                self.selected_index -= 1
                for sprite in self.collection_shapes.sprites():
                    sprite.moveRight()
                    
            while (self.selected_index < self.selector.selected_index):
                
                self.selected_index += 1
                for sprite in self.collection_shapes.sprites():
                    sprite.moveLeft()
                
            self.selected_shape = None if len(self.collection_shapes) == 0 else self.collection_shapes.sprites()[self.selected_index]
            
            if self.selected_shape != None:
                self.up_button.updateCost(getEssenceCost(self.selected_shape.shape_data.level), self.user.shape_essence)

            # determine if the up button should be enabled or disabled
            cost = round(0.25 * (1.35 ** self.selected_shape.shape_data.level), 2)
            if self.user.shape_essence < cost:
                self.up_button.disable()
            else: self.up_button.enable()

            self.heart_button.selected = False if self.selected_shape == None else self.selected_shape.shape_data.id == self.user.favorite_id
            if self.mode == COLLECTION: self.del_button.disable() if self.selected_shape.shape_data.id == self.user.favorite_id else self.del_button.enable()

            self.woosh_sound.play()

        # update child elements
        self.collection_shapes.update()
        self.deleted_shapes.update()

        # update nameplate and selector with special care for opponent
        if not self.is_opponent: 
            self.nameplate.update(rel_mouse_pos, events)
            if not self.nameplate.locked.selected: self.selector.update(rel_mouse_pos, events)
            else: self.selector.update(None, None)
        else: 
            # all updates are handled by the server sending data for opponent selection
            self.selector.update(None, None)
            self.nameplate.update(None, None)
            
        self.positionWindow()
        self.renderSurface()

    def handleInputs(self, mouse_pos, events):
        # rel_mouse_pos = [mouse_pos[0] - self.rect.x, mouse_pos[1] - self.rect.y + self.y - 50]

        # update screen elements
        for screen_element in self.screen_elements:
            screen_element.update(events, mouse_pos)

        # check if the user is hovering over the question mark on collection window
        if not self.question_button.disabled:
            if self.question_button.rect.collidepoint(mouse_pos) and self.info_alpha < 254: 
                self.info_alpha += 15
                self.info_alpha = min(self.info_alpha, 255)

            elif self.question_button.rect.collidepoint(mouse_pos) and self.info_alpha == 255: pass

            elif self.info_alpha > 0: 
                self.info_alpha -= 15
                self.info_alpha = max(self.info_alpha, 0)

        # check for updates to opponent nameplate
        if self.is_opponent and self.mode == NETWORK: 
            selections = self.connection_manager.getPlayerSelections()
            
            # if opponent's selection has changed, update selector (which will cause collection update)
            new_idx = selections.users_selected[0 if self.connection_manager.pid == 1 else 1]
            if self.selected_index != new_idx and new_idx != -1: self.selector.setSelected(new_idx)

            # if opponent ready status changed
            if selections.players_ready[0 if self.connection_manager.pid == 1 else 1] != self.nameplate.ready.selected:
                self.nameplate.ready.selected = not self.nameplate.ready.selected
                self.nameplate.ready.update()
                self.nameplate.renderSurface()

            # if opponent confirmed selection status changed
            if selections.locked[0 if self.connection_manager.pid == 1 else 1] != self.nameplate.locked.selected:
                self.nameplate.locked.selected = not self.nameplate.locked.selected
                self.nameplate.locked.update()
                self.nameplate.renderSurface()

            # if opponent keeps status changed
            if selections.keeps[0 if self.connection_manager.pid == 1 else 1] != self.nameplate.keeps.selected:
                self.nameplate.keeps.selected = not self.nameplate.keeps.selected
                self.nameplate.keeps.update()
                self.nameplate.renderSurface()

            return

        # handle events as normal if you aren't the opponent window
        for event in events:
            if event.type != MOUSEBUTTONDOWN: return

            if self.mode == COLLECTION:
                if self.button.rect.collidepoint(mouse_pos) and not self.button.disabled:
                    self.toggle()

                # if the window is closed the only inputs we want to accept are the open button
                if not self.opened: return

                elif self.add_button.isHovAndEnabled(mouse_pos):
                    self.userGenerateShape()
                    self.woosh_sound.play()

                elif self.heart_button.rect.collidepoint(mouse_pos):
                    self.markSelectedFavorite()


            if self.mode == NETWORK:
                rel_mouse_pos = [mouse_pos[0] - self.nameplate.rect.x, mouse_pos[1] - self.nameplate.rect.y]

                if self.nameplate.locked.rect.collidepoint(rel_mouse_pos):
                    self.connection_manager.send(f'LOCKED_{0 if self.nameplate.locked.selected else 1}.')

                    if self.nameplate.ready.selected:
                        self.nameplate.ready.selected = False
                        self.nameplate.ready.update()
                        self.connection_manager.readyUp(0 if self.nameplate.ready.selected else 1)

                elif self.nameplate.keeps.rect.collidepoint(rel_mouse_pos):
                    self.connection_manager.send(f'KEEPS_{0 if self.nameplate.keeps.selected else 1}.')

                    if self.nameplate.ready.selected:
                        self.nameplate.ready.selected = False
                        self.nameplate.ready.update()
                        self.connection_manager.readyUp(0 if self.nameplate.ready.selected else 1)

                elif self.nameplate.ready.rect.collidepoint(rel_mouse_pos) and self.nameplate.locked.selected:
                    self.connection_manager.readyUp(0 if self.nameplate.ready.selected else 1)

        # send players selected index, if changed
        if self.mode == NETWORK:
            selections = self.connection_manager.getPlayerSelections()

            # if user's selector selected_index has changed, send shape selection
            if self.selected_index != self.selector.selected_index:
                self.connection_manager.send(f'SELECTED_{self.selector.selected_index}.SHAPE_{self.selected_shape.shape_data.id}.')

            # if the current selection doesn't match the selections object, send selection again
            if (self.selected_index == self.selector.selected_index) and selections.users_selected[self.connection_manager.pid] != self.selected_index and self.selected_shape != None:
                self.connection_manager.send(f'SELECTED_{self.selector.selected_index}.SHAPE_{self.selected_shape.shape_data.id}.')

            # if toggle button state doesn't match selections, send again
            if selections.locked[self.connection_manager.pid] != self.nameplate.locked.selected:
                self.connection_manager.send(f'LOCKED_{1 if self.nameplate.locked.selected else 0}.')
            if selections.keeps[self.connection_manager.pid] != self.nameplate.keeps.selected:
                self.connection_manager.send(f'KEEPS_{1 if self.nameplate.keeps.selected else 0}.')
            if selections.players_ready[self.connection_manager.pid] != self.nameplate.ready.selected:
                self.connection_manager.send(f'READY_{1 if self.nameplate.ready.selected else 0}.')
