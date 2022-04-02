import pygame, sys
from support import import_folder
from settings import screen_width, screen_height
from random import randint

class Tile(pygame.sprite.Sprite):
    def __init__(self, size, x, y):
        super().__init__()
        self.image = pygame.Surface((size, size))
        self.rect = self.image.get_rect(topleft = (x, y))

    def update(self, shift, shifty):
        self.rect.x += shift
        self.rect.y += shifty

class StaticTile(Tile):
    def __init__(self, size, x, y, surface):
        super().__init__(size, x, y)
        self.image = surface

class Crate(StaticTile):
    def __init__(self, size, x, y):
        super().__init__(size, x, y, pygame.image.load('graphics/terrain/crate.png').convert_alpha())
        offset_y = y + size #+ 2
        self.rect = self.image.get_rect(bottomleft=(x, offset_y))
        offset_width = 0#10
        offset_x = offset_width / 2
        self.rect = pygame.Rect((self.rect.left + offset_x , self.rect.top ), (self.rect.width - offset_width, self.rect.height))

class AnimatedTile(Tile):
    def __init__(self, size, x, y, path):
        super().__init__(size, x, y)
        self.frames = import_folder(path)
        self.frame_index = 0
        self.image = self.frames[self.frame_index]

    def animate(self):
        # loop over frame index
        self.frame_index += 0.15
        if self.frame_index >= len(self.frames):
            self.frame_index = 0
        self.image = self.frames[int(self.frame_index)]

    def update(self, shift, shifty):
        self.animate()
        self.rect.x += shift
        self.rect.y += shifty

class Coin(AnimatedTile):
    def __init__(self, size, x, y, path, value):
        super().__init__(size, x, y, path)
        center_x = x + int(size/2)
        center_y = y + int(size/2)
        self.rect = self.image.get_rect(center = (center_x, center_y))
        self.value = value

class Palm(AnimatedTile):
    def __init__(self, size, x, y, path, offset):
        super().__init__(size, x, y, path)
        offset_y = y - offset
        self.rect.topleft = (x, offset_y )
        self.rect.height = self.rect.height - 20

class Door(Tile):
    def __init__(self, size, x, y, path, offset, val):
        super().__init__(size, x, y)
        offset_y = y - offset
        self.rect.topleft = (x, offset_y )
        self.frames = import_folder(path)
        self.frame_index = 0
        self.image = self.frames[self.frame_index]
        self.rect.width +=25
        self.rect.height+=35
        self.open = False
        self.door_type = val

    def animate(self):
        # loop over frame index
        if self.frame_index <= len(self.frames) -1:
            self.frame_index += 0.1
        self.image = self.frames[int(self.frame_index)]

    def update(self, shift, shifty):
        self.rect.x += shift
        self.rect.y += shifty
        if self.open: self.animate()

class Npc(Tile):
    def __init__(self, size, x, y, path, offset, val):
        super().__init__(size, x, y)
        offset_y = y - offset
        self.rect.topleft = (x, offset_y )
        self.frames = import_folder(path)
        self.frame_index = 0
        self.image = self.frames[self.frame_index]
        self.npc_type = val


    def animate(self):
        # loop over frame index
        self.frame_index += 0.15
        if self.frame_index >= len(self.frames):
            self.frame_index = 0
        self.image = self.frames[int(self.frame_index)]

    def update(self, shift, shifty):
        self.rect.x += shift
        self.rect.y += shifty
        self.animate()

class Heart(AnimatedTile):
    def __init__(self, x, y, path, type):
        super().__init__(30, x, y, path)
        center_x = x
        center_y = y - 50
        self.rect = self.image.get_rect(center = (center_x, center_y))
        self.rect.width = 30
        if type == 0: self.value = 10
        if type == 1: self.value = 50

class Rain(StaticTile):
    def __init__(self, size, x, y):
        super().__init__(size, x, y, pygame.image.load('graphics/decoration/rain/rain.png').convert_alpha())
        self.speed = randint(1, 20)
        self.scale = randint(4,10)
        self.angle = randint(0,10)
        self.image = pygame.transform.rotozoom(self.image,self.angle, self.scale/10)

    def update(self, shift, shifty):
        self.rect.x += shift
        self.rect.y += shifty
        self.rect.y += 10 + self.speed
        self.rect.x -= 10 + self.speed - self.angle/2
        if self.rect.y > screen_height:
            self.rect.y = -50
            self.rect.x = randint(0, int(screen_width*1.5))



