import random
import pygame


class Button:
    def __init__(self, parent):
        self.parent = parent
        self.color = (40,40,40)
        self.old_color = self.color
        self.color_f = (250,250,250)
        self.screen = parent.screen
        self.text = 'Text'
        self.active = True
        self.indexs = None
        self.border, self.img = None, None
        self.func = lambda args: print("click")
        self.text_render = self.parent.font.render(self.text, False, self.color_f)

    def set_indexs(self, indexs):
        self.indexs = indexs

    def set_func(self, func):
        self.func = func

    def set_color(self, color):
        self.color = color
        self.old_color = self.color

    def set_color_f(self, color_f):
        self.color_f = color_f
        if self.color_f:
            self.text_render = self.parent.font.render(self.text, False, self.color_f)

    def set_border(self, border):
        self.border = border

    def set_text(self, text):
        self.text = text
        self.text_render = self.parent.font.render(self.text, False, self.color_f)

    def set_pos(self, x, y, w, h):
        self.x, self.y, self.w, self.h = x, y, w, h

    def collision(self, mouse):
        return self.x <= mouse[0] <= self.x + self.w and self.y <= mouse[1] <= self.y + self.h

    def update(self, mouse):
        if self.color:
            if self.collision(mouse):
                self.color = tuple(a-10 if a-10>0 else 0 for a in self.old_color)
            else:
                self.color = self.old_color

    def set_img(self, img):
        self.img = img

    def set_active(self, active):
        self.active = active

    def click(self, mouse):
        if self.collision(mouse) and self.active:
            self.func(self)

    def draw(self):
        self.rect = pygame.Rect(self.x, self.y, self.w, self.h)
        if self.color:
            if self.border:
                pygame.draw.rect(self.screen, self.color, self.rect, width=self.border)
            else:
                pygame.draw.rect(self.screen, self.color, self.rect)
        text_rect = self.text_render.get_rect(center=(self.x + self.w // 2, self.y + self.h // 2))
        if self.color_f:
            self.screen.blit(self.text_render, text_rect)
        if self.img:
            self.screen.blit(self.img, self.rect)


class Player:
    columns, rows = 5, [5, 6, 6, 6, 4]

    def __init__(self, game, num, is_moving=False, name=""):
        self.game, self.pos, self.screen = game, None, game.screen
        self.name = name
        self.back = pygame.image.load("PlayField.png")
        self.font = self.game.font
        self.rows_points = [
            [6, 4],
            [9, 5],
            [7, 3],
            [8, 4],
            [3, 2],
        ]
        self.score = 0
        y = game.size[1] - 80
        self.is_playing, self.current_button = False, None
        self.back = pygame.transform.scale(self.back, (self.back.get_width() * (y / self.back.get_height()), y))
        if num == 2:
            self.color = (222, 0, 0)
        else:
            self.color = (0, 222, 0)
        self.list_buttons = []
        self.is_moving = is_moving
        self.texts_scores = []
        self.text = self.font.render(f'Игрок {num}', False, self.color)
        self.button_play = Button(self)
        self.button_play.set_func(self.play)
        self.button_play.set_text("Нарисовать")

    def play(self, args):
        if self.current_button:
            i, j = self.current_button.indexs
            if not self.list_buttons[i][j][1]:
                self.is_playing = True
                img = self.game.get_img()
                self.current_button.set_img(img[0])
                self.score += img[1]
                self.list_buttons[i][j][1] = self.game.rand
                check = True
                house = False
                for b in range(self.rows[i]):
                    if not self.list_buttons[i][b][1]:
                        check = False
                    if self.list_buttons[i][b][1] == 1:
                        house = True
                if check:
                    if house:
                        sc = self.rows_points[i][0]
                    else:
                        sc = self.rows_points[i][1]
                    self.score += sc
                    self.texts_scores.append([self.font.render(f'{sc}', False, self.color), (62*i+73+self.pos[0], self.pos[1]+10)])

                self.buttons_zeroing()

    def zero(self):
        self.is_playing = False
        self.current_button = None

    def restart(self):
        print("sd")
        self.score = 0
        self.is_moving = False
        self.is_playing, self.current_button = False, None
        self.texts_scores = []
        self.generate_cells()

    def buttons_zeroing(self):
        for i in range(self.columns):
            for j in range(self.rows[i]):
                self.list_buttons[i][j][0].set_color(None)
                self.list_buttons[i][j][0].set_color_f(None)

    def select(self, button):
        if self.is_moving and not self.is_playing:
            self.buttons_zeroing()
            self.current_button = button
            button.set_color(self.color), button.set_color_f(None)

    def generate_cells(self):
        self.list_buttons = []
        w, h = 62,55
        for i in range(self.columns):
            line_buttons = []

            for j in range(self.rows[i]):
                b = Button(self)
                b.set_pos(w*i+42+self.pos[0], h*j+90+self.pos[1]-(0 if i % 2 else h//2)+(h if i == 0 else 0)+(h*2 if i == self.columns-1 else 0), w, h)
                b.set_color(None)
                b.set_color_f(None)
                b.set_func(lambda d: self.select(d))
                b.set_border(2)
                b.set_indexs([i, j])
                arg = 0
                if [i, j] in [[0, 1], [2, 3], [4, 2]]:
                    arg = -1
                line_buttons.append([b, arg])
            self.list_buttons.append(line_buttons)

    def set_pos(self, *args):
        self.pos = args
        self.button_play.set_pos(self.pos[0] + 150, 10, 180, 50)
        self.generate_cells()

    def check_full(self):
        check = 0
        for i in range(self.columns):
            r = True
            for j in range(self.rows[i]):
                if not self.list_buttons[i][j][1]:
                    r = False
            if r:
                check += 1
        return True if check >= 3 else False

    def update(self):
        self.button_play.update(self.game.mouse)
        for i in range(self.columns):
            for j in range(self.rows[i]):
                self.list_buttons[i][j][0].update(self.game.mouse)

    def draw(self):
        self.screen.blit(self.text, (self.pos[0]+5, 10))
        self.screen.blit(self.back, self.pos)
        self.button_play.draw()
        if self.is_moving:
            self.rect = pygame.Rect(self.pos[0], 10, 140, 50)
            pygame.draw.rect(self.screen, self.color, self.rect, width=3)
        for i in range(self.columns):
            for j in range(self.rows[i]):
                self.list_buttons[i][j][0].draw()
        for i in self.texts_scores:
            text_rect = i[0].get_rect(center=i[1])
            self.screen.blit(i[0], text_rect)

    def click(self):
        self.button_play.click(self.game.mouse)
        for i in range(self.columns):
            for j in range(self.rows[i]):
                self.list_buttons[i][j][0].click(self.game.mouse)


class App:
    def __init__(self):
        pygame.init(), pygame.font.init()
        self.size = 1200, 800
        self.screen = pygame.display.set_mode(self.size)
        self.img = [
            [pygame.image.load("house.png"), 1],
            [pygame.image.load("tangle.png"), 1],
            [pygame.image.load("butterfly.png"), 1],
            [pygame.image.load("dish.png"), 1],
            [pygame.image.load("pillow.png"), 1],
            [pygame.image.load("mouse.png"), 1]
        ]
        self.mouse = None
        self.font = pygame.font.SysFont('Comic Sans MS', 30)
        self.font2 = pygame.font.SysFont('Comic Sans MS', 45)
        self.player1, self.player2 = Player(self, 1, name="зеленый"), Player(self, 2, name="красный")
        self.player1.set_pos(15, 65), self.player2.set_pos(self.size[0] - self.player2.back.get_width() - 15, 65)
        self.running = True
        self.queue = 0
        self.rand = 0
        self.draw = self.draw1_func
        self.button_motion = Button(self)
        self.button_motion.set_text('Бросить кубики')
        self.button_motion.set_pos(self.size[0] / 2 - 125, 200, 250, 90)
        self.button_motion.set_func(self.moving)
        self.button_restart = Button(self)
        self.button_restart.set_text('Играть снова')
        self.button_restart.set_pos(self.size[0] / 2 - 125, 200, 250, 90)
        self.button_restart.set_func(self.restart)
        self.button_restart.set_active(False)
        self.text = self.font.render(f'Бросьте кубики!', False, (200,150,200))
        self.text_arrow = self.font2.render(f'--', False, (80,80,80))
        self.update()

    def restart(self, args):
        self.draw = self.draw1_func
        self.player1.restart()
        self.player2.restart()
        self.queue = 0
        self.rand = 0
        self.button_motion.set_active(True)
        self.button_restart.set_active(False)
        self.text = self.font.render(f'Бросьте кубики!', False, (200, 150, 200))
        self.text_arrow = self.font2.render(f'--', False, (80, 80, 80))

    def moving(self, args):
        if self.queue == 2:
            if self.player2.is_playing:
                self.queue = 1
                self.rand = random.randrange(1, 7)
                self.text_arrow = self.font2.render(f'<--', False, self.player1.color)
                self.player1.is_moving, self.player2.is_moving = True, False
                self.player2.zero()
        elif self.queue == 1:
            if self.player1.is_playing:
                self.queue = 2
                self.rand = random.randrange(1, 7)
                self.text_arrow = self.font2.render(f'-->', False, self.player2.color)
                self.player1.is_moving, self.player2.is_moving = False, True
                self.player1.zero()
        else:
            self.queue = 1
            self.rand = random.randrange(1, 7)
            self.text_arrow = self.font2.render(f'<--', False, self.player1.color)
            self.player1.is_moving, self.player2.is_moving = True, False
        self.text = self.font.render(f'Выпало {self.rand}', False, (200, 150, 200))

    def get_img(self):
        return self.img[self.rand-1]

    def update(self):
        while self.running:
            self.screen.fill((0, 0, 0))
            self.mouse = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    break
                if event.type == pygame.KEYDOWN:
                    ...
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.player1.click(), self.player2.click(), self.button_motion.click(self.mouse), self.button_restart.click(self.mouse)
            self.update_()
            self.draw()
            pygame.display.flip()
        pygame.quit()

    def update_(self):
        self.player1.update()
        self.player2.update()
        self.button_motion.update(self.mouse)
        # Если все ячейки заполнены
        if self.player1.check_full() or self.player2.check_full():
            self.button_restart.set_active(True)
            self.button_motion.set_active(False)
            self.draw = self.draw2_func

    def draw1_func(self):
        self.player1.draw()
        self.player2.draw()
        self.button_motion.draw()
        t_r = self.text.get_rect(center=(self.size[0] / 2, 400))
        self.screen.blit(self.text, t_r)
        t_r2 = self.text_arrow.get_rect(center=(self.size[0] / 2, 40))
        self.screen.blit(self.text_arrow, t_r2)

    def get_winner(self):
        if self.player1.score == self.player2.score:
            return ["Ничья!", self.player1.score]
        elif self.player1.score > self.player2.score:
            return [self.player1.name, self.player1.score]
        else:
            return [self.player2.name, self.player2.score]

    def draw2_func(self):
        self.player1.draw()
        self.player2.draw()
        self.button_restart.draw()
        winner = self.get_winner()
        if winner[0] == "Ничья!":
            text_winner = self.font.render(winner[0], False, (200, 150, 200))
        else:
            text_winner = self.font.render(f'Победил {winner[0]}!', False, (200, 150, 200))
        text_score = self.font.render(f'Со счетом {winner[1]}', False, (200, 150, 200))
        t_r = self.text.get_rect(center=(self.size[0] / 2-50, 400))
        self.screen.blit(text_winner, t_r)
        t_r = self.text.get_rect(center=(self.size[0] / 2-50, 450))
        self.screen.blit(text_score, t_r)
        t_r2 = self.text_arrow.get_rect(center=(self.size[0] / 2, 40))
        self.screen.blit(self.text_arrow, t_r2)


if __name__ == '__main__':
    app = App()
