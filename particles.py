import pygame
from support import import_folder

class ParticleEffect(pygame.sprite.Sprite):
    def __init__(self, pos, type):
        super().__init__()
        self.frame_index = 0
        self.animation_speed = 0.5
        self.image_flip = False
        self.type = type

        if type == 'jump':
            self.frames = import_folder('graphics/character/dust_particles/jump')
        if type == 'land':
            self.frames = import_folder('graphics/character/dust_particles/land')
        if type == 'explosion':
            self.frames = import_folder('graphics/enemy/explosion')
        if type == 'slime':
            self.frames = import_folder('graphics/enemy/particles/slime')
            self.animation_speed = 0.1
        if type == 'exclamation':
            self.frames = import_folder('graphics/enemy/particles/exclamation')
            self.animation_speed = 0.2
        if type == 'bubbles':
            self.frames = import_folder('graphics/enemy/particles/bubbles')
            self.animation_speed = 0.2
        if type == 'jaws':
            self.frames = import_folder('graphics/enemy/tooth/effect')
            self.animation_speed = 0.1
        if type == 'splash':
            self.frames = import_folder('graphics/character/dust_particles/water_splash')
            self.animation_speed = 0.2
        if type == 'heart_fx':
            self.frames = import_folder('graphics/character/dust_particles/heart_fx')
            self.animation_speed = 0.1
        if type == 'earth_impact':
            self.frames = import_folder('graphics/character/dust_particles/earth')
            self.animation_speed = 0.2
        if type == 'boss_punch':
            self.frames = import_folder('graphics/character/dust_particles/boss_punch')
            self.animation_speed = 0.3
        if type == 'button_up':
            self.frames = import_folder('graphics/ui/button_up')
            self.animation_speed = 0.5

        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect(center = pos)

    def animate(self):

        if self.type == 'bubbles':  self.rect.y -= 1

        self.frame_index += self.animation_speed
        if self.frame_index >= len(self.frames):
            self.kill()
        else:
            self.image = self.frames[int(self.frame_index)]
            if self.image_flip == True: self.image = pygame.transform.flip(self.image,True, False)

    def flip(self):
        self.image_flip = True

    def update(self, x_shift,shifty):
        self.animate()
        self.rect.x += x_shift
        self.rect.y += shifty
