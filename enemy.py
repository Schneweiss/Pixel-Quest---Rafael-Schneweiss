import pygame
from tiles import AnimatedTile
from random import randint
from particles import ParticleEffect
from math import sin
from support import import_folder

class Enemy(AnimatedTile):
    def __init__(self, size, x, y, path, val, surface):
        super().__init__(size, x, y, path)
        #particles
        self.enemy_particle = pygame.sprite.GroupSingle()
        self.display_surface = surface
        self.particle_time = 0

        #generic
        self.impact = 0
        self.invincible = False
        self.enemy_idle = False
        self.attack = False
        self.status = 'run'
        self.wait = 0
        self.generic_delay = 0
        self.facing_right = False
        self.attack_delay = 0
        self.hurt = False
        self.rush = False


        #audio
        self.pig_rush = pygame.mixer.Sound('audio/effects/pig_rush.wav')
        self.pig_alert = pygame.mixer.Sound('audio/effects/pig_atention.wav')
        self.roar_sound = pygame.mixer.Sound('audio/effects/monster-3.wav')
        self.crunch_sound = pygame.mixer.Sound('audio/effects/crunch.mp3')
        self.monster_sound = pygame.mixer.Sound('audio/effects/monster-5.wav')
        self.monster_sound_2 = pygame.mixer.Sound('audio/effects/monster-15.wav')
        self.monster_sound_3 = pygame.mixer.Sound('audio/effects/monster-4.wav')
        self.break_sound = pygame.mixer.Sound('audio/effects/Explosion_04.mp3')
        self.fire1_sound = pygame.mixer.Sound('audio/effects/fire1.wav')

        #Enemy types
        self.enemy_type = val
        #slime
        if self.enemy_type == '0':
            self.rect.y += size - self.image.get_size()[1]
            self.speed = randint(1, 3)
            self.anim_ratio = 7
            self.rect.width = self.rect.width + 25
            self.delay = 50
            self.life = 10
            self.collision_rect = pygame.Rect((self.rect.left, self.rect.top), (self.rect.width, self.rect.height))

        #tooth
        if self.enemy_type == '1':
            self.rect.y += size - self.image.get_size()[1] + 4
            self.speed = randint(3, 4)
            self.anim_ratio = 20
            self.rect.width = self.rect.width
            self.delay = 20
            self.life = 30
            self.import_enemy_assets()
            self.image = self.animations['run'][self.frame_index]
            self.collision_rect = pygame.Rect((self.rect.left, self.rect.top), (self.rect.width, self.rect.height))

        #pig
        if self.enemy_type == '2':
            self.rect.y += size - self.image.get_size()[1] + 2
            self.speed = 2
            self.anim_ratio = 7
            self.rect.width = self.rect.width
            self.delay = 40
            self.life = 80
            self.import_enemy_assets()
            self.image = self.animations['run'][self.frame_index]
            self.rush = False
            self.collision_rect = pygame.Rect((self.rect.left, self.rect.top), (self.rect.width, self.rect.height))

        #bird
        if self.enemy_type == '3':
            self.rect.y += size - self.image.get_size()[1]
            self.speed = 3
            self.anim_ratio = 3
            self.rect.width = self.rect.width + 25
            self.delay = 50
            self.life = 10
            self.collision_rect = pygame.Rect((self.rect.left, self.rect.top), (self.rect.width, self.rect.height))

        #boss_0
        if self.enemy_type == '4':
            self.rect.y += size - self.image.get_size()[0] + 38
            self.speed = 4
            self.anim_ratio = 20
            self.rect.width = 150
            self.rect.height = 150
            self.delay = 0
            self.life = 200
            self.import_enemy_assets()
            self.image = self.animations['walk'][self.frame_index]
            self.rush = False
            self.collision_rect = pygame.Rect((self.rect.left + 100, self.rect.top + 100), (100, 100))
            self.create_gargoyle = False
            self.speak = True

        #gargoyle
        if self.enemy_type == '5':
            self.rect.y += size - self.image.get_size()[1]
            self.speed = 3
            self.anim_ratio = 10
            self.rect.width = self.rect.width + 25
            self.delay = 10
            self.life = 20
            self.collision_rect = pygame.Rect((self.rect.left, self.rect.top), (self.rect.width, self.rect.height))

    def import_enemy_assets(self):
        if self.enemy_type == '1':
            enemy_path = 'graphics/enemy/tooth/'
            self.animations = {'idle': [], 'run': [], 'anticipation': [], 'attack': [], 'underwater': [], 'effect': []}
        if self.enemy_type == '2':
            enemy_path = 'graphics/enemy/pig/'
            self.animations = {'idle': [], 'run': [], 'rush': []}
        if self.enemy_type == '4':
            enemy_path = 'graphics/enemy/boss_0/'
            self.animations = {'idle': [], 'run': [], 'walk': [], 'attack': [], 'attack2': [], 'attack3': [], 'hurt': [], 'run_roar': []}


        for animation in self.animations.keys():
            full_patch = enemy_path + animation
            self.animations[animation] = import_folder(full_patch)

    def move(self):
        self.generic_delay += 1
        self.attack_delay += 1
        if self.impact != 0:
            if self.speed < 0 and self.impact > 0: self.speed *= -1
            if self.speed > 0 and self.impact < 0: self.speed *= -1

            if self.status != 'underwater' or self.status != 'hurt':
                self.rect.x += self.speed/abs(self.speed) * int(abs(self.impact)/2)
            self.impact -= self.impact/abs(self.impact)
        else:
            if self.status == 'idle' or self.status == 'anticipation' or self.status == 'underwater' or self.status == 'attack' or self.status == 'attack2' or self.status == 'attack3' or self.status == 'hurt':
                if self.status != 'hurt':
                    self.invincible = False
                else:
                    if self.generic_delay > 30:
                        self.hurt = False
                        self.rush = True
                        self.speed *= 2
                        self.generic_delay += 200
            else:
                self.invincible = False
                if self.generic_delay > self.delay:
                    self.rect.x += self.speed

    def enemy_status(self):
        #pig
        if self.enemy_type == '2':
            if self.rush == False:
                if self.enemy_idle:
                    self.status = 'idle'
                else:
                    if self.status == 'idle':
                        self.create_enemy_particles((self.rect.centerx, self.rect.bottom), '2')
                        if self.generic_delay > 50: self.pig_alert.play()

                    if self.generic_delay > 20:
                        if self.life <= 40:
                            self.status = 'rush'
                            self.anim_ratio = 5
                            self.speed*=1.5
                            self.rush = True
                            self.pig_rush.play()
                        else:
                            self.status = 'run'

                    else:
                        self.status = 'idle'
        #tooth
        if self.enemy_type == '1':
            if self.status != 'underwater':
                if self.enemy_idle:
                    self.status = 'idle'
                else:
                    if self.status == 'idle' and self.generic_delay >= self.delay*2:
                        self.status = 'anticipation'
                        self.create_enemy_particles((self.rect.centerx, self.rect.bottom), '2')
                        self.frame_index = 0
                        self.roar_sound.play()
                        self.generic_delay = 0
                    else:
                        if self.attack and self.status != 'attack':
                            self.status ='attack'
                            self.create_enemy_particles((self.rect.centerx, self.rect.bottom), '3')
                            self.crunch_sound.play()
                            self.frame_index = 0
                        else:
                            if self.generic_delay >= self.delay and self.status != 'attack': self.status = 'run'
        #bird/gargoyle
        if self.enemy_type == '3' or self.enemy_type == '5':
            if self.enemy_idle:
                self.status = 'idle'
            else:
                self.status = 'run'
        #boss_0
        if self.enemy_type == '4':
            if self.hurt and self.status != 'hurt':
                self.frame_index = -1
                self.invincible = True
                self.status = 'hurt'
                self.generic_delay = 0
                self.monster_sound_3.play()
            elif self.hurt:
                pass
            else:
                if self.enemy_idle:
                    self.status = 'idle'
                    self.frames = self.animations[self.status]
                else:
                    if self.attack and self.status != 'attack' and self.status != 'attack2'  and self.status != 'attack3' and self.attack_delay > 60:
                        if self.rush: self.speed *= 0.5
                        self.rush = False
                        part = randint(1, 3)
                        if part == 1:
                            self.status = 'attack'
                            self.monster_sound.play()
                            self.frame_index = 0
                            self.attack_delay = 0
                        if part == 2:
                            self.status = 'attack2'
                            self.monster_sound_2.play()
                            self.frame_index = 0
                            self.attack_delay = 0
                        if part == 3:
                            self.status = 'attack3'
                            self.frame_index = 0
                            self.attack_delay = 0
                    else:
                        if self.rush:
                            self.status = 'run_roar'
                        else:
                            if self.generic_delay >= self.delay and self.status != 'attack' and self.status != 'attack2'and self.status != 'attack3' : self.status = 'run'

    def reverse_image(self):
        if self.enemy_type == '4' :
            if not self.facing_right:
                self.collision_rect = pygame.Rect((self.rect.left +50, self.rect.top + 50), (100, 100))
                if self.status == 'attack' and self.frame_index > 4 or self.status == 'attack2' and self.frame_index > 4:
                    self.collision_rect = pygame.Rect((self.rect.left -30, self.rect.top + 50), (180, 130))
            if self.facing_right:
                self.image = pygame.transform.flip(self.image, True, False)
                self.collision_rect = pygame.Rect((self.rect.left +70, self.rect.top + 50), (100, 100))
                if self.status == 'attack' and self.frame_index > 4 or self.status == 'attack2' and self.frame_index > 4:
                    self.collision_rect = pygame.Rect((self.rect.left +70, self.rect.top + 50), (180, 130))


        else:
            self.collision_rect = pygame.Rect((self.rect.left, self.rect.top), (self.rect.width, self.rect.height))
            #generic flip
            if self.speed > 0 and self.generic_delay > self.delay:
                self.image = pygame.transform.flip(self.image, True, False)

    def reverse(self):
        self.speed *= -1
        self.generic_delay = 0

    def enemy_animate(self):
        # loop over frame index
        if self.enemy_type == '4':
            if self.facing_right and self.speed < 0 and self.status == 'run':
                self.frame_index -= abs(self.speed) / self.anim_ratio
            elif not self.facing_right and self.speed > 0 and self.status == 'run':
                self.frame_index -= abs(self.speed) / self.anim_ratio
            else:
                self.frame_index += abs(self.speed) / self.anim_ratio

            if int(self.frame_index) < 0: self.frame_index = len(self.frames) - 1
        else:
            self.frame_index += abs(self.speed) / self.anim_ratio

        if int(self.frame_index) >= len(self.frames):
            if self.status == 'attack' : self.status = 'run'
            if self.status == 'attack2': self.status = 'run'
            if self.status == 'attack3':
                self.status = 'run'
                self.create_gargoyle = True
            self.frame_index = 0

        if self.enemy_type == "1" or self.enemy_type == "2" or self.enemy_type == "4":
            self.frames = self.animations[self.status]

        self.image = self.frames[int(self.frame_index)]


        if self.invincible:
            alpha = self.wave_value()
            self.image.set_alpha(alpha)
        else:
            self.image.set_alpha(255)

    def create_enemy_particles(self, pos, particle_type):
        if particle_type == '0':
            if self.speed < 0: pos += pygame.math.Vector2(30, - 8)
            if self.speed > 0: pos += pygame.math.Vector2(-30, - 8)
            enemy_particle_sprite = ParticleEffect(pos, 'slime')
            self.enemy_particle.add(enemy_particle_sprite)
        if particle_type == '1':
            if self.speed < 0: pos += pygame.math.Vector2(-20, -30)
            if self.speed > 0: pos += pygame.math.Vector2(20, -30)
            enemy_particle_sprite = ParticleEffect(pos, 'bubbles')
            self.enemy_particle.add(enemy_particle_sprite)
        if particle_type == '2':
            if self.speed < 0: pos += pygame.math.Vector2(10, - 75)
            if self.speed > 0: pos += pygame.math.Vector2(-10, - 75)
            enemy_particle_sprite = ParticleEffect(pos, 'exclamation')
            if self.speed > 0 : enemy_particle_sprite.flip()
            self.enemy_particle.add(enemy_particle_sprite)
        if particle_type == '3':
            if self.speed < 0: pos += pygame.math.Vector2(-30, - 35)
            if self.speed > 0: pos += pygame.math.Vector2(30, - 35)
            enemy_particle_sprite = ParticleEffect(pos, 'jaws')
            if self.speed > 0 : enemy_particle_sprite.flip()
            self.enemy_particle.add(enemy_particle_sprite)
        if particle_type == '4':
            if not self.facing_right: pos += pygame.math.Vector2(-80, - 26)
            if self.facing_right: pos += pygame.math.Vector2(140, - 26)
            enemy_particle_sprite = ParticleEffect(pos, 'earth_impact')
            if self.facing_right: enemy_particle_sprite.flip()
            self.enemy_particle.add(enemy_particle_sprite)
        if particle_type == '5':
            if not self.facing_right: pos += pygame.math.Vector2(-40, - 26)
            if self.facing_right: pos += pygame.math.Vector2(100, - 26)
            enemy_particle_sprite = ParticleEffect(pos, 'boss_punch')
            if self.facing_right: enemy_particle_sprite.flip()
            self.enemy_particle.add(enemy_particle_sprite)

    def run_particles(self):
        if self.enemy_type == '0':
            part= randint(1, 20)
            if part == 1 and self.particle_time >= 10:
                self.create_enemy_particles((self.rect.centerx, self.rect.bottom), '0')
                self.particle_time = 0
            self.particle_time += 0.1
        if self.status == 'underwater':
            part = randint(1, 20)
            if part == 1 and self.particle_time >= 5:
                self.create_enemy_particles((self.rect.centerx, self.rect.bottom), '1')
                self.particle_time = 0
            self.particle_time += 0.1
        if self.enemy_type == '4' and self.status == 'attack2' and int(self.frame_index) == 4:
            self.create_enemy_particles((self.rect.centerx, self.rect.bottom), '4')
            if self.frame_index <= 4 + abs(self.speed) / self.anim_ratio: self.break_sound.play()
        if self.enemy_type == '4' and self.status == 'attack' and int(self.frame_index) == 4:
            self.create_enemy_particles((self.rect.centerx, self.rect.bottom), '5')
        if self.enemy_type == '4' and self.status == 'attack3' and int(self.frame_index) == 1:
            if self.frame_index < 1 + abs(self.speed) / self.anim_ratio: self.fire1_sound.play()



    def wave_value(self):
        value = sin(pygame.time.get_ticks())
        if value >= 0: return 255
        else: return 0

    def update(self, shift,shifty):
        self.rect.x += shift
        self.rect.y += shifty
        self.enemy_status()
        self.enemy_animate()
        self.move()
        self.reverse_image()
        self.run_particles()
        self.enemy_particle.update(shift, shifty)
        self.enemy_particle.draw(self.display_surface)



