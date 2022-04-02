import pygame
from game_data import font_path

class UI:
    def __init__(self, surface):
        # setup
        self.display_surface = surface

        # health
        self.health_bar = pygame.image.load('graphics/ui/health_bar.png').convert_alpha()
        self.health_bar_topleft = (54, 39)
        self.bar_max_width = 152
        self.bar_height = 4
        # stamina
        self.stamina_bar = pygame.image.load('graphics/ui/mini.png').convert_alpha()
        self.stamina_bar_topleft = (61, 64)
        self.stamina_bar_max_width = 97
        self.stamina_bar_height = 2


        # coins
        self.coin = pygame.image.load('graphics/ui/coin.png').convert_alpha()
        self.coin_rect = self.coin.get_rect(topleft = (21, 75))
        self.font = pygame.font.Font(font_path, 30)


    def show_health(self, current, full):
        self.display_surface.blit(self.health_bar, (20, 10))
        current_health_ratio = current / full
        current_bar_width = self.bar_max_width * current_health_ratio
        health_bar_rect = pygame.Rect((self.health_bar_topleft),(current_bar_width,self.bar_height))
        pygame.draw.rect(self.display_surface,'#dc4949',health_bar_rect)

    def show_stamina(self, current, full):
        self.display_surface.blit(self.stamina_bar, (55, 50))
        current_stamina_ratio = current / full
        stamina_bar_width = self.stamina_bar_max_width * current_stamina_ratio
        stamina_bar_rect = pygame.Rect((self.stamina_bar_topleft), (stamina_bar_width, self.stamina_bar_height))
        if current < 20: color =  (160,160,160)
        else: color =  (220,220,220)
        pygame.draw.rect(self.display_surface, color, stamina_bar_rect)

    def show_coins(self, amount):
        self.display_surface.blit(self.coin, self.coin_rect)
        coin_amount_surf = self.font.render(str(amount), False, '#33323d')
        coin_amount_rect = coin_amount_surf.get_rect(midleft = (self.coin_rect.right + 5, self.coin_rect.centery))
        self.display_surface.blit(coin_amount_surf, coin_amount_rect)

