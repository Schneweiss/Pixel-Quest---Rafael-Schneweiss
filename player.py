import pygame
from support import import_folder
from math import sin


class Player(pygame.sprite.Sprite):
    def __init__(self, pos, surface, create_jump_particles, change_health, change_stamina):
        super().__init__()
        self.import_character_assets()
        self.frame_index = 0
        self.animation_speed = 0.15
        self.image = self.animations['idle'][self.frame_index]
        self.rect = self.image.get_rect(topleft = pos)

        #player movement
        self.direction = pygame.math.Vector2(0, 0)
        self.jump_delay = 0
        self.init_speed = 3
        self.dash_speed = 0
        self.speed = 3
        self.gravity = 0.8
        self.jump_speed = -15
        self.player_flow = 16
        self.rect_offset_left = 20
        self.rect_offset_right = 18
        self.rect_offset_height = 10
        self.rect_attack_offset = 15
        self.rect_attack_offset_y = 5
        self.rect_attack_offset_height = 20
        self.collision_rect = pygame.Rect((self.rect.left, self.rect.top), (self.rect.width - self.rect_offset_right - self.rect_offset_left, self.rect.height - self.rect_offset_height))
        self.attack_rect = pygame.Rect((self.rect.left , self.rect.top ), (self.rect.width - self.rect_offset_right - self.rect_offset_left,
        self.rect.height - self.rect_offset_height - self.rect_attack_offset_height))

        #player status
        self.status = 'idle'
        self.facing_right = True
        self.on_ground = False
        self.on_ceiling = False
        self.on_left = False
        self.on_right = False
        self.player_mode = 'Null'
        self.attack = False
        self.attack2 = False
        self.attack3 = False
        self.combo_delay =0
        self.attack_frame = False
        self.throw = False
        self.world_shift = 0
        self.rock_angle = 0
        self.stamina = 100
        self.tired = False
        self.on_climb = False
        self.up_down = False
        self.dash_time = 10
        self.absolute_speed = 2
        self.second_jump = True
        self.touch_ground = True
        self.impact = 0

        #dust particles
        self.import_dust_run_particles()
        self.dust_frame_index = 0
        self.dust_animation_speed = 0.15
        self.display_surface = surface
        self.create_jump_particles = create_jump_particles
        # dust particles
        self.import_attack_particle()
        self.particle_frame_index_1 = len(self.attack_particles_1)
        self.particle_frame_index_2 = len(self.attack_particles_2)
        self.particle_frame_index_3 = len(self.attack_particles_3)
        self.particle_frame_index_rock1 = len(self.attack_particles_rock1)
        self.particle_frame_index_rock2 = len(self.attack_particles_rock2)
        self.v_x = 0
        self.v_y = 0
        self.rock_pos= (0, 0)
        self.rock_moving = False
        self.particle_animation_speed = 0.30
        self.rock_time_duration = 30


        #health
        self.change_health = change_health
        self.invincible = False
        self.invincibility_duration = 800
        self.hurt_time = 0

        #stamina
        self.change_stamina = change_stamina

        #audio
        self.jump_sound = pygame.mixer.Sound('audio/effects/jump.wav')
        self.jump_sound.set_volume(0.5)
        self.hit_sound = pygame.mixer.Sound('audio/effects/hit.wav')
        self.hit_sound.set_volume(1)
        self.attack1_sound = pygame.mixer.Sound('audio/effects/attack1.mp3')
        self.attack2_sound = pygame.mixer.Sound('audio/effects/attack2.mp3')
        self.attack3_sound = pygame.mixer.Sound('audio/effects/attack3.mp3')
        self.throw1_sound = pygame.mixer.Sound('audio/effects/throw1.mp3')
        self.throw2_sound = pygame.mixer.Sound('audio/effects/throw2.mp3')
        self.dash_sound = pygame.mixer.Sound('audio/effects/dash.mp3')

    def import_character_assets(self):
        character_path = 'graphics/character/'
        self.animations = {'idle':[],'run':[],'jump':[],'fall':[],'attack1':[],'attack2':[],'climb':[],'death':[],'push':[],'run2':[],'throw':[],'dash':[], 'in':[], 'jump2':[]}

        for animation in self.animations.keys():
            full_patch = character_path + animation
            self.animations[animation] = import_folder(full_patch)

    def import_dust_run_particles(self):
        self.dust_run_particles = import_folder('graphics/character/dust_particles/run')

    def import_attack_particle(self):
        self.attack_particles_1 = import_folder('graphics/character/dust_particles/attack')
        self.attack_particles_2 = import_folder('graphics/character/dust_particles/attack1')
        self.attack_particles_3 = import_folder('graphics/character/dust_particles/attack2')
        self.attack_particles_rock1 = import_folder('graphics/character/dust_particles/rock/Rock1')
        self.attack_particles_rock2 = import_folder('graphics/character/dust_particles/rock/Rock2')

    def animate(self):
        animation = self.animations[self.status]
        #loop over frame index
        if not self.on_climb: self.frame_index += self.animation_speed
        #throw rock frame
        if self.status == 'throw':
            if self.frame_index >= 6: self.rock_moving = True

        if self.frame_index >= len(animation):
            if self.player_mode != 'death' and self.status != 'in' :
                self.frame_index = 0
                if self.status == 'attack1' and self.attack == True:
                    self.attack = False
                if self.status == 'attack2' and self.attack == True:
                    self.attack = False
                    self.attack2 = False
                if self.status == 'throw':
                    self.throw = False
                if self.status == 'jump2':
                    self.attack3 = False
            else:
                self.frame_index = len(animation) - self.animation_speed
        # select frames from attack_status to attack enemy
        if self.attack and int(self.frame_index) == 1:
            self.attack_frame = True
        elif self.attack3:
            self.attack_frame = True
        else:
            self.attack_frame = False



        image = animation[int(self.frame_index)]

        #attack rect
        if self.status == 'attack2':
            self.rect_attack_offset = 50
        elif self.status == 'jump2':
            self.rect_attack_offset = -40
            self.attack_rect.width = 100
            self.attack_rect.height = 80
        else:
            self.rect_attack_offset = 30
            self.attack_rect.width = 30
            self.attack_rect.height = 40




        if self.facing_right:
            self.image = image
            self.rect.bottomleft = (self.collision_rect.left - self.rect_offset_left, self.collision_rect.bottom)
            self.attack_rect.bottomleft = (self.collision_rect.left + self.rect_attack_offset , self.collision_rect.bottom - self.rect_attack_offset_y)
        else:
            flipped_image = pygame.transform.flip(image, True, False)
            self.image = flipped_image
            self.rect.bottomright = (self.collision_rect.right + self.rect_offset_left, self.collision_rect.bottom)
            self.attack_rect.bottomright = (self.collision_rect.right - self.rect_attack_offset, self.collision_rect.bottom- self.rect_attack_offset_y)

        if self.invincible and self.player_mode != 'death':
            alpha = self.wave_value()
            self.image.set_alpha(alpha)
        else:
            self.image.set_alpha(255)

        self.rect = self.image.get_rect(midbottom = self.rect.midbottom)

    def run_dust_animation(self):
        if self.status == 'run2' or self.status == 'push' or self.status == 'dash' and self.on_ground:
            self.dust_frame_index += self.dust_animation_speed
            if self.dust_frame_index >= len(self.dust_run_particles):
                self.dust_frame_index = 0

            dust_particle = self.dust_run_particles[int(self.dust_frame_index)]

            if self.facing_right:
                pos = self.rect.bottomleft - pygame.math.Vector2(6, 10)
                self.display_surface.blit(dust_particle, pos)
            else:
                pos = self.rect.bottomright - pygame.math.Vector2(6, 10)
                flipped_dust_particle = pygame.transform.flip(dust_particle, True, False)
                self.display_surface.blit(flipped_dust_particle, pos)

    def run_attack_animation(self):
    #throw 1
        if self.rock_moving:
            attack_particles_rock1 = self.attack_particles_rock1[int(self.particle_frame_index_rock1)]
            if self.particle_frame_index_rock1 <= len(self.attack_particles_rock1)-1:
                self.particle_frame_index_rock1 += self.particle_animation_speed

                if self.facing_right:
                    self.rock_pos = self.rect.topright + pygame.math.Vector2(-45, 25)
                else:
                    self.rock_pos = self.rect.topleft + pygame.math.Vector2(45, 25)
                    if self.v_x > 0: self.v_x *= -1

                self.rock_rect = self.attack_particles_rock1[0].get_rect(center=self.rock_pos)


            if abs(self.v_y) > 1: self.rock_rect.centery += self.v_y
            if abs(self.v_x) > 1: self.rock_rect.centerx += self.v_x

            #animation
            attack_particles_rock1 = pygame.transform.rotozoom(attack_particles_rock1, -(self.rock_rect.x + self.world_shift)*5, 1)
            if self.rock_time_duration <= 3: attack_particles_rock1.set_alpha(self.wave_value())
            self.display_surface.blit(attack_particles_rock1, (self.rock_rect.x-2, self.rock_rect.y-2))

            # duration
            self.rock_time_duration -= 0.1
            if self.rock_time_duration <= 0: self.rock_moving = False

    # attack 1
        if self.particle_frame_index_1 < len(self.attack_particles_1) -1 and self.attack:
            self.particle_frame_index_1 += self.particle_animation_speed

            attack_particles_1 = self.attack_particles_1[int(self.particle_frame_index_1)]

            if self.particle_frame_index_1 >= 0:
                if self.facing_right:
                    pos = self.rect.topright + pygame.math.Vector2(-40, 15)
                    self.display_surface.blit(attack_particles_1, pos)
                else:
                    pos = self.rect.topleft + pygame.math.Vector2(-25, 15)
                    flipped_attack_particle = pygame.transform.flip(attack_particles_1, True, False)
                    self.display_surface.blit(flipped_attack_particle, pos)
    #attack 2
        if self.particle_frame_index_2 < len(self.attack_particles_2) -1 and self.attack:
            self.particle_frame_index_2 += self.particle_animation_speed

            attack_particles_2 = self.attack_particles_2[int(self.particle_frame_index_2)]
            attack_particles_2 = pygame.transform.rotozoom(attack_particles_2,-20,2)
            if self.particle_frame_index_2 >= 0:
                if self.facing_right:
                    pos = self.rect.topright + pygame.math.Vector2(-105, -30)
                    self.display_surface.blit(attack_particles_2, pos)
                else:
                    pos = self.rect.topleft + pygame.math.Vector2(-50, -30)
                    flipped_attack_particle = pygame.transform.flip(attack_particles_2, True, False)
                    self.display_surface.blit(flipped_attack_particle, pos)
    #attack 3
        if self.particle_frame_index_3 < len(self.attack_particles_3) -1 and self.attack3:
            self.particle_frame_index_3 += self.particle_animation_speed
            attack_particles_3 = self.attack_particles_3[int(self.particle_frame_index_3)]
            attack_particles_3 = pygame.transform.rotozoom(attack_particles_3,-20,1.5)
            if self.particle_frame_index_3 >= 0:
                if self.facing_right:
                    pos = self.rect.topright + pygame.math.Vector2(-95, -30)
                    self.display_surface.blit(attack_particles_3, pos)
                else:
                    pos = self.rect.topleft + pygame.math.Vector2(-35, -30)
                    flipped_attack_particle = pygame.transform.flip(attack_particles_3, True, False)
                    self.display_surface.blit(flipped_attack_particle, pos)

    def get_status(self):
        keys = pygame.key.get_pressed()
        if self.player_mode == 'death'  and self.on_ground:
            self.status = 'death'
            if self.death_frame == 0:
                self.frame_index = 0
                self.death_frame = 1
        elif self.status != 'in' :
            self.death_frame = 0
    ##------------------------AIR -----------------------------------------------------------------
            if self.direction.y < self.gravity and self.on_ground == False :
                if self.attack3:
                    self.status = 'jump2'
                else:
                    self.status = 'jump'

                if self.dash_speed >= 1: self.dash_speed = self.absolute_speed
            elif self.direction.y > self.gravity:
                if self.attack3:
                    self.status = 'jump2'
                else:
                    self.status = 'fall'
                self.attack = False
                self.throw = False
                if self.dash_speed >= 1:
                    self.dash_speed = self.absolute_speed
                    self.dash_time = 0
    ##------------------------GROUND --------------------------------------------------------------
            else:
                if self.on_ground:
                    self.touch_ground = True
                    self.attack3 = False
                if self.direction.x != 0:
                    if self.player_mode == 'push' and self.stamina > 0 and not self.tired:
                        self.status = 'push'
                        if self.stamina >= 0:
                            self.stamina -= 0.5
                            self.change_stamina(-0.5)
                    else:
                        if keys[pygame.K_LSHIFT] and self.stamina > 0 and not self.tired and not self.on_climb:
                            self.status = 'run2'
                            self.stamina -= 0.4
                            self.change_stamina(-0.4)
                            if self.dash_time >= 0:
                                if self.dash_time == 10:
                                    self.dash_sound.play()
                                    self.stamina -= 6
                                    self.change_stamina(-6)
                                self.status = 'dash'
                                self.dash_speed = self.absolute_speed*3
                                self.dash_time -= 1
                            else:
                                self.dash_speed = self.absolute_speed
                        else:
                            self.status = 'run'
                            self.dash_speed = 0
                            self.dash_time = 10
                else:
                    if self.attack:
                        if not self.attack2:
                            self.status = 'attack1'
                        elif self.attack2:
                            self.status = 'attack2'
                    else:
                        self.status = 'idle'

                        if self.throw:
                            self.status = 'throw'

            if self.on_climb:
                self.status = 'climb'
                self.attack3 = False
                self.dash_speed = 0

        if self.attack:
            self.combo_delay += 1

    def get_input(self):
        self.jump_delay += 1
        if self.player_mode != 'death' and self.status != 'in' and self.player_mode != 'wait':
            keys = pygame.key.get_pressed()

            if keys[pygame.K_RIGHT] and not self.attack and not self.throw:
                self.direction.x = 1
                self.facing_right = True
                if self.on_climb: self.frame_index += self.animation_speed
            elif keys[pygame.K_LEFT] and not self.attack and not self.throw:
                self.direction.x = -1
                self.facing_right = False
                if self.on_climb: self.frame_index += self.animation_speed
            else:
                self.direction.x = 0

            if keys[pygame.K_SPACE] and self.on_ground and self.jump_delay >= 20:
                self.jump()

            if keys[pygame.K_RETURN]:
                self.create_attack()
                if not self.on_ground and self.touch_ground:
                    self.touch_ground = False
                    self.jump_attack()


            if keys[pygame.K_LCTRL]:
                if keys[pygame.K_UP]: self.rock_angle = 5
                elif keys[pygame.K_DOWN]: self.rock_angle = -5
                else:self.rock_angle = 0
                self.create_throw()

            if keys[pygame.K_UP] or keys[pygame.K_DOWN]:
                self.up_down = True


        else: self.direction.x = 0

    def create_throw(self):
        if self.on_ground and not self.attack and not self.throw and not self.rock_moving and self.stamina > 30:
            self.throw2_sound.play()
            self.throw = True
            self.frame_index = 0
            self.particle_frame_index_rock1 = 0
            self.v_x = 10 -self.rock_angle * 0.75
            self.v_y = -6 -self.rock_angle * 1.25
            self.rock_time_duration = 20
            self.stamina -= 30
            self.change_stamina(-30)

    def create_attack(self):
        if self.on_ground and self.attack == False and self.throw == False and self.stamina > 0 and not self.tired and not self.on_climb:
            self.attack = True
            self.attack1_sound.play()
            self.combo_delay = 0
            self.frame_index = 0
            if self.facing_right: self.direction.x = 1
            if not self.facing_right: self.direction.x = -1
            self.dash_speed = 1
            self.particle_frame_index_1 = -2
            self.stamina -= 2
            self.change_stamina(-2)

        else:
            if self.status == 'attack1' and self.combo_delay > 8 and self.stamina > 0 and not self.tired:
                self.attack2 = True
                self.attack2_sound.play()
                self.frame_index = 0
                if self.facing_right: self.direction.x = 1
                if not self.facing_right: self.direction.x = -1
                self.dash_speed = 1
                self.particle_frame_index_2 = 0
                self.stamina -= 6
                self.change_stamina(-6)

    def apply_gravity(self):
        if not self.on_climb:
            if self.direction.y <= self.player_flow: self.direction.y += self.gravity
            self.collision_rect.y += self.direction.y
        if self.v_y <= self.player_flow and self.rock_moving: self.v_y += self.gravity/2

    def jump(self):
        if self.stamina > 0 and not self.tired and not self.on_climb:
            self.jump_delay = 0
            self.direction.y = self.jump_speed
            self.jump_sound.play()
            self.create_jump_particles(self.rect.midbottom)
            self.frame_index = 0
            self.attack = False
            self.stamina -= 10
            self.change_stamina(-10)
            self.second_jump = False

    def jump_attack(self):
        if self.stamina > 0 and not self.tired and not self.on_climb and not self.attack3:
            self.direction.y = self.jump_speed*0.7
            self.jump_delay = 0
            self.particle_frame_index_3 = -2
            self.frame_index = 0
            self.stamina -= 10
            self.change_stamina(-10)
            self.attack3 = True
            self.attack3_sound.play()

    def get_damage(self, damage):
        if not self.invincible:
            self.hit_sound.play()
            self.change_health(-damage)
            self.invincible = True
            self.hurt_time = pygame.time.get_ticks()

    def invincibility_timer(self):
        if self.invincible:
            concurrent_time = pygame.time.get_ticks()
            if concurrent_time - self.hurt_time >= self.invincibility_duration:
                self.invincible = False

    def wave_value(self):
        value = sin(pygame.time.get_ticks())
        if value >= 0: return 255
        else: return 0

    def stamina_reload(self):
        if self.stamina <= 0: self.tired = True
        if self.stamina >= 20: self.tired = False
        if self.stamina < 100:
            self.stamina += 0.2
            self.change_stamina(0.2)

    def update(self):
        self.get_input()
        self.get_status()
        self.animate()
        self.stamina_reload()
        self.run_dust_animation()
        self.run_attack_animation()
        self.invincibility_timer()
        self.wave_value()




