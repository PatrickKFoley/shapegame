from pygame.locals import *
from pygame.sprite import Group
from pygame.transform import smoothscale
from pygame.surface import Surface
import pygame

from createdb import Shape as ShapeData

from .collectionshape import CollectionShape

MIN_W = 75
MAX_W = 1030

class Selection(pygame.sprite.Sprite):
    def __init__(self, shape: ShapeData, position: int, num_shapes: int, inverted: bool = False):
        super().__init__()
        
        self.shape_type = shape.type
        self.shape = shape
        self.position = position
        self.num_shapes = num_shapes
        self.inverted = inverted
        self.surface_size = 35
        self.min_size = 25
        self.max_size = 35
        
        self.selected = position == 0
        self.hovered = False
        self.size = self.max_size if self.selected else self.min_size
        self.next_size = self.size
        
        self.image = Surface((self.surface_size, self.surface_size), pygame.SRCALPHA, 32).convert_alpha()
        self.selected_surface = Surface((self.surface_size, self.surface_size), pygame.SRCALPHA, 32).convert_alpha()
        self.unselected_surface = Surface((self.surface_size, self.surface_size), pygame.SRCALPHA, 32).convert_alpha()
        self.rect = self.image.get_rect()
        
        width = min(max(self.num_shapes * 50, MIN_W), MAX_W)
        self.x = (position + 1)* (width / (num_shapes + 1))
        self.rect.center = [self.x, 30]
        
        if self.shape_type == 'triangle':
            pygame.draw.polygon(self.selected_surface, 'white' if self.inverted else 'black', [[self.surface_size/2, 0], [self.surface_size, self.surface_size], [0, self.surface_size]])
            pygame.draw.polygon(self.unselected_surface, 'lightgray' if self.inverted else 'gray', [[self.surface_size/2, 0], [self.surface_size, self.surface_size], [0, self.surface_size]])
        
        elif self.shape_type == 'square':
            # self.selected_surface.fill('black')
            # self.unselected_surface.fill('gray')
            pygame.draw.rect(self.selected_surface, 'white' if self.inverted else 'black', [0, 0, self.surface_size, self.surface_size], border_radius=10)
            pygame.draw.rect(self.unselected_surface, 'lightgray' if self.inverted else 'gray', [0, 0, self.surface_size, self.surface_size], border_radius=10)
        
        elif self.shape_type == 'circle':
            pygame.draw.circle(self.selected_surface, 'white' if self.inverted else 'black', [self.surface_size/2, self.surface_size/2], self.surface_size/2)
            pygame.draw.circle(self.unselected_surface, 'lightgray' if self.inverted else 'gray', [self.surface_size/2, self.surface_size/2], self.surface_size/2)

        shape_image = smoothscale(self.selected_surface if self.selected or self.hovered else self.unselected_surface, [self.size, self.size])
        rect = shape_image.get_rect()
        rect.center = self.surface_size/2, self.surface_size/2
        self.image.blit(shape_image, rect)

    def update(self):
        
        # check if a shape was added
        width = min(max(self.num_shapes * 50, MIN_W), MAX_W)
        if self.x != (self.position + 1)* (width / (self.num_shapes + 1)): 
            self.x = (self.position + 1)* (width / (self.num_shapes + 1))
            
            self.rect.center = self.x, 30
        
        # shrink to unselected size if not hovered or selected
        if not self.hovered and not self.selected and self.next_size != 25:
            self.next_size = self.min_size
        
        # change size to match status
        if self.size != self.next_size:
            # # print(self.position, self.size, self.next_size)
            # # print('changing size')
            
            # grow
            if self.size < self.next_size:
                self.size = min(self.size + 1, self.next_size)
            # shrink
            else:
                self.size = max(self.size - 1, self.next_size)
                
            # reset surface
            self.image = Surface((self.surface_size, self.surface_size), pygame.SRCALPHA, 32).convert_alpha()
            shape_image = smoothscale(self.selected_surface if self.selected or self.hovered else self.unselected_surface, [self.size, self.size])
            rect = shape_image.get_rect()
            rect.center = self.surface_size/2, self.surface_size/2
            self.image.blit(shape_image, rect)
        
class Selector:
    def __init__(self, shapes: list[CollectionShape], center: list[int], inverted: bool = False):
        self.shapes = shapes
        self.num_shapes = len(shapes)
        self.center = center
        self.topleft = [850, 377]
        self.selected_index = 0
        self.inverted = inverted

        self.disabled = False
        
        self.w = min(max(self.num_shapes * 50, MIN_W), MAX_W)
        self.h = 60
        self.next_w = self.w
        
        self.surface = Surface((self.w, 60), pygame.SRCALPHA, 32).convert_alpha()
        self.rect = self.surface.get_rect()
        # self.rect.center = center
        self.rect.topleft = self.topleft
        pygame.draw.rect(self.surface, 'white' if self.inverted else 'black', [0, 0, self.w, self.h], border_radius=10)
        pygame.draw.rect(self.surface, 'black' if self.inverted else 'white', [3, 3, self.w-6, self.h-6], border_radius=10)
        self.selections = Group()
        
        for count, shape in enumerate(self.shapes):
            self.selections.add(Selection(shape.shape_data, count, self.num_shapes, self.inverted))
        
    def addShape(self, shape: ShapeData):
        if len(self.selections) != 0: 
            # self.selections.sprites()[self.selected_index].selected = False

            for selection in self.selections.sprites(): selection.selected = False
            
        self.selected_index = 0
        self.num_shapes += 1
        
        for sprite in self.selections.sprites():
            sprite.position += 1
            sprite.num_shapes += 1
        
        selections_copy = self.selections.sprites()
        
        self.selections.empty()
        self.selections.add(Selection(shape, 0, self.num_shapes, self.inverted))
        self.selections.add(selections_copy)
        
        self.redrawSurface()
        
    def removeShape(self):
        
        removed_shape = self.selections.sprites()[self.selected_index]
        for sprite in self.selections.sprites():
            sprite: Selection

            sprite.num_shapes -= 1
            if sprite.position > removed_shape.position:
                sprite.position -= 1
        self.selections.remove(removed_shape)
        self.num_shapes -= 1
        
        if removed_shape.position == self.num_shapes: 
            self.selected_index -= 1
        
        if self.selected_index >= 0:
            new_selected = self.selections.sprites()[self.selected_index]
            new_selected.selected = True
            new_selected.next_size = new_selected.max_size
        
        self.redrawSurface()
        
    def redrawSurface(self):
        self.next_w = min(max(self.num_shapes * 50, MIN_W), MAX_W)
        self.surface = Surface((self.w, 60), pygame.SRCALPHA, 32).convert_alpha()
        # self.surface.fill((255, 255, 255))
        self.rect = self.surface.get_rect()
        # self.rect.center = self.center
        self.rect.topleft = self.topleft
        pygame.draw.rect(self.surface, 'white' if self.inverted else 'black', [0, 0, self.w, self.h], border_radius=10)
        pygame.draw.rect(self.surface, 'black' if self.inverted else 'white', [3, 3, self.w-6, self.h-6], border_radius=10)

    def setSelected(self, selected_index):
        print(self.selected_index)
        self.selected_index = selected_index

        for idx, sprite in enumerate(self.selections.sprites()):
            if idx != self.selected_index:
                sprite.selected = False
                sprite.hovered = False
            
            else:
                sprite.selected = True
                sprite.next_size = sprite.max_size

        print(self.selected_index)

    def update(self, mouse_pos, events):

        # if no inputs are provided, this is the opponent's selector
        if mouse_pos != None and not self.disabled:
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
                            self.selected_index = sprite.position
                            
                            sprite.selected = True
                            sprite.next_size = sprite.max_size
                            
                            for sprite2 in self.selections.sprites():
                                if sprite.position != sprite2.position: 
                                    sprite2.selected = False
                                    sprite2.hovered = False
                            
        if self.w != self.next_w:
            if self.w < self.next_w:
                self.w = min(self.w + 5, self.next_w)
            else:
                self.w = max(self.w - 5, self.next_w)
            
            self.surface = Surface((self.w, 60), pygame.SRCALPHA, 32).convert_alpha()
            self.rect = self.surface.get_rect()
            self.rect.topleft = self.topleft
        
        pygame.draw.rect(self.surface, 'white' if self.inverted else 'black', [0, 0, self.w, self.h], border_radius=10)
        pygame.draw.rect(self.surface, 'black' if self.inverted else 'white', [3, 3, self.w-6, self.h-6], border_radius=10)
        self.selections.draw(self.surface)
        self.selections.update()
  
    def disable(self):
        self.disabled = True

    def enable(self):
        self.disabled = False

    def draw(self, surface):
        surface.blit(self.surface, self.rect)

