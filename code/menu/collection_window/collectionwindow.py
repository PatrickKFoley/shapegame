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

from .collectionshape import CollectionShape
from .selector import Selector
from .essencebar import EssenceBar

class CollectionWindow:
    def __init__(self, user: User, session: Session):
        self.user = user
        self.session = session

        self.initCollectionWindow()
        self.initCollectionGroup()
        
        self.selector = Selector(self.collection_shapes, [1200, 400])

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

        self.button = Button('shapes', 50, [25, 25])
        self.button.draw(self.surface)
        self.question_button = Button('question', 40, [780, 131])
        self.question_button.disable()
        self.add_button = Button('add', 90, [81, 226])
        self.del_button = Button('trash', 40, [205, 131])
        self.heart_button = Button('heart', 40, [780, 400])

        # disable add button if user has no shape tokens
        if self.user.shape_tokens == 0: self.add_button.disable()

        self.clickables = [
            self.button, self.question_button, 
            self.add_button,    self.del_button, 
            self.yes_clickable, self.no_clickable,
            self.heart_button
        ]

        self.background = load('assets/backgrounds/collection_window.png').convert_alpha()
        self.background_hearts = load('assets/backgrounds/collection_window_hearts.png').convert_alpha()
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
        self.fully_closed = True
        self.info_alpha = 0

        self.selected_index = 0
        self.selected_shape: ShapeData | None = None
        self.collection_shapes = Group()
        self.deleted_shapes = Group()

        self.delete_clicked = False
        
        self.woosh_sound = Sound('assets/sounds/woosh.wav')

    def initCollectionGroup(self):
        '''create Collection shapes for newly logged in user'''

        # create sprites
        for count, shape_data in enumerate(self.user.shapes):
            new_shape = CollectionShape(shape_data, count, self.user.num_shapes, self.session)
            self.collection_shapes.add(new_shape)

        # sort favorite shape to the front of the list
        for sprite in self.collection_shapes.sprites(): 
            sprite: CollectionShape
            if sprite.shape_data.id == self.user.favorite_id:

                # sort list
                self.collection_shapes.remove(sprite)
                collection_copy = self.collection_shapes.sprites()
                self.collection_shapes.empty()
                self.collection_shapes.add(sprite)
                self.collection_shapes.add(collection_copy)

                # reposition sprites
                [sprite.reposition(position, self.user.num_shapes) for position, sprite in enumerate(self.collection_shapes.sprites())]
                
                # disable delete button
                self.selected_shape = sprite
                self.del_button.disable()
                break

        # if user has 1 or 0 shapes, disable delete button
        if self.user.num_shapes <= 1:
            self.del_button.disable()

        if self.user.num_shapes >= 1: 
            self.question_button.enable()

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

            # determine closed status
            if self.y == 1080:
                self.fully_closed = True

    def userGenerateShape(self):
        '''handle the user adding a shape to their collection'''
        if self.user.shape_tokens == 0 or self.user.num_shapes == 30: return

        # move all shapes to original position
        while self.selected_index != 0:
            self.selected_index -= 1

            for shape in self.collection_shapes:
                shape.moveRight()

        # create shape in database
        shape_data = generateRandomShape(self.user, self.session)

        # add new collection shape to the front of the list
        new_shape = CollectionShape(shape_data, -1, self.user.num_shapes, self.session, True)
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
        if self.user.num_shapes >= 1: self.question_button.enable()
        
        # add shape to selector
        self.selector.addShape(shape_data)
        
        # toggle heart button
        self.heart_button.selected = self.selected_shape.shape_data.id == self.user.favorite_id
        self.del_button.disable() if self.selected_shape.shape_data.id == self.user.favorite_id else self.del_button.enable()

        # reposition shapes
        [sprite.redrawPosition(position, self.user.num_shapes) for position, sprite in enumerate(self.collection_shapes.sprites())]

    def deleteSelectedShape(self):
        # don't let user delete their only shape
        if self.user.num_shapes == 1: return

        # remove shape from sprites first
        removed = False
        for count, sprite in enumerate(self.collection_shapes.sprites()):
            sprite: CollectionShape
            
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
                    for sprite in self.collection_shapes.sprites():
                        sprite.moveRight()

                    self.selected_index -= 1
                
                self.selected_shape = self.collection_shapes.sprites()[self.selected_index]

                # if user deleted their favorite shape, mark next new selected shape as favorite 
                if sprite.shape_data.id == self.user.favorite_id:
                    self.markSelectedFavorite()
                self.heart_button.selected = self.selected_shape.shape_data.id == self.user.favorite_id
                self.del_button.disable() if self.selected_shape.shape_data.id == self.user.favorite_id else self.del_button.enable()
                
                
            
            elif removed: sprite.moveLeft()

        # close the delete window
        self.delete_clicked = False

        # if user now has one shape, disable delete button
        if self.user.num_shapes == 1: 
            self.del_button.disable()

        # reposition shapes
        [sprite.redrawPosition(position, self.user.num_shapes) for position, sprite in enumerate(self.collection_shapes.sprites())]

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

            if self.button.rect.collidepoint(mouse_pos):
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
        self.del_button.disable()
        
        self.del_button.disable() 
        self.session.query(User).filter(User.id == self.user.id).update({User.favorite_id: self.selected_shape.shape_data.id})

        self.session.commit()

    def idle(self, mouse_pos, events):
        ''' replaces update() when window is fully closed
            only accepts inputs to and draws toggle button
        '''

        self.button.update(mouse_pos)
        self.surface.blit(self.button.surface, self.button.rect)

        for event in events: 
            if event.type == MOUSEBUTTONDOWN and event.button == 1 and self.button.rect.collidepoint(mouse_pos):
                self.toggle()

    def update(self, mouse_pos, events):
        '''update position of the collection window'''
        rel_mouse_pos = [mouse_pos[0], mouse_pos[1] - self.y + 50]

        # if the window is fully closed, idle
        if self.fully_closed:
            self.idle(rel_mouse_pos, events)
            return
        
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
                    

            self.selected_shape = self.collection_shapes.sprites()[self.selected_index]
            
            self.heart_button.selected = self.selected_shape.shape_data.id == self.user.favorite_id
            self.del_button.disable() if self.selected_shape.shape_data.id == self.user.favorite_id else self.del_button.enable()

            self.woosh_sound.play()

        # update returns true when shape essence amount is altered, needing commit
        if self.essence_bar.update(): 
            self.session.commit()
            self.shape_token_text = Text(f'{self.user.shape_tokens}', 35 if self.user.shape_tokens < 10 else 30, 108, 200, color=('black' if self.user.shape_tokens > 0 else 'red'))

        if self.essence_bar.changing and not self.del_button.disabled:
            self.del_button.disable()
        elif not self.essence_bar.changing and self.del_button.disabled and self.user.num_shapes > 1 and not self.selected_shape.shape_data.id == self.user.favorite_id:
            self.del_button.enable()

        self.handleInputs(mouse_pos, events)

        self.collection_shapes.update()
        self.deleted_shapes.update()
        self.selector.update(rel_mouse_pos, events)
        
        self.positionWindow()

        self.renderSurface()

    def toggle(self):
        self.opened = not self.opened

        if self.opened: 
            self.fully_closed = False
            self.next_y = 1080 - self.background.get_size()[1]
        else: self.next_y = 1080

    def renderSurface(self):
        self.surface.blit(self.background_hearts if self.selected_shape.shape_data.id == self.user.favorite_id else self.background, [0, 50])

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

    def isButtonHovered(self, mouse_pos):
        rel_mouse_pos = [mouse_pos[0], mouse_pos[1] - self.y + 50]

        return self.button.rect.collidepoint(rel_mouse_pos)