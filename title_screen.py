import pygame
from support import import_folder

class Node(pygame.sprite.Sprite):
    def __init__(self, pos, path):
        super().__init__()
        self.frames = import_folder(path)
        self.frame_index = 0
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect(center=pos)


    def animate(self):
        # loop over frame index
        self.frame_index += 0.15
        if self.frame_index >= len(self.frames):
            self.frame_index = 0
        self.image = self.frames[int(self.frame_index)]

    def update(self):
        self.animate()


class TitleScreen():
    def __init__(self, surface, init_game):

        self.init_game = init_game
        #setup
        self.display_surface = surface
        #movemente logic
        self.move_direction = pygame.math.Vector2(0,0)
        self.speed = 8
        self.moving = False
        #sprites
        self.setup_nodes()

        #time
        self.start_time = pygame.time.get_ticks()
        self.allow_input = False
        self.timer_lenght = 500

    def setup_nodes(self):
        self.nodes = pygame.sprite.Group()
        node_sprite = Node((600, 200), 'graphics/title_screen/0/')
        self.nodes.add(node_sprite)
        node_sprite = Node((600, 350), 'graphics/title_screen/1/')
        self.nodes.add(node_sprite)
        node_sprite = Node((600, 600), 'graphics/title_screen/3/')
        self.nodes.add(node_sprite)
        node_sprite = Node((600, 500), 'graphics/title_screen/2/')
        self.nodes.add(node_sprite)


    def input(self):
        if self.allow_input:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_SPACE] or keys[pygame.K_RETURN]:
                self.init_game(0,0)

    def input_timer(self):
        if not self.allow_input:
            current_time = pygame.time.get_ticks()
            if current_time - self.start_time >= self.timer_lenght:
                self.allow_input = True

    def run(self):
        self.input_timer()
        self.input()
        self.nodes.update()
        self.nodes.draw(self.display_surface)
