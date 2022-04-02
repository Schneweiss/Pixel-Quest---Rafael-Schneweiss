import pygame.image
from game_data import text_path, font_path

class TextLoader(pygame.sprite.Sprite):
    def __init__(self):
        self.board = pygame.image.load('graphics/ui/board.png').convert_alpha()
        # 26 strings
        self.limit = 26
        self.pos_x = self.board.get_width() -80
        self.pos_y = self.board.get_height()-140
        self.font = pygame.font.Font(font_path, 25)
        self.extract_text()
        self.i = 0
        self.w = 0
        self.line = 0
        self.text = ['','','','','','','','','','']
        self.show_text = False
        self.text_over = False


        #audio
        self.text_sound = pygame.mixer.Sound('audio/effects/text.mp3')

    def extract_text(self):
        path = text_path
        self.speaks = []
        with open(path, 'r') as file:
            self.speaks = file.readlines()

    def reset_text(self):
        self.line = 0
        self.i = 0
        self.w = 0
        self.text = ['', '', '', '', '', '']

    def run(self, surface, x, y, line):
        keys = pygame.key.get_pressed()
        #blit board
        surface.blit(self.board, (x -self.pos_x,y-self.pos_y))
        #extract strings
        speak = self.speaks[line].split()

        if self.w < len(speak):
            if self.i > len(speak[self.w]) -1:
                self.i = -1
                self.text[self.line] += ' '
                self.w += 1
                if self.w < len(speak):
                    if len(self.text[self.line]) + len(speak[self.w]) - 1 > self.limit:
                        self.line += 1
                        self.i = -1
                self.text_sound.play()
            else:
                self.text[self.line] += speak[self.w][self.i]

        else:
            if keys[pygame.K_UP]:
                self.text_over = True
                self.show_text = False
                self.reset_text()

        if self.line > 4 and keys[pygame.K_UP]:
            self.line = 0
            self.text = ['', '', '', '', '', '', '', '', '', '']

        if self.line <= 4:
            self.i += 1

        #define and blit
        text_1 = self.font.render(str(self.text[0]), False, '#33323d')
        text_1_rect = text_1.get_rect(midleft=(x - 405, y - 215))
        text_2 = self.font.render(str(self.text[1]), False, '#33323d')
        text_2_rect = text_2.get_rect(midleft=(x - 405, y - 185))
        text_3 = self.font.render(str(self.text[2]), False, '#33323d')
        text_3_rect = text_3.get_rect(midleft=(x - 405, y - 155))
        text_4 = self.font.render(str(self.text[3]), False, '#33323d')
        text_4_rect = text_4.get_rect(midleft=(x - 405, y - 125))
        text_5 = self.font.render(str(self.text[4]), False, '#33323d')
        text_5_rect = text_5.get_rect(midleft=(x - 405, y - 95))


        surface.blit(text_1, text_1_rect)
        surface.blit(text_2, text_2_rect)
        surface.blit(text_3, text_3_rect)
        surface.blit(text_4, text_4_rect)
        surface.blit(text_5, text_5_rect)
