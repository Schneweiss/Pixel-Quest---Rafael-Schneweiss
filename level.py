import pygame
from tiles import Tile, StaticTile, Crate, Palm, Door, Npc, Heart, Rain
from settings import *
from player import Player
from particles import ParticleEffect
from support import import_csv_layout, import_cut_graphics
from enemy import Enemy
from decoration import Sky, Water, Clouds
from game_data import levels
from math import sin
from text import TextLoader
from random import randint

class Level:
    def __init__(self, current_level, surface, create_overworld, change_coins, change_health, cur_health, change_stamina, coin_sprites, player_ref, boss_sprites):
        #level setup
        self.display_surface = surface
        if current_level == 11 or current_level == 12: player_ref=[0,0,0,0,0,0]
        self.world_shift = player_ref[0]
        self.world_shifty = player_ref[1]
        self.level_pos = player_ref[2]
        self.level_posy = player_ref[3]
        self.night = True
        self.mood = 'night'
        self.rain = True
        self.center = False

        #audio
        self.coins_sound = pygame.mixer.Sound('audio/effects/coin.wav')
        self.coins_sound.set_volume(1)
        self.stomp_sound = pygame.mixer.Sound('audio/effects/stomp.wav')
        self.stomp_sound.set_volume(1)
        self.hit_sound = pygame.mixer.Sound('audio/effects/Hit_01.mp3')
        self.door_sound = pygame.mixer.Sound('audio/effects/door.wav')
        self.heart_sound = pygame.mixer.Sound('audio/effects/heart.mp3')
        self.rain_sound = pygame.mixer.Sound('audio/effects/rain.mp3')
        self.rain_sound.set_volume(0.4)
        self.level_sound = pygame.mixer.Sound('audio/tension.mp3')
        if current_level == 0:  self.level_sound.play()
        self.boss_sound = pygame.mixer.Sound('audio/boss.mp3')
        self.boss_sound.set_volume(1)

        #overworld connection
        self.create_overworld = create_overworld
        self.current_level = current_level
        level_data = levels[self.current_level]
        self.new_max_level = level_data['unlock']
        self.cur_health = cur_health
        self.change_stamina = change_stamina
        self.cur_stamina = 100
        self.death_delay = 0
        #player
        player_layout = import_csv_layout(level_data['player'])
        self.player = pygame.sprite.GroupSingle()
        self.goal = pygame.sprite.GroupSingle()
        self.player_setup(player_layout, change_health, change_stamina)
        self.player_push = "Null"
        self.player.sprite.collision_rect.x += player_ref[4]
        self.player.sprite.collision_rect.y += player_ref[5]
        self.collect_ref = False
        self.fade_out = False
        self.door_level = 0
        #dynamic objects
        self.crate_collide = False
        self.direction_crate = pygame.math.Vector2(0, 0)
        self.show_text = False
        #user interface
        self.change_coins = change_coins
        #terrain setup
        terrain_layout = import_csv_layout(level_data['terrain'])
        self.terrain_sprites = self.create_tile_group(terrain_layout, 'terrain')
        terrain_bg_layout = import_csv_layout(level_data['terrain_bg'])
        self.terrain_bg_sprites = self.create_tile_group(terrain_bg_layout, 'terrain_bg')

        terrain_masonry_layout = import_csv_layout(level_data['terrain_masonry'])
        self.terrain_masonry_sprites = self.create_tile_group(terrain_masonry_layout, 'terrain_masonry')
        # masonry_bg
        masonry_layout = import_csv_layout(level_data['masonry'])
        self.masonry_sprites = self.create_tile_group(masonry_layout, 'masonry')
        #decoration_masonry
        decoration_masonry_layout = import_csv_layout(level_data['decoration_masonry'])
        self.decoration_masonry_sprites = self.create_tile_group(decoration_masonry_layout, 'decoration_masonry')
        # masonry_roof_plataform
        masonry_collide_layout = import_csv_layout(level_data['masonry_collide'])
        self.masonry_collide_sprites = self.create_tile_group(masonry_collide_layout, 'masonry_collide')
        #village
        village_layout = import_csv_layout(level_data['village'])
        self.village_sprites = self.create_tile_group(village_layout, 'village')
        #door_masonry
        door_layout = import_csv_layout(level_data['door'])
        self.door_sprites = self.create_tile_group(door_layout, 'door')
        #npc
        npc_layout = import_csv_layout(level_data['npc'])
        self.npc_sprites = self.create_tile_group(npc_layout, 'npc')
        #grass setup
        grass_layout = import_csv_layout(level_data['grass'])
        self.grass_sprites = self.create_tile_group(grass_layout, 'grass')
        #crates setup
        crates_layout = import_csv_layout(level_data['crates'])
        self.crates_sprites = self.create_tile_group(crates_layout, 'crates')
        #ladder setup
        ladder_layout = import_csv_layout(level_data['ladder'])
        self.ladder_sprites = self.create_tile_group(ladder_layout, 'ladder')
        #coins
        self.coins_sprites = coin_sprites[current_level]
        #bosses
        self.boss_sprites = boss_sprites[current_level]
        #hearts
        self.heart_sprites = pygame.sprite.Group()
        self.heart_fx_sprites = pygame.sprite.Group()
        #foreground palms
        fg_palm_layout = import_csv_layout(level_data['fg palms'])
        self.fg_palms_sprites = self.create_tile_group(fg_palm_layout, 'fg palms')
        #bg palms
        bg_palm_layout = import_csv_layout(level_data['bg palms'])
        self.bg_palms_sprites = self.create_tile_group(bg_palm_layout, 'bg palms')
        #enemy
        enemy_layout = import_csv_layout(level_data['enemies'])
        self.enemy_sprites = self.create_tile_group(enemy_layout, 'enemies')
        self.enemy_range = 500
        #constraint
        constraint_layout = import_csv_layout(level_data['constraint'])
        self.constraint_sprites = self.create_tile_group(constraint_layout, 'constraint')
        #decoration
        self.sky = Sky(6, mood = self.mood)
        level_width = len(terrain_layout[0]) * tile_size
        self.level_width = level_width
        self.water= Water(screen_height - 120, level_width + 200)
        self.clouds = Clouds(level_offset  + 200, level_width, 30)
        #textloader
        self.text_loader = TextLoader()
        #dust
        self.dust_sprite = pygame.sprite.GroupSingle()
        self.player_on_ground = False
        #explosion
        self.explosion_sprites = pygame.sprite.Group()
        #water splash
        self.splash_sprites = pygame.sprite.Group()
        #up icon
        self.up_icon_sprites = pygame.sprite.Group()

        #rain
        self.rain_sprites = pygame.sprite.Group()
        if self.rain:
            self.rain_sprites.add(self.create_rain())
        else:
            self.rain_sound.stop()

    def input(self):
        player = self.player.sprite
        keys = pygame.key.get_pressed()
        if keys[pygame.K_p]:
            self.create_overworld(self.current_level, self.new_max_level)
        if keys[pygame.K_ESCAPE]:
            self.create_overworld(self.current_level, 0)

        #pygame.draw.rect(self.display_surface, 'yellow', pygame.Rect(heart.rect), 2)
        # pygame.draw.rect(self.display_surface, 'yellow', pygame.Rect(crates.rect), 2)
        #pygame.draw.rect(self.display_surface, 'yellow', pygame.Rect(player.collision_rect), 2)
        #pygame.draw.rect(self.display_surface, 'red', pygame.Rect(player.attack_rect), 2)
        # if player.rock_moving: pygame.draw.rect(self.display_surface, 'red', pygame.Rect(player.rock_rect), 2)
        #for enemie in self.enemy_sprites.sprites():
        #    pygame.draw.rect(self.display_surface, 'red', pygame.Rect(enemie.rect), 2)

    def create_tile_group(self, layout, type):
        sprite_group = pygame.sprite.Group()

        for row_index, row in enumerate(layout):
            for col_index, val in enumerate(row):
                if val != '-1':
                    x = col_index * tile_size
                    y = row_index * tile_size - level_offset

                    if type == 'terrain' or type == 'terrain_bg':
                        terrain_tile_list = import_cut_graphics('graphics/terrain/tilesets/terrain_tiles.png')
                        tile_surface = terrain_tile_list[int(val)]
                        sprite = StaticTile(tile_size, x, y, tile_surface)

                    if type == 'terrain_masonry' or type == 'masonry' :
                        terrain_tile_list = import_cut_graphics('graphics/terrain/tilesets/masonry/terrain.png')
                        tile_surface = terrain_tile_list[int(val)]
                        sprite = StaticTile(tile_size, x, y, tile_surface)

                    if type == 'village':
                        terrain_tile_list = import_cut_graphics('graphics/decoration/village/TX Village Props.png')
                        tile_surface = terrain_tile_list[int(val)]
                        sprite = StaticTile(tile_size, x, y, tile_surface)

                    if type == 'decoration_masonry':
                        terrain_tile_list = import_cut_graphics('graphics/terrain/tilesets/masonry/Decorations.png')
                        tile_surface = terrain_tile_list[int(val)]
                        sprite = StaticTile(tile_size, x, y, tile_surface)

                    if type == 'masonry_collide':sprite = Tile(tile_size,x,y)

                    if type == 'door':
                        sprite = Door(tile_size, x, y, 'graphics/decoration/door', 40, val)

                    if type == 'npc':
                        if val == '0': sprite = Npc(tile_size, x, y, 'graphics/npc/old_man', 15, val)
                        if val == '1': sprite = Npc(tile_size, x, y, 'graphics/npc/bomb_guy', 12, val)
                        if val == '2': sprite = Npc(tile_size, x, y, 'graphics/npc/runner', 0, val)

                    if type == 'grass':
                        grass_tile_list = import_cut_graphics('graphics/decoration/grass/grass.png')
                        tile_surface = grass_tile_list[int(val)]
                        sprite = StaticTile(tile_size, x, y, tile_surface)

                    if type == 'crates':
                        sprite = Crate(tile_size, x, y)

                    if type == 'fg palms':
                        if val == '0': sprite = Palm(tile_size, x, y, 'graphics/terrain/palm_small', 38)
                        if val == '1': sprite = Palm(tile_size, x, y, 'graphics/terrain/palm_large', 70)

                    if type == 'bg palms':
                        sprite = Palm(tile_size, x, y, 'graphics/terrain/palm_bg', 64)

                    if type == 'ladder':
                        if val == '0': sprite = StaticTile(tile_size, x, y, pygame.image.load('graphics/terrain/ladder/Ladder2.png').convert_alpha())
                        if val == '1': sprite = StaticTile(tile_size, x, y, pygame.image.load('graphics/terrain/ladder/Ladder1.png').convert_alpha())

                    if type == 'enemies':
                        self.enemy_type = val
                        if val == '0': sprite = Enemy(tile_size, x, y, 'graphics/enemy/slime/run', val, self.display_surface)
                        if val == '1': sprite = Enemy(tile_size, x, y, 'graphics/enemy/tooth/run', val, self.display_surface)
                        if val == '2': sprite = Enemy(tile_size, x, y, 'graphics/enemy/pig/run', val, self.display_surface)
                        if val == '3': sprite = Enemy(tile_size, x, y, 'graphics/enemy/bird', val, self.display_surface)
                        if val == '5': sprite = Enemy(tile_size, x, y, 'graphics/enemy/gargoyle', val, self.display_surface)

                    if type == 'constraint': sprite = Tile(tile_size,x,y)


                    sprite_group.add(sprite)

        return sprite_group

    def create_rain(self):
        sprite_group = pygame.sprite.Group()
        rain_range = 500
        self.rain_sound.play(loops=-1)
        for i in range(rain_range):
            sprite = Rain(0, i*screen_width/rain_range,i*screen_height/rain_range)
            sprite_group.add(sprite)
        return sprite_group

    def create_heart_group(self, x, y, type):
        sprite_group = pygame.sprite.Group()
        if type != -1:
            if type == 0: path = 'graphics/hearts/mini'
            if type == 1: path = 'graphics/hearts/big'
            sprite = Heart(x, y, path, type)
            sprite_group.add(sprite)
        return sprite_group

    def player_setup(self, layout, change_health, change_stamina):
        for row_index, row in enumerate(layout):
            for col_index, val in enumerate(row):
                x = col_index * tile_size
                y = row_index * tile_size - level_offset
                if val == '0':
                    sprite = Player((x,y), self.display_surface, self.create_jump_particles, change_health, change_stamina)
                    self.player.add(sprite)
                    self.player_init_x = x
                    self.player_init_y = y
                if val == '1':
                    hat_surface = pygame.image.load('graphics/character/hat.png').convert_alpha()
                    sprite = StaticTile(tile_size, x, y, hat_surface)
                    self.goal.add(sprite)

    def create_jump_particles(self, pos):
        if self.player.sprite.facing_right:
            pos -= pygame.math.Vector2(0,  5)
        else:
            pos += pygame.math.Vector2(0, -5)

        jump_particle_sprite = ParticleEffect(pos, 'jump')
        self.dust_sprite.add(jump_particle_sprite)

    def get_player_on_ground(self):
        if self.player.sprite.on_ground:
            self.player_on_ground = True
        else:
            self.player_on_ground = False

    def create_landing_dust(self):
        if not self.player_on_ground and self.player.sprite.on_ground and not self.dust_sprite.sprites():
            if self.player.sprite.facing_right:
                offset = pygame.math.Vector2(10, 15)
            else:
                offset = pygame.math.Vector2(-10, 15)
            fall_dust_particle = ParticleEffect(self.player.sprite.rect.midbottom -offset,'land')
            self.dust_sprite.add(fall_dust_particle)

    def scroll_x(self):
        player = self.player.sprite
        player_x = player.collision_rect.x
        direction_x = player.direction.x

        #worldshift
        if player_x < screen_width / 3 and direction_x < 0 and self.level_pos > 0 +10:
            self.world_shift = player.init_speed + player.dash_speed
            self.level_pos -= self.world_shift
            player.speed = player.init_speed - self.world_shift
        elif player_x > screen_width - (screen_width / 3) and direction_x > 0 and self.level_pos < (self.level_width - (screen_width) ) -10:
            self.world_shift =- player.init_speed - player.dash_speed
            self.level_pos -= self.world_shift
            player.speed = player.init_speed + self.world_shift
        else:
            self.world_shift = 0
            player.speed = player.init_speed+ player.dash_speed

    def scroll_y(self):
        player = self.player.sprite
        player_y = player.collision_rect.centery
        #screen up
        if player_y < screen_height_play/3 + 100 and self.level_posy > -level_offset +20:
            self.world_shifty = int(abs(player.direction.y)) + 2
            self.level_posy -= self.world_shifty
            player.collision_rect.y += self.world_shifty
        #screen down
        elif player_y > screen_height_play*2/3 and self.level_posy < -20:
            self.world_shifty = -int(abs(player.direction.y)) - 2
            self.level_posy -= self.world_shifty
            player.collision_rect.y += self.world_shifty

        else:
            self.world_shifty = 0

    def centralize(self):
        player = self.player.sprite
        player_x = player.collision_rect.x

        #worldshift
        if player_x < screen_width / 2 and self.level_pos > 0 +10:
            self.world_shift += 1
            self.level_pos -= self.world_shift
            player.collision_rect.x += 1
        elif player_x > screen_width / 2 and self.level_pos < (self.level_width - (screen_width) ) -10:
            self.world_shift -= 1
            self.level_pos -= self.world_shift
            player.collision_rect.x -= 1

    def horizontal_object_collision(self):
        # detect collision for crates
        player = self.player.sprite
        collidable_sprites = self.terrain_sprites.sprites() + self.fg_palms_sprites.sprites() + self.crates_sprites.sprites() +self.terrain_masonry_sprites.sprites()
        enemie_sprites =  self.enemy_sprites.sprites() + self.boss_sprites.sprites()
        if player.status == 'push':

            for crates in self.crates_sprites.sprites():
                if crates.rect.colliderect(player.collision_rect):
                    if player.direction.x < 0 and player.collision_rect.centerx > crates.rect.centerx:
                        crates.rect.x -= 1
                    elif player.direction.x > 0 and player.collision_rect.centerx < crates.rect.centerx:
                        crates.rect.x += 1
                    for sprite in collidable_sprites:
                        if sprite.rect.colliderect((crates.rect)) and sprite!= crates:
                            if player.direction.x < 0:
                                crates.rect.left = sprite.rect.right
                            elif player.direction.x > 0:
                                crates.rect.right = sprite.rect.left
                    for enemie in enemie_sprites:
                        if enemie.collision_rect.colliderect((crates.rect)):
                            if player.direction.x < 0:
                                crates.rect.left = enemie.collision_rect.right
                            elif player.direction.x > 0:
                                crates.rect.right = enemie.collision_rect.left

    def horizontal_movement_collision(self):
        player = self.player.sprite
        player.collision_rect.x += player.direction.x * (player.speed + player.dash_speed)
        collidable_sprites = self.terrain_sprites.sprites() + self.crates_sprites.sprites() + self.fg_palms_sprites.sprites()+ self.terrain_masonry_sprites.sprites()
        #collisions overhaul
        self.player_push = False
        for sprite in collidable_sprites:
            if sprite.rect.colliderect(player.collision_rect) and not player.on_climb:
                self.player_push = True
                self.horizontal_object_collision()
                if player.collision_rect.centerx > sprite.rect.centerx:
                    player.collision_rect.left = sprite.rect.right
                elif player.collision_rect.centerx < sprite.rect.centerx:
                    player.collision_rect.right = sprite.rect.left

    def enemy_collision_reverse(self):
        enemie_sprites = self.enemy_sprites.sprites() + self.boss_sprites.sprites()
        for enemy in enemie_sprites:
            if enemy.enemy_type != '3' and enemy.enemy_type != '5':
                for constrain in self.constraint_sprites:
                    if constrain.rect.colliderect(enemy.rect):
                        if enemy.speed < 0:
                            enemy.rect.left = constrain.rect.right
                        elif enemy.speed > 0:
                            enemy.rect.right = constrain.rect.left
                        enemy.reverse()


        for enemy in enemie_sprites:
            for crates in self.crates_sprites:
                if crates.rect.colliderect(enemy.rect):
                    if enemy.speed < 0:
                        enemy.rect.left = crates.rect.right
                    elif enemy.speed > 0:
                        enemy.rect.right = crates.rect.left
                    enemy.reverse()

    def rock_collisions(self):
        player = self.player.sprite
        collidable_sprites = self.terrain_sprites.sprites() + self.fg_palms_sprites.sprites() + self.crates_sprites.sprites() +self.terrain_masonry_sprites.sprites()
        enemies_sprites = self.enemy_sprites.sprites() + self.boss_sprites.sprites()
        #rock collisions
        if player.rock_moving:
            #scroll
            player.rock_rect.x += self.world_shift
            player.rock_rect.y += self.world_shifty
            player.world_shift = self.level_pos
            # collisions
            for sprite in collidable_sprites:
                if sprite.rect.colliderect((player.rock_rect)):
                    relative_x = player.rock_rect.centerx - sprite.rect.centerx
                    relative_y = player.rock_rect.centery - sprite.rect.centery

                    if abs(relative_x) > abs(relative_y):
                        if relative_x < 0:
                            if player.v_x < 0: player.v_x *= 1 / 2
                            else: player.v_x *= - 1 / 2
                        else:
                            if player.v_x < 0: player.v_x *= -1 / 2
                            else: player.v_x *=  1 / 2
                    elif abs(relative_x) < abs(relative_y):
                        if relative_y < 0:
                            if player.v_y > 0: player.v_y *= -1/2
                            else: player.v_y *= 1/2
                        else:
                            if player.v_y > 0: player.v_y *= 1
                            else: player.v_y *= -1
                        player.v_x *= 0.95
            for sprite in enemies_sprites:
                if sprite.collision_rect.colliderect((player.rock_rect)):
                    relative_x = player.rock_rect.centerx - sprite.collision_rect.centerx
                    relative_y = player.rock_rect.centery - sprite.collision_rect.centery

                    if abs(relative_x) > abs(relative_y):
                        if relative_x < 0:
                            if player.v_x < 0:
                                player.v_x *= 1 / 2
                            else:
                                player.v_x *= - 1 / 2
                        else:
                            if player.v_x < 0:
                                player.v_x *= -1 / 2
                            else:
                                player.v_x *= 1 / 2
                    elif abs(relative_x) < abs(relative_y):
                        if relative_y < 0:
                            if player.v_y > 0:
                                player.v_y *= -1 / 2
                            else:
                                player.v_y *= 1 / 2
                        else:
                            if player.v_y > 0:
                                player.v_y *= 1
                            else:
                                player.v_y *= -1
                        player.v_x *= 0.95

    def vertical_object_collision(self):
        player = self.player.sprite
        collidable_sprites = self.terrain_sprites.sprites() + self.fg_palms_sprites.sprites() + self.crates_sprites.sprites() + self.masonry_collide_sprites.sprites()+self.terrain_masonry_sprites.sprites()

        #crates collisions
        for crates in self.crates_sprites.sprites():
            crates.rect.y += player.player_flow
            #if crates.rect.bottom > screen_height_play - 95 - self.level_posy: crates.rect.y -=16 + sin(pygame.time.get_ticks()/100)*2 + 0.5
            for sprite in collidable_sprites:
                if sprite.rect.colliderect((crates.rect)) and sprite != crates:
                    crates.rect.bottom = sprite.rect.top

        # hearts collisions
        for heart in self.heart_sprites.sprites():
            heart.rect.y += 1
            move = sin(pygame.time.get_ticks() / 200) * 2 + 0.5
            for sprite in collidable_sprites:
                if sprite.rect.colliderect((heart.rect)) and sprite != heart:
                    heart.rect.bottom = sprite.rect.top
                    move = 0
            heart.rect.x += move

    def vertical_movement_collision(self):
        player = self.player.sprite
        player.apply_gravity()
        player.collision_rect.x += player.impact

        keys = pygame.key.get_pressed()
        collidable_sprites = self.terrain_sprites.sprites() + self.crates_sprites.sprites() + self.fg_palms_sprites.sprites()+self.terrain_masonry_sprites.sprites()
        for sprite in collidable_sprites:
            if sprite.rect.colliderect(player.collision_rect):
                if player.direction.y > 0 and player.collision_rect.bottom < sprite.rect.centery:
                    player.collision_rect.bottom = sprite.rect.top
                    player.direction.y = 0
                    player.on_ground = True
                    player.impact = 0
                elif player.direction.y < 0 and player.collision_rect.top > sprite.rect.centery:
                    player.collision_rect.top = sprite.rect.bottom
                    player.direction.y = player.gravity
                    player.on_ceiling = True

        for plataform in self.masonry_collide_sprites.sprites():
            if plataform.rect.colliderect(player.collision_rect):
                if player.direction.y > 0 and player.collision_rect.bottom < plataform.rect.centery and not keys[pygame.K_DOWN]:
                    player.collision_rect.bottom = plataform.rect.top
                    player.direction.y = 0
                    player.on_ground = True



        if player.on_ground and player.direction.y < 0 or player.direction.y > 1:
            player.on_ground = False

    def check_death(self):
        player = self.player.sprite
        offset = pygame.math.Vector2(0, 30)
        if player.rect.top > screen_height_play:
            player.change_health(-100)

    def check_win(self):
        if pygame.sprite.spritecollide(self.player.sprite, self.goal, False):
            self.create_overworld(self.current_level,self.new_max_level)

    def check_coin_collisions(self):
        collided_coins = pygame.sprite.spritecollide(self.player.sprite, self.coins_sprites, True)
        if collided_coins:
            self.coins_sound.play()
            for coin in collided_coins:
                self.change_coins(coin.value)

    def check_heart_collisions(self):
        collided_hearts = pygame.sprite.spritecollide(self.player.sprite, self.heart_sprites, True)
        if collided_hearts:
            self.heart_sound.play()
            for heart in collided_hearts:
                self.player.sprite.change_health(heart.value)
                heart.kill()
                fx_sprite = ParticleEffect(heart.rect.center, 'heart_fx')
                self.heart_fx_sprites.add(fx_sprite)

    def check_enemy_collisions(self):
        objects = self.crates_sprites.sprites()
        player = self.player.sprite
        collidable_sprites = self.enemy_sprites.sprites()+ self.boss_sprites.sprites()
        #enemy collision
        if not self.player.sprite.invincible:
            for sprite in collidable_sprites:
                if sprite.collision_rect.colliderect(player.collision_rect):
                    enemy_center = sprite.rect.centery
                    player_bottom = player.collision_rect.bottom
                    if player_bottom < enemy_center and self.player.sprite.direction.y > 0 and not sprite.invincible:
                         #damage
                         sprite.life -= 20
                         sprite.invincible = True
                         self.player.sprite.direction.y *= -0.8
                         self.hit_sound.play()
                         if sprite.enemy_type == '4': sprite.hurt = True
                         #impact
                         enemy_centerx = sprite.rect.centerx
                         if enemy_centerx > player.collision_rect.centerx:
                             sprite.impact = 16
                         else:
                             sprite.impact = -16
                         if sprite.life <= 0:
                             self.stomp_sound.play()
                             self.player.sprite.direction.y = -5
                             explosion_sprite = ParticleEffect(sprite.rect.center, 'explosion')
                             self.explosion_sprites.add(explosion_sprite)
                             sprite.kill()
                             self.gen_heart(sprite.rect.centerx, sprite.rect.centery)
                    else:
                         if not sprite.invincible:
                            self.player.sprite.direction.y = -5
                            self.player.sprite.get_damage(10)
                            if sprite.enemy_type == '4':
                                enemy_centerx = sprite.rect.centerx
                                if enemy_centerx > player.collision_rect.centerx:
                                    player.impact = -10
                                else:
                                    player.impact = 10


        # crate impact on player
            for crates in self.crates_sprites.sprites():
                if crates.rect.colliderect(player.collision_rect):
                    player_center = player.collision_rect.centery
                    player_top = player.collision_rect.top
                    if player_top < crates.rect.bottom < player_center:
                        self.player.sprite.direction.y = -5
                        if player.collision_rect.centerx > crates.rect.centerx:
                            player.direction.x = 1
                        elif player.collision_rect.centerx < crates.rect.centerx:
                            player.direction.x  = -1
                        self.player.sprite.get_damage(30)

        # crates impact on enemy
        for sprites in collidable_sprites:
           for crates in objects:
               if sprites.rect.colliderect(crates.rect):
                    enemy_center = sprites.rect.centery
                    enemy_top = sprites.rect.top
                    if  enemy_top < crates.rect.bottom < enemy_center:

                        self.stomp_sound.play()
                        explosion_sprite = ParticleEffect(sprites.rect.center, 'explosion')
                        self.explosion_sprites.add(explosion_sprite)
                        sprites.kill()
                        self.gen_heart(sprite.rect.centerx, sprite.rect.centery)

    def enemy_status(self):
        player = self.player.sprite
        collidable_sprites = self.enemy_sprites.sprites()+ self.boss_sprites.sprites()
        for sprite in collidable_sprites:
            #pig
            if sprite.enemy_type == '2':
                enemy_centerx = sprite.collision_rect.centerx
                enemy_centery = sprite.collision_rect.centery
                relative_distance = enemy_centerx - player.collision_rect.centerx
                relative_height = abs(enemy_centery - player.collision_rect.centery)

                if sprite.enemy_idle:
                    if player.status != 'run' and player.status != 'idle':
                        self.enemy_range = 500
                    else:
                        self.enemy_range = 150
                if relative_distance > 0 and sprite.speed < 0: self.enemy_range = 500
                if relative_distance < 0 and sprite.speed > 0: self.enemy_range = 500

                if abs(relative_distance) > self.enemy_range or relative_height > 100:
                    sprite.enemy_idle = True
                else:
                    if relative_distance > 0:
                        if sprite.speed > 0: sprite.reverse()
                    if relative_distance < 0:
                        if sprite.speed < 0: sprite.reverse()
                    sprite.enemy_idle = False
            #tooth
            if sprite.enemy_type == '1':
                enemy_centerx = sprite.collision_rect.centerx
                enemy_centery = sprite.collision_rect.centery
                relative_distance = enemy_centerx - player.collision_rect.centerx
                relative_height = abs(enemy_centery - player.collision_rect.centery)
                #drowning parameters
                if enemy_centery > screen_height_play - 120 - self.level_posy:
                    sprite.status = 'underwater'
                    sprite.rect.y += int(sin(pygame.time.get_ticks()/100)*2)
                else:
                    #idle and run parameters
                    if sprite.enemy_idle:
                        if player.status != 'run' and player.status != 'idle':
                            self.enemy_range = 500
                        else:
                            self.enemy_range = 150
                    if relative_distance > 0 and sprite.speed < 0: self.enemy_range = 500
                    if relative_distance < 0 and sprite.speed > 0: self.enemy_range = 500

                    if abs(relative_distance) > self.enemy_range or relative_height > 100:
                        if sprite.status!= 'attack': sprite.enemy_idle = True
                    else:
                        if relative_distance > 0:
                            if sprite.speed > 0: sprite.reverse()
                        if relative_distance < 0:
                            if sprite.speed < 0: sprite.reverse()
                        sprite.enemy_idle = False
                        if abs(relative_distance) < 45:
                            sprite.attack = True
                        else:
                            sprite.attack = False
            #bird/gargolye
            if sprite.enemy_type == '3' or sprite.enemy_type == '5':
                enemy_centerx = sprite.collision_rect.centerx
                enemy_centery = sprite.collision_rect.centery
                relative_distance = enemy_centerx - player.collision_rect.centerx
                relative_height = enemy_centery - player.collision_rect.centery
                self.enemy_range = 600
                if abs(relative_distance) > self.enemy_range or abs(relative_height) > 500:
                    sprite.enemy_idle = True
                    sprite.rect.y += sin(pygame.time.get_ticks() / 100)  + 0.5
                    sprite.anim_ratio = 3
                else:
                    if relative_distance > 0:
                        if sprite.speed > 0: sprite.reverse()
                    if relative_distance < 0:
                        if sprite.speed < 0: sprite.reverse()
                    if relative_height < 0:
                        sprite.rect.y += 1
                        sprite.anim_ratio = 4
                    if relative_height > 0:
                        sprite.rect.y -= 1
                        sprite.anim_ratio = 2
                    sprite.enemy_idle = False
            #boss_0
            if sprite.enemy_type == '4':
                if not sprite.speak:
                    enemy_centerx = sprite.collision_rect.centerx
                    enemy_centery = sprite.collision_rect.centery
                    relative_distance = enemy_centerx - player.collision_rect.centerx
                    relative_height = abs(enemy_centery - player.collision_rect.centery)
                    self.enemy_range = 500
                    if sprite.create_gargoyle:
                        if sprite.facing_right: offset = 160
                        else: offset = -40
                        self.enemy_sprites.add(pygame.sprite.Group(
                            Enemy(tile_size, sprite.rect.x + offset, sprite.rect.y + 70, 'graphics/enemy/gargoyle', '5',
                                  self.display_surface)))
                        sprite.create_gargoyle = False

                    if relative_distance > 40:
                        sprite.facing_right = False
                        if sprite.speed > 0 and sprite.generic_delay > 120: sprite.reverse()
                        if sprite.speed < 0 and abs(relative_distance) < 80: sprite.reverse()
                    if relative_distance < -40:
                        sprite.facing_right = True
                        if sprite.speed < 0 and sprite.generic_delay > 120: sprite.reverse()
                        if sprite.speed > 0 and abs(relative_distance) < 80: sprite.reverse()

                    if abs(relative_height) < 180 or abs(relative_distance) > self.enemy_range:
                        sprite.enemy_idle = False
                        if abs(relative_distance) < 120:
                            sprite.attack = True
                        else:
                            sprite.attack = False
                    else:
                        sprite.enemy_idle = True
                else:
                    sprite.enemy_idle = True
                    enemy_centerx = sprite.collision_rect.centerx
                    relative_distance = enemy_centerx - player.collision_rect.centerx
                    if abs(relative_distance) < 400:
                        if not self.center: self.text_loader.reset_text()
                        self.center = True
                        self.text_loader.run(self.display_surface, sprite.rect.x, sprite.rect.y, 3)
                        if self.text_loader.text_over:
                            sprite.speak = False
                            self.center = False
                            self.level_sound.stop()
                            self.boss_sound.play()

    def check_attack_collision(self):
        player = self.player.sprite
        collidable_sprites = self.enemy_sprites.sprites()+ self.boss_sprites.sprites()

        if player.attack_frame:
            for sprite in collidable_sprites:
                enemy_centerx = sprite.rect.centerx
                if sprite.collision_rect.colliderect(player.attack_rect) and sprite.impact == 0:
                        sprite.life -= 10
                        sprite.invincible = True
                        self.hit_sound.play()
                        if enemy_centerx > player.collision_rect.centerx:
                            sprite.impact = 16
                        else:
                            sprite.impact = -16

                        if sprite.life <= 0:
                            self.stomp_sound.play()
                            explosion_sprite = ParticleEffect(sprite.rect.center, 'explosion')
                            self.explosion_sprites.add(explosion_sprite)
                            sprite.kill()
                            self.gen_heart(sprite.rect.centerx,sprite.rect.centery)

        if player.rock_moving:
            for sprite in collidable_sprites:
                enemy_centerx = sprite.collision_rect.centerx
                if sprite.collision_rect.colliderect(player.rock_rect) and sprite.impact == 0:
                    if abs(player.v_x) + abs(player.v_y) > 10:
                        sprite.life -= 10
                        sprite.invincible = True
                        self.hit_sound.play()
                        if enemy_centerx > player.rock_rect.centerx:
                            sprite.impact = 16
                        else:
                            sprite.impact = -16

                        if sprite.life <= 0:
                            self.stomp_sound.play()
                            explosion_sprite = ParticleEffect(sprite.rect.center, 'explosion')
                            self.explosion_sprites.add(explosion_sprite)
                            sprite.kill()
                            self.gen_heart(sprite.rect.centerx, sprite.rect.centery)

    def get_player_mod(self):
        if self.cur_health <= 0:
            self.player.sprite.player_mode = 'death'
        else:
            if self.player_push:
                self.player.sprite.player_mode = 'push'
            elif self.center:
                self.player.sprite.player_mode = 'wait'
            else:
                self.player.sprite.player_mode = 'Null'

    def player_climb(self):
        player = self.player.sprite
        player.on_climb = False

        if player.up_down:

            collidable_sprites = self.ladder_sprites.sprites()
            keys = pygame.key.get_pressed()
            player.ladder_rect = pygame.Rect((player.collision_rect.left, player.collision_rect.top ),(player.collision_rect.width, 55))
            for ladder in collidable_sprites:
                ladder_bottom = ladder.rect.bottom
                ladder.rect.width = 40
                #enable to see the collision retangles
                #pygame.draw.rect(self.display_surface, 'red', pygame.Rect(ladder.rect), 2)
                #pygame.draw.rect(self.display_surface, 'yellow', pygame.Rect(player.ladder_rect), 2)
                #up
                if ladder.rect.colliderect(player.collision_rect):
                    player.on_climb = True
                    player.direction.y = 0
                    if keys[pygame.K_UP] :
                        player.collision_rect.y -= 1
                        player.frame_index += player.animation_speed
                #down
                if ladder.rect.colliderect(player.ladder_rect):
                    if keys[pygame.K_DOWN] and player.collision_rect.bottom <= ladder_bottom:
                        player.collision_rect.y += 2
                        player.frame_index += player.animation_speed
                        player.on_climb = True
                        player.direction.y = 0


        if not player.on_climb:
            player.up_down = False

    def open_door(self):
        #def
        keys = pygame.key.get_pressed()
        player = self.player.sprite
        doors = self.door_sprites.sprites()
        if keys[pygame.K_UP] and player.on_ground and player.up_down:
            for door in doors:
                #pygame.draw.rect(self.display_surface, 'white', pygame.Rect(door.rect), 2)
                if door.rect.colliderect(player.collision_rect):
                    door.open = True
                    self.door_sound.play()
                    player.frame_index = 0
                    player.status = 'in'
                    self.fade_out = True

                    # dor mapping
                    if self.current_level == 0:
                        if door.door_type == '0': self.door_level = 11
                        if door.door_type == '1': self.door_level = 12
                        self.collect_ref = True
                    if self.current_level == 11 or self.current_level == 12:
                        self.door_level = 0

    def create_show_text(self):
        player = self.player.sprite
        npcs = self.npc_sprites.sprites()
        keys = pygame.key.get_pressed()
        npc_near = False
        for npc in npcs:
            relative_width = abs(npc.rect.centerx - player.collision_rect.centerx)
            relative_height = abs(npc.rect.centery - player.collision_rect.centery)
            if relative_width < 300 and relative_height < 100:
                npc_near = True
                #show icon
                if len(self.up_icon_sprites) < 1:
                    up_icon_sprite = ParticleEffect((80,screen_height_play - 50), 'button_up')
                    self.up_icon_sprites.add(up_icon_sprite)
                #wait input up
                if keys[pygame.K_UP] and not self.text_loader.show_text and not self.text_loader.text_over:
                    self.text_loader.show_text = True
                    self.text_loader.reset_text()

                #text_line
                if self.text_loader.show_text:
                    if npc.npc_type == '0':
                        self.text_loader.run(self.display_surface, npc.rect.x, npc.rect.y, 0)
                    if npc.npc_type == '1':
                        self.text_loader.run(self.display_surface, npc.rect.x, npc.rect.y, 1)
                    if npc.npc_type == '2':
                        self.text_loader.run(self.display_surface, npc.rect.x, npc.rect.y, 2)

        #verify if any npc is near
        if not npc_near:
            self.text_loader.show_text = False
            self.text_loader.text_over = False

    def reset_coins_pos(self):
        self.coins_sprites.update(self.level_pos, self.level_posy)

    def gen_heart(self, x, y):
        part = randint(1, 30)
        if part == 1:
            self.heart_sprites.add(self.create_heart_group(x, y, 0))
        if part == 2:
            self.heart_sprites.add(self.create_heart_group(x, y, 1))

    def run(self):
        if self.center: self.centralize()
        level_data = levels[self.current_level]
        #background
        self.sky.draw(self.display_surface, self.world_shifty)
        self.clouds.draw(self.display_surface, self.world_shift, self.world_shifty)
        self.bg_palms_sprites.update(self.world_shift, self.world_shifty)
        self.bg_palms_sprites.draw(self.display_surface)
        # dust particles
        self.dust_sprite.update(self.world_shift, self.world_shifty)
        self.dust_sprite.draw(self.display_surface)
        #tilesets
        self.terrain_bg_sprites.update(self.world_shift, self.world_shifty)
        self.terrain_bg_sprites.draw(self.display_surface)

        self.masonry_sprites.update(self.world_shift, self.world_shifty)
        self.masonry_sprites.draw(self.display_surface)

        self.masonry_collide_sprites.update(self.world_shift, self.world_shifty)

        self.door_sprites.update(self.world_shift, self.world_shifty)
        self.door_sprites.draw(self.display_surface)

        self.terrain_sprites.update(self.world_shift, self.world_shifty)
        self.terrain_sprites.draw(self.display_surface)

        self.terrain_masonry_sprites.update(self.world_shift, self.world_shifty)
        self.terrain_masonry_sprites.draw(self.display_surface)

        self.decoration_masonry_sprites.update(self.world_shift, self.world_shifty)
        self.decoration_masonry_sprites.draw(self.display_surface)

        self.village_sprites.update(self.world_shift, self.world_shifty)
        self.village_sprites.draw(self.display_surface)

        #grass
        self.grass_sprites.update(self.world_shift, self.world_shifty)
        self.grass_sprites.draw(self.display_surface)
        #ladder
        self.ladder_sprites.update(self.world_shift, self.world_shifty)
        self.ladder_sprites.draw(self.display_surface)
        #enemy
        self.enemy_status()
        self.enemy_sprites.draw(self.display_surface)
        self.enemy_sprites.update(self.world_shift, self.world_shifty)
        self.boss_sprites.draw(self.display_surface)
        self.boss_sprites.update(self.world_shift, self.world_shifty)

        #fx
        self.explosion_sprites.update(self.world_shift, self.world_shifty)
        self.explosion_sprites.draw(self.display_surface)
        self.constraint_sprites.update(self.world_shift, self.world_shifty)
        #scenery
        self.crates_sprites.update(self.world_shift, self.world_shifty)
        self.crates_sprites.draw(self.display_surface)
        #coins
        self.coins_sprites.update(self.world_shift, self.world_shifty)
        self.coins_sprites.draw(self.display_surface)
        #hearts
        self.heart_sprites.update(self.world_shift, self.world_shifty)
        self.heart_sprites.draw(self.display_surface)
        #npc
        self.npc_sprites.update(self.world_shift, self.world_shifty)
        self.npc_sprites.draw(self.display_surface)
        self.create_show_text()
        #palms
        self.fg_palms_sprites.update(self.world_shift, self.world_shifty)
        self.fg_palms_sprites.draw(self.display_surface)

        self.goal.update(self.world_shift, self.world_shifty)
        self.goal.draw(self.display_surface)

        #player
        self.player.draw(self.display_surface)
        self.player.update()
        self.open_door()
        self.player_climb()
        self.get_player_on_ground()
        self.enemy_collision_reverse()
        if self.cur_health > 0: self.horizontal_movement_collision()
        self.vertical_movement_collision()
        self.vertical_object_collision()
        self.create_landing_dust()
        self.check_attack_collision()
        self.rock_collisions()
        #fx
        self.heart_fx_sprites.update(self.world_shift, self.world_shifty)
        self.heart_fx_sprites.draw(self.display_surface)
        #water
        if self.current_level ==0:
            self.water.draw(self.display_surface, self.world_shift, self.world_shifty)
            self.splash_sprites.update(self.world_shift, self.world_shifty)
            self.splash_sprites.draw(self.display_surface)
        #rain
        self.rain_sprites.update(self.world_shift, self.world_shifty)
        self.rain_sprites.draw(self.display_surface)
        #ui icon
        self.up_icon_sprites.update(0,0)
        self.up_icon_sprites.draw(self.display_surface)

        #world_movement
        self.scroll_x()
        self.scroll_y()

        self.check_death()
        self.get_player_mod()
        if self.cur_health > 0:
            self.check_win()
            self.check_coin_collisions()
            self.check_enemy_collisions()
            self.check_heart_collisions()

        self.input()
