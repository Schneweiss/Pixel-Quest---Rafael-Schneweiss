import pygame, sys
from settings import *
from level import Level
from overworld import Overworld
from title_screen import TitleScreen
from ui import UI
from game_data import levels, sound_level
from support import import_csv_layout
from tiles import Coin
from enemy import Enemy
from random import randint


class Game:
    def __init__(self):

        #game atributes
        self.max_level = 0
        self.max_health = 100
        self.cur_health = 100
        self.cur_coins = 0
        self.coins = 0
        self.death_delay = 0
        self.max_stamina = 100
        self.cur_stamina = 100
        self.death_delay = 0
        self.fade_time = 0
        self.alpha_level = 0

        #load coins
        self.coins_sprites = []
        self.load_world_coins()
        # load bosses
        self.boss_sprites = []
        self.load_bosses()

        #audio
        self.level_bg_music = pygame.mixer.Sound(sound_level[0])
        self.overworld_bg_music = pygame.mixer.Sound('audio/overworld_music.mp3')
        self.overworld_bg_music.set_volume(1)
        self.game_over_sound = pygame.mixer.Sound('audio/effects/game_over.mp3')
        self.title_screen_sound = pygame.mixer.Sound('audio/title_screen.mp3')
        self.title_screen_sound.set_volume(1)
        self.thunder_sound = pygame.mixer.Sound('audio/effects/thunder.mp3')
        self.thunder_sound.set_volume(0.5)

        #title_screen creation
        self.create_title_screen(screen)
        self.status = 'tittle_screen'

        #user interface
        self.ui = UI(screen)

    def create_level(self, current_level, player_ref):
        self.level = Level(current_level, screen, self.create_overworld, self.change_coins, self.change_health, self.cur_health, self.change_stamina, self.coins_sprites, player_ref, self.boss_sprites)
        self.status = 'level'
        self.cur_stamina = 100
        self.level_bg_music.stop()
        self.overworld_bg_music.stop()
        self.level_bg_music = pygame.mixer.Sound(sound_level[current_level])
        if current_level !=0: self.level_bg_music.play(loops=-1)
        self.level_bg_music.set_volume(1)

    def create_overworld(self, current_level, new_max_level):
        if new_max_level > self.max_level:
            self.max_level = new_max_level
        self.overworld = Overworld(current_level, self.max_level, screen, self.create_level)
        self.status = 'overworld'
        pygame.mixer.stop()
        self.overworld_bg_music.play(loops=-1)
        self.level.reset_coins_pos()

    def init_game(self, current_level, new_max_level):
        if new_max_level > self.max_level:
            self.max_level = new_max_level
        self.overworld = Overworld(current_level, self.max_level, screen, self.create_level)
        self.status = 'overworld'
        self.title_screen_sound.stop()
        self.overworld_bg_music.play(loops=-1)

    def create_title_screen(self, screen):
        self.title_screen = TitleScreen(screen, self.init_game)
        self.status = "title_screen"
        self.level_bg_music.stop()
        self.overworld_bg_music.stop()
        self.title_screen_sound.play(loops=-1)

    def load_world_coins(self):
        for current_level in levels:
            level_data = levels[current_level]
            coins_layout = import_csv_layout(level_data['coins'])
            sprite_group = pygame.sprite.Group()

            for row_index, row in enumerate(coins_layout):
                for col_index, val in enumerate(row):
                    if val != '-1':
                        x = col_index * tile_size
                        y = row_index * tile_size - level_offset
                        if val == '0': sprite = Coin(tile_size, x, y, 'graphics/coins/gold', 5)
                        if val == '1': sprite = Coin(tile_size, x, y, 'graphics/coins/silver', 1)

                        sprite_group.add(sprite)

            self.coins_sprites.append(sprite_group)

    def load_bosses(self):
        for current_level in levels:
            level_data = levels[current_level]
            bosses_layout = import_csv_layout(level_data['enemies'])
            sprite_group = pygame.sprite.Group()

            for row_index, row in enumerate(bosses_layout):
                for col_index, val in enumerate(row):
                    if val != '-1':
                        x = col_index * tile_size
                        y = row_index * tile_size - level_offset
                        if val == '4':
                            sprite = Enemy(tile_size, x, y, 'graphics/enemy/boss_0/run', val, screen)
                            sprite_group.add(sprite)

            self.boss_sprites.append(sprite_group)

    def check_game_over(self):
        if self.cur_health <= 0:
            #game over snd + fade out
            self.level_bg_music.stop()
            fade = pygame.Surface((screen_width, screen_height))
            fade.fill('black')
            fade.set_alpha( self.death_delay*10)
            screen.blit(fade,(0,0))
            if self.death_delay == 0:
                pygame.mixer.stop()
                self.game_over_sound.play()
            self.death_delay += 0.1

            if self.death_delay >= 25:
                self.cur_health = 100
                self.coins = 0
                self.max_level = 0
                self.overworld = Overworld(0, self.max_level, screen, self.create_level)
                self.status = 'overworld'
                self.overworld_bg_music.play(loops=-1)
                self.level.reset_coins_pos()
        else:
            self.death_delay = 0

    def create_transition(self):
        fade = pygame.Surface((screen_width, screen_height))
        fade.fill('black')
        fade.set_alpha(self.fade_time)
        screen.blit(fade, (0, 0))
        if self.fade_time < 255:
            self.fade_time += 4
        else:
            self.level.fade_out = False
            self.fade_time = 0
            if self.level.collect_ref: self.player_ref = [-self.level.level_pos, -self.level.level_posy, self.level.level_pos, self.level.level_posy,
                                                          self.level.player.sprite.collision_rect.x -self.level.player_init_x, self.level.player.sprite.collision_rect.y-self.level.player_init_y]
            self.level.reset_coins_pos()
            self.create_level(self.level.door_level, self.player_ref)
            self.overworld_bg_music.stop()

    def create_night(self):
        if self.level.night:
            fade = pygame.Surface((screen_width, screen_height))
            fade.fill((0,0,30))
            fade.set_alpha(self.alpha_level)
            if self.level.rain:
                t = randint(0, 400)
                if t == 1:
                    self.alpha_level = 0
                    self.thunder_sound.play()
            if self.alpha_level< 100: self.alpha_level += 5
            screen.blit(fade, (0,0))

    def change_coins(self, amount):
        self.coins += amount

    def change_health(self, amount):
        self.cur_health += amount
        self.level.cur_health += amount
        if self.cur_health > self.max_health: self.cur_health = self.max_health

    def change_stamina(self, amount):
        self.cur_stamina += amount

    def run(self):
        if self.status == 'overworld':
            self.overworld.run()
        elif self.status == 'tittle_screen':
            self.title_screen.run()
        else:
            self.level.run()
            self.create_night()
            self.ui.show_health(self.cur_health,  self.max_health)
            self.ui.show_stamina(self.cur_stamina, self.max_stamina)
            self.ui.show_coins(self.coins)
            self.check_game_over()
            if self.level.fade_out: self.create_transition()

#Setup
pygame.init()
screen = pygame.display.set_mode((screen_width, screen_height_play))
pygame.display.set_caption('PixelQuest')
clock = pygame.time.Clock()
game = Game()



while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    screen.fill((20,20,20))
    game.run()


    pygame.display.update()
    clock.tick(60)