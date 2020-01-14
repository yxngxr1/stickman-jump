import pygame as pg
import random
from threading import Thread
from components import *
from settings import *
from sprites import *


class Game:
    def __init__(self):
        # Инициализировать игровое окно
        pg.mixer.pre_init(44100, -16, 1, 512)
        pg.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption(TITLE)
        self.font_name = pg.font.match_font(FONT)
        self.clock = pg.time.Clock()
        self.running = True
        self.sound_on_off = True
        self.music_on_off = True
        self.str_sound_on_off = "Выключить звуки"
        self.str_music_on_off = "Выключить музыку"
        self.load_data()

    def start(self):
        self.play_start_music()
        self.menu_screen()

    def play_start_music(self):
        self.last_music = random.choice(MUSIC_MENU)
        self.music_end = pg.USEREVENT+1
        pg.mixer.music.set_endevent(self.music_end)
        file = random.choice(MUSIC_MENU)
        while file == self.last_music:
            file = random.choice(MUSIC_MENU)
        pg.mixer.music.load(file)
        pg.mixer.music.set_volume(self.music_volume)
        pg.mixer.music.play(1)

    def play_game_music(self):
        self.last_music = random.choice(MUSIC_GAMEPLAY)
        self.music_end = pg.USEREVENT+2
        pg.mixer.music.set_endevent(self.music_end)
        file = random.choice(MUSIC_GAMEPLAY)
        while file == self.last_music:
            file = random.choice(MUSIC_GAMEPLAY)
        pg.mixer.music.load(file)
        pg.mixer.music.set_volume(self.music_volume)
        pg.mixer.music.play(1)

    def play_gameover_music(self):
        self.last_music = random.choice(MUSIC_GAMEOVER)
        self.music_end = pg.USEREVENT+3
        pg.mixer.music.set_endevent(self.music_end)
        file = random.choice(MUSIC_GAMEOVER)
        while file == self.last_music:
            file = random.choice(MUSIC_GAMEOVER)
        pg.mixer.music.load(file)
        pg.mixer.music.set_volume(self.music_volume)
        pg.mixer.music.play(1)

    def load_data(self):
        # загрузка рекорда
        with open(HIGHSCORE, 'r') as file:
            try:
                self.highscore = int(file.read())
            except:
                self.highscore = 0

            self.jump_sound = pg.mixer.Sound(SOUND_JUMP)
            self.death_sound = pg.mixer.Sound(SOUND_DEATH)
            self.hover_sound = pg.mixer.Sound(SOUND_BTN_HOVER)
            self.press_sound = pg.mixer.Sound(SOUND_BTN_PRESS)
            self.music_volume = MUSIC_VOLUME
            self.sound_volume = SOUND_VOLUME
            self.change_volume(SOUND_VOLUME, MUSIC_VOLUME)

    def change_volume(self, sound_volume, music_volume):
        self.jump_sound.set_volume(sound_volume[0])
        self.death_sound.set_volume(sound_volume[1])
        self.hover_sound.set_volume(sound_volume[2])
        self.press_sound.set_volume(sound_volume[3])
        pg.mixer.music.set_volume(music_volume)
        self.sound_volume = sound_volume
        self.music_volume = music_volume

    def new_game(self):
        # Начать новую игру
        self.score = 0
        self.death = False
        self.all_sprites = pg.sprite.Group()
        self.platforms = pg.sprite.Group()

        self.player = Player(self)
        self.all_sprites.add(self.player)

        for i in START_MAP:
            p = Platform(*i)
            self.all_sprites.add(p)
            self.platforms.add(p)

        self.run()

    def run(self):
        self.play_game_music()

        # Главный игровой цикл
        self.playing = True
        while self.playing:
            self.clock.tick(FPS)

            # обязательная проверка на сохранность игрового процесса
            if self.playing:
                self.events() # проверка событий

            if self.playing:
                self.update() # обновление всех событий в игре

            if self.playing:
                self.draw() # отрисовка игрового мира

        if self.running:
            pg.mixer.music.fadeout(FADE_OUT - 200 if FADE_OUT > 200 else 0)
            self.gameover_screen()

    def events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                if self.playing:
                    pg.mixer.music.stop()
                    self.playing = False
                self.running = False
                pg.mixer.music.stop()
                pg.quit()

            if event.type == self.music_end:
                self.play_game_music()

    def update(self):
        self.all_sprites.update()

        # поставить игрока на платформу при падении
        if self.player.vel.y > 0:
            hits = pg.sprite.spritecollide(self.player, self.platforms, False)
            if hits:
                if self.player.pos.y < hits[0].rect.bottom + hits[0].rect.height // 2:
                    self.player.pos.y = hits[0].rect.top
                    self.player.vel.y = 0
                    self.player.OnGround = True
            else:
                self.player.OnGround = False

        # смещение мира по отношению к игроку (камера)
        if self.player.pos.y <= WIDTH // 2:
            self.player.pos.y += abs(self.player.vel.y)
            for i in self.platforms:
                i.rect.y += abs(self.player.vel.y)
                # удаление платформ за экраном
                if i.rect.top >= HEIGHT:
                    i.kill()
            self.score += abs(int(self.player.vel.y))

        # добавление новых платформ
        while len(self.platforms) < 6:
            w = random.choice([40, 60, 80, 100])
            h = 20
            x = random.randrange(20, WIDTH - w - 20)
            y = -20
            p = Platform(x, y, w, h)
            self.platforms.add(p)
            self.all_sprites.add(p)

        # смерть игрока
        if self.player.rect.top > HEIGHT:
            if self.death == False:
                self.death = True
                self.death_sound.play()

            # если герой вышел за экран внизу,
            # то все предметы улетают наверх с его же скоростью
            for i in self.all_sprites:
                i.rect.y -= self.player.vel.y
                if i.rect.bottom < 0:
                    i.kill()

        if len(self.platforms) == 0:
             self.playing = False

    def draw(self):
        self.screen.blit(pg.image.load('images/background/bg.png'), (0, 0))
        self.all_sprites.draw(self.screen)
        self.draw_text(f'Набрано очков: {self.score}', 28, RED, WIDTH / 2, 15)
        pg.display.flip()

    def menu_screen(self):
        self.menu_screen_run = True
        self.screen.fill(LIGHTGREY)
        self.draw_text("Stickman Jump", 64, WHITE, WIDTH // 2, 20)
        self.draw_text("Рекорд: " + str(self.highscore), 24, WHITE, WIDTH // 2, 100)
        # кнопки
        self.btn_play = Button(self, "Играть", 48, BUTTON_SIZE, WHITE, RED, LIGHTBLUE, WIDTH // 2, HEIGHT // 3)
        self.btn_settings = Button(self, "Настройки", 48, BUTTON_SIZE, WHITE, RED, LIGHTBLUE, WIDTH // 2, HEIGHT // 3 + 100)
        self.btn_exit_menu = Button(self, "Выйти из игры", 48, BUTTON_SIZE, WHITE, RED, LIGHTBLUE, WIDTH // 2, HEIGHT // 3 + 200)
        self.draw_text("v.0.1", 24, WHITE, 40, HEIGHT - 40)

        buttons = [self.btn_play, self.btn_settings, self.btn_exit_menu]

        while self.menu_screen_run:
            button_pressed = self.wait_for_press(buttons, 'menu')

            if button_pressed == self.btn_play:
                self.menu_screen_run = False
                pg.mixer.music.fadeout(FADE_OUT)
                self.new_game()

            elif button_pressed == self.btn_settings:
                self.menu_screen_run = False
                self.settings_screen()

            elif button_pressed == self.btn_exit_menu:
                self.menu_screen_run = False
                self.running = False
                pg.mixer.music.stop()
                pg.quit()

            if self.running:
                pg.display.flip()

    def settings_screen(self):
        self.settings_screen_run = True
        self.screen.fill(LIGHTGREY)
        self.draw_text("Управление", 64, WHITE, WIDTH // 2, 20)
        self.draw_text("–> - вправо", 32, WHITE, WIDTH // 2, 110)
        self.draw_text("<– - влево", 32, WHITE, WIDTH // 2, 150)
        self.draw_text("Space - прыжок", 32, WHITE, WIDTH // 2, 190)
        # кнопки
        self.btn_sound_on_off = Button(self, self.str_sound_on_off, 36, BUTTON_SIZE, WHITE, RED, LIGHTBLUE, WIDTH // 2, HEIGHT // 3 + 100 - 40)
        self.btn_music_on_off = Button(self, self.str_music_on_off, 36, BUTTON_SIZE, WHITE, RED, LIGHTBLUE, WIDTH // 2, HEIGHT // 3 + 190 - 40)
        self.btn_reset = Button(self, "Сброс данных", 40, BUTTON_SIZE, WHITE, RED, LIGHTBLUE, WIDTH // 2, HEIGHT // 3 + 280 - 40)
        self.btn_menu = Button(self, "Назад", 48, (int(BUTTON_SIZE[0] // 1.5), BUTTON_SIZE[1]), WHITE, RED, LIGHTBLUE, WIDTH // 2, HEIGHT // 3 + 370 - 20)

        buttons = [self.btn_sound_on_off, self.btn_music_on_off, self.btn_reset, self.btn_menu]

        while self.settings_screen_run:
            button_pressed = self.wait_for_press(buttons, 'setting')

            if button_pressed == self.btn_sound_on_off:
                self.sound_on_off = True if not self.sound_on_off else False
                self.str_sound_on_off = "Включить звуки" if not self.sound_on_off else "Выключить звуки"
                self.change_volume([0, 0, 0, 0], self.music_volume) if not self.sound_on_off else self.change_volume(SOUND_VOLUME, self.music_volume)
                self.settings_screen()

            elif button_pressed == self.btn_music_on_off:
                self.music_on_off = True if not self.music_on_off else False
                self.str_music_on_off = "Включить музыку" if not self.music_on_off else "Выключить музыку"
                self.change_volume(self.sound_volume, 0) if not self.music_on_off else self.change_volume(self.sound_volume, MUSIC_VOLUME)
                self.settings_screen()


            elif button_pressed == self.btn_reset:
                self.highscore = 0
                with open(HIGHSCORE, 'w') as file:
                    file.write(str(0))

            elif button_pressed == self.btn_menu:
                self.settings_screen_run = False
                self.menu_screen()

            if self.running:
                pg.display.flip()

    def gameover_screen(self):
        self.gameover_screen_run = True
        self.play_gameover_music()
        self.screen.fill(LIGHTGREY)
        self.draw_text("GAME OVER", 82, RED, WIDTH // 2, 20)
        self.draw_text("Очков: " + str(self.score), 24, WHITE, WIDTH // 2, 120)

        self.btn_play_again = Button(self, "Играть заново", 48, BUTTON_SIZE, WHITE, RED, LIGHTBLUE, WIDTH // 2, HEIGHT // 3)
        self.btn_menu = Button(self, "Меню", 48, BUTTON_SIZE, WHITE, RED, LIGHTBLUE, WIDTH // 2, HEIGHT // 3 + 100)
        self.btn_exit_go = Button(self, "Выйти из игры", 48, BUTTON_SIZE, WHITE, RED, LIGHTBLUE, WIDTH // 2, HEIGHT // 3 + 200)

        if self.score > self.highscore:
            self.highscore = self.score
            self.draw_text('Ты побил рекорд, поздравляю!', 30, LIGHTBLUE, WIDTH // 2, 160)
            with open(HIGHSCORE, 'w') as file:
                file.write(str(self.highscore))
        else:
            self.draw_text("Рекорд: " + str(self.highscore), 36, LIGHTBLUE, WIDTH // 2, 160)

        buttons = [self.btn_play_again, self.btn_menu, self.btn_exit_go]

        while self.gameover_screen_run:
            button_pressed = self.wait_for_press(buttons, 'gameover')

            if button_pressed == self.btn_play_again:
                self.gameover_screen_run = False
                pg.mixer.music.fadeout(FADE_OUT)
                self.new_game()

            elif button_pressed == self.btn_menu:
                self.gameover_screen_run = False
                pg.mixer.music.fadeout(FADE_OUT)
                self.start()

            elif button_pressed == self.btn_exit_go:
                self.gameover_screen_run = False
                self.running = False
                pg.mixer.music.stop()
                pg.quit()

            if self.running:
                pg.display.flip()

    def wait_for_input(self):
        waiting = True
        while waiting:
            self.clock.tick(FPS)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    waiting = False
                    pg.mixer.music.stop()
                    self.running = False
                if event.type == pg.KEYUP:
                    waiting = False

    def wait_for_press(self, buttons, window):
        waiting = True
        while waiting:
            self.clock.tick(FPS)
            for event in pg.event.get():
                # если проигрывание музыки завершено, запустить другую
                if event.type == self.music_end:
                    if window == 'menu' or 'setting':
                        self.play_start_music()

                    if window == 'gameover':
                        self.play_gameover_music()

                if event.type == pg.QUIT:
                    pg.mixer.music.stop()
                    self.running = False
                    pg.quit()
                    return

                for button in buttons:
                    button.ishover()
                    if event.type == pg.MOUSEBUTTONDOWN:
                        if button.ispressed():
                            return button

            pg.display.flip()

    def draw_text(self, text, size, color, x, y):
        font = pg.font.Font(self.font_name, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.midtop = (x, y)
        self.screen.blit(text_surface, text_rect)


g = Game()
g.start()

pg.quit()
