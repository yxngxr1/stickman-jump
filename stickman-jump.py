import pygame as pg
import random
from pygame import gfxdraw
from components import Button
from settings import *
from sprites import Platform, Player, Background, Enemy, load_image


class Game:
    def __init__(self):
        # Инициализировать игровое окно
        pg.mixer.pre_init(44100, -16, 1, 512)
        pg.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        self.screen.set_colorkey((255, 255, 255))
        pg.display.set_icon(pg.image.load(ICON))
        pg.display.set_caption(TITLE)
        self.font_name = pg.font.match_font(FONT)
        self.clock = pg.time.Clock()
        self.running = True
        self.sound_on_off = True
        self.music_on_off = True
        self.str_sound_on_off = "Выключить звуки"
        self.str_music_on_off = "Выключить музыку"
        self.last_music = None
        self.load_data()

    def start(self):
        self.play_music('menu')
        self.menu_screen()

    def play_music(self, window):
        self.music_end = pg.USEREVENT + 1
        pg.mixer.music.set_endevent(self.music_end)

        if window == 'menu':
            music = MUSIC_MENU
        elif window == 'gameplay':
            music = MUSIC_GAMEPLAY
        else:
            music = MUSIC_GAMEOVER

        file = random.choice(music)
        while file == self.last_music:
            file = random.choice(music)
        pg.mixer.music.load(file)
        pg.mixer.music.set_volume(self.music_volume)
        pg.mixer.music.play(1)
        self.last_music = file

    def load_data(self):
        # загрузка рекорда
        with open(HIGHSCORE, 'r') as file:
            try:
                self.highscore = int(file.read())
            except ValueError:
                self.highscore = 0

            self.jump_sound = pg.mixer.Sound(SOUND_JUMP)
            self.powerup_sound = pg.mixer.Sound(SOUND_POWERUP)
            self.death_sound = pg.mixer.Sound(SOUND_DEATH)
            self.hover_sound = pg.mixer.Sound(SOUND_BTN_HOVER)
            self.press_sound = pg.mixer.Sound(SOUND_BTN_PRESS)
            self.music_volume = MUSIC_VOLUME
            self.sound_volume = SOUND_VOLUME
            self.change_volume(SOUND_VOLUME, MUSIC_VOLUME)

    def change_volume(self, sound_volume, music_volume):
        self.jump_sound.set_volume(sound_volume[0])
        self.powerup_sound.set_volume(sound_volume[1])
        self.death_sound.set_volume(sound_volume[2])
        self.hover_sound.set_volume(sound_volume[3])
        self.press_sound.set_volume(sound_volume[4])
        pg.mixer.music.set_volume(music_volume)
        self.sound_volume = sound_volume
        self.music_volume = music_volume

    def new_game(self):
        # Начать новую игру
        self.score = 0
        self.death = False
        self.bg_count = 0
        self.gravity = PLAYER_GRAVITY
        self.gravity_on_off = True
        self.gravity_count = 0
        self.enemy_count = 0
        self.all_sprites = pg.sprite.Group()
        self.platforms = pg.sprite.Group()
        self.powerups = pg.sprite.Group()
        self.enemies = pg.sprite.Group()

        self.background1 = Background(self, 0, -HEIGHT)
        self.background2 = Background(self, 0, 0)
        self.player = Player(self)

        for i in START_MAP:
            Platform(self, *i)

        self.run()

    def run(self):
        self.play_music('gameplay')

        # Главный игровой цикл
        self.playing = True
        while self.playing:
            self.clock.tick(FPS)

            # обязательная проверка на сохранность игрового процесса
            if self.playing:
                self.events()  # проверка событий

            if self.playing:
                self.update()  # обновление всех событий в игре

            if self.playing:
                self.draw()  # отрисовка игрового мира

        if self.running:
            pg.mixer.music.fadeout(FADE_OUT - 200 if FADE_OUT > 200 else 0)
            self.gameover_screen()

    def events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                if self.playing:
                    self.playing = False
                self.running = False
                pg.quit()

            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    if self.playing:
                        self.playing = False
                    self.running = False
                    pg.quit()

            if event.type == self.music_end:
                self.play_music('gameplay')

    def update(self):
        self.all_sprites.update()

        # спавн врагов по времени
        now = pg.time.get_ticks()
        if now - self.enemy_count > 6000 +  random.choice([-1000, -500, 0, 500, 1000]):
            self.enemy_count = now
            Enemy(self)

        # поставить игрока на платформу при падении
        if self.player.vel.y > 0:
            hits = pg.sprite.spritecollide(self.player, self.platforms, False)
            if hits:
                object = hits[0]
                for hit in hits:
                    if hit.rect.bottom > object.rect.bottom:
                        object = hit

                if self.player.pos.x < object.rect.right + 10 and \
                    self.player.pos.x > object.rect.left - 10:
                    if self.player.pos.y < object.rect.bottom + object.rect.height:
                        self.player.pos.y = object.rect.top

                        # добавить к скорости игрока скорость платформы на которой он стоит
                        if hits[0].color == GREEN:
                            self.player.pos.x += hits[0].vel
                        self.player.vel.y = 0
                        self.player.OnGround = True
            else:
                self.player.OnGround = False

        # смещение мира по отношению к игроку (камера)
        if self.player.pos.y <= HEIGHT // 3 + 100:
            self.player.pos.y += abs(self.player.vel.y)
            self.background1.rect.y += abs(int(self.player.vel.y * 0.4))
            self.background2.rect.y += abs(int(self.player.vel.y * 0.4))
            for i in self.enemies:
                i.rect.y += abs(self.player.vel.y)
                # удаление врага за экраном
                if i.rect.top >= HEIGHT:
                    i.kill()
            for i in self.platforms:
                i.rect.y += abs(self.player.vel.y)
                # удаление платформ за экраном
                if i.rect.top >= HEIGHT:
                    i.kill()
            self.score += abs(int(self.player.vel.y))

        # добавление новых платформ
        self.add_new_platform(-20)

        # соприкосновение с бонусом
        powerup_hits = pg.sprite.spritecollide(self.player, self.powerups, True, pg.sprite.collide_mask)
        for powerup in powerup_hits:
            if powerup.type == 'big jump':
                self.powerup_sound.play()
                self.player.vel.y = -POWERUP_JUMP
                self.player.jumping = False

            elif powerup.type == 'small gravity':
                self.powerup_sound.play()
                self.gravity_count = 0
                self.gravity_on_off = False

        self.gravity = PLAYER_GRAVITY if self.gravity_on_off else POWERUP_GRAVITY
        if not self.gravity_on_off:
            self.gravity_count += 1
            if self.gravity_count >= 600:
                self.gravity_count = 0
                self.gravity_on_off = True

        # соприкосновение с врагом
        enemy_hits = pg.sprite.spritecollide(self.player, self.enemies, False, pg.sprite.collide_mask)
        if enemy_hits:
            self.death_sound.play()
            self.playing = False

        # смерть игрока
        if self.player.rect.top > HEIGHT:
            if self.death is False:
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
        self.all_sprites.draw(self.screen)
        self.draw_text_mid(f'Набрано очков: {self.score}', 28, RED, WIDTH / 2, 15)
        if not self.gravity_on_off:
            self.draw_text_mid('Антигравитация', 48, RED, WIDTH / 2, 60)
            self.draw_text_mid(f'{10 - int(self.gravity_count // FPS)}', 80, RED, WIDTH / 2, 100)

        pg.display.flip()

    def add_new_platform(self, y):
        if len(self.platforms) < 6:
            w = random.choice([60, 80, 100])
            h = 20
            x = random.randrange(20, WIDTH - w - 20)
            y = y
            color = random.choice([BLUE, RED, GREEN])
            Platform(self, color, x, y, w, h)

    def menu_screen(self):
        self.menu_screen_run = True
        self.screen.fill(LIGHTGREY)
        self.draw_text_mid("Stickman Jump", 64, WHITE, WIDTH // 2, 20)
        self.draw_text_mid("Рекорд: " + str(self.highscore), 24, WHITE, WIDTH // 2, 100)
        self.draw_text_mid("v.1.0", 24, WHITE, 40, HEIGHT - 40)
        # кнопки
        self.btn_play = Button(self, "Играть", 48, BUTTON_SIZE, WHITE, LIGHTGREEN, LIGHTBLUE, WIDTH // 2, HEIGHT // 3)
        self.btn_settings = Button(self, "Настройки", 48, BUTTON_SIZE, WHITE, LIGHTBLUE, LIGHTBLUE, WIDTH // 2, HEIGHT // 3 + 100)
        self.btn_info = Button(self, "Информация", 48, BUTTON_SIZE , WHITE, LIGHTBLUE, LIGHTBLUE, WIDTH // 2, HEIGHT // 3 + 200)
        self.btn_exit_menu = Button(self, "Выйти из игры", 48, BUTTON_SIZE, WHITE, RED, LIGHTBLUE, WIDTH // 2, HEIGHT // 3 + 300)

        buttons = [self.btn_play, self.btn_settings, self.btn_exit_menu, self.btn_info]

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
                pg.quit()

            elif button_pressed == self.btn_info:
                self.menu_screen_run = False
                self.info_screen()

            if self.running:
                pg.display.flip()

    def settings_screen(self):
        self.settings_screen_run = True
        self.screen.fill(LIGHTGREY)
        self.draw_text_mid("Настройки", 64, WHITE, WIDTH // 2, 20)
        # кнопки
        self.btn_sound_on_off = Button(self, self.str_sound_on_off, 36, BUTTON_SIZE, WHITE, LIGHTGREEN, LIGHTBLUE, WIDTH // 2, HEIGHT // 3)
        self.btn_music_on_off = Button(self, self.str_music_on_off, 36, BUTTON_SIZE, WHITE, LIGHTGREEN, LIGHTBLUE, WIDTH // 2, HEIGHT // 3 + 100)
        self.btn_reset = Button(self, "Сброс данных", 40, BUTTON_SIZE, WHITE, RED, LIGHTBLUE, WIDTH // 2, HEIGHT // 3 + 200)
        self.btn_menu = Button(self, "Назад", 48, (int(BUTTON_SIZE[0] // 1.5), BUTTON_SIZE[1]), WHITE, LIGHTBLUE, LIGHTBLUE, WIDTH // 2, HEIGHT // 3 + 300)

        buttons = [self.btn_sound_on_off, self.btn_music_on_off, self.btn_reset, self.btn_menu]

        while self.settings_screen_run:
            button_pressed = self.wait_for_press(buttons, 'setting')

            if button_pressed == self.btn_sound_on_off:
                self.sound_on_off = True if not self.sound_on_off else False
                self.str_sound_on_off = "Включить звуки" if not self.sound_on_off else "Выключить звуки"
                if not self.sound_on_off:
                    self.change_volume([0, 0, 0, 0, 0], self.music_volume)
                else:
                    self.change_volume(SOUND_VOLUME, self.music_volume)
                self.settings_screen()

            elif button_pressed == self.btn_music_on_off:
                self.music_on_off = True if not self.music_on_off else False
                self.str_music_on_off = "Включить музыку" if not self.music_on_off else "Выключить музыку"
                if not self.music_on_off:
                    self.change_volume(self.sound_volume, 0)
                else:
                    self.change_volume(self.sound_volume, MUSIC_VOLUME)
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

    def info_screen(self):
        self.info_screen_run = True
        self.screen.fill(LIGHTGREY)

        # отрисовка полевых объектов
        pg.draw.rect(self.screen, RED, (WIDTH // 4 - 80, 230 + 6, 100, 20), 3)
        pg.draw.rect(self.screen, GREEN, (WIDTH // 4 - 80, 260 + 6, 100, 20), 3)
        pg.draw.rect(self.screen, BLUE, (WIDTH // 4 - 80, 290 + 6, 100, 20), 3)
        gfxdraw.aacircle(self.screen, WIDTH // 4 - 20, 390 + 18, 12, YELLOW)
        gfxdraw.filled_circle(self.screen, WIDTH // 4 - 20, 390 + 18, 12, YELLOW)
        gfxdraw.aacircle(self.screen, WIDTH // 4 - 20, 420 + 18, 12,  VIOLET)
        gfxdraw.filled_circle(self.screen, WIDTH // 4 - 20, 420 + 18, 12,  VIOLET)
        self.screen.blit(pg.transform.scale(load_image('enemy/enemy.png'), (50, 75)), (155, 500))

        self.draw_text_mid("Управление", 50, WHITE, WIDTH // 2, 10)
        self.draw_text_mid("–> - вправо", 28, WHITE, WIDTH // 2, 70)
        self.draw_text_mid("<– - влево", 28, WHITE, WIDTH // 2, 100)
        self.draw_text_mid("Space - прыжок", 28, WHITE, WIDTH // 2, 130)

        self.draw_text_mid("Платформы", 50, WHITE, WIDTH // 2, 170)
        self.draw_text("–  усиливают прыжок", 28, WHITE, WIDTH // 2 - 80, 230)
        self.draw_text("–  двигаются", 28, WHITE, WIDTH // 2 - 80, 260)
        self.draw_text("–  стоят на месте", 28, WHITE, WIDTH // 2 - 80, 290)

        self.draw_text_mid("Бонусы", 50, WHITE, WIDTH // 2, 330)
        self.draw_text("–  ускоритель", 28, WHITE, WIDTH // 3 - 30, 390)
        self.draw_text("–  слабая сила тяжести", 28, WHITE, WIDTH // 3 - 30, 420)

        self.draw_text_mid("Враги", 50, WHITE, WIDTH // 2, 460)
        self.draw_text("–  клякса", 28, WHITE, WIDTH // 2 - 30, 520)

        self.draw_text_mid("© 2020, Yxngxr1, Георгий Дерганов", 25, (150, 150, 150), WIDTH // 2, HEIGHT - 40)



        # кнопки
        self.btn_menu = Button(self, "Назад", 48, (int(BUTTON_SIZE[0] // 1.5), BUTTON_SIZE[1]), WHITE, LIGHTBLUE, LIGHTBLUE, WIDTH // 2, HEIGHT // 3 + 370 - 20)

        buttons = [self.btn_menu]

        while self.info_screen_run:
            button_pressed = self.wait_for_press(buttons, 'info')
            if button_pressed == self.btn_menu:
                self.info_screen_run = False
                self.menu_screen()

            if self.running:
                pg.display.flip()

    def gameover_screen(self):
        self.gameover_screen_run = True
        self.play_music('gameover')
        self.screen.fill(LIGHTGREY)
        self.draw_text_mid("GAME OVER", 82, RED, WIDTH // 2, 20)
        self.draw_text_mid("Очков: " + str(self.score), 24, WHITE, WIDTH // 2, 120)

        self.btn_play_again = Button(self, "Играть заново", 48, BUTTON_SIZE, WHITE, LIGHTGREEN, LIGHTBLUE, WIDTH // 2, HEIGHT // 3 + 50)
        self.btn_menu = Button(self, "Меню", 48, BUTTON_SIZE, WHITE, LIGHTBLUE, LIGHTBLUE, WIDTH // 2, HEIGHT // 3 + 150)
        self.btn_exit_go = Button(self, "Выйти из игры", 48, BUTTON_SIZE, WHITE, RED, LIGHTGREEN, WIDTH // 2, HEIGHT // 3 + 250)

        if self.score > self.highscore:
            self.highscore = self.score
            self.draw_text_mid('Ты побил рекорд, поздравляю!', 30, LIGHTBLUE, WIDTH // 2, 160)
            with open(HIGHSCORE, 'w') as file:
                file.write(str(self.highscore))
        else:
            self.draw_text_mid("Рекорд: " + str(self.highscore), 36, LIGHTBLUE, WIDTH // 2, 160)

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
            if self.running:
                self.clock.tick(FPS)
                for event in pg.event.get():
                    # если проигрывание музыки завершено, запустить другую
                    if event.type == self.music_end:
                        if window == 'menu' or 'setting' or 'info':
                            self.play_music('menu')

                        if window == 'gameover':
                            self.play_music('gameover')

                    if event.type == pg.QUIT:
                        if window == 'menu':
                            self.menu_screen_run = False
                        elif window == 'setting':
                            self.settings_screen_run = False
                        elif window == 'info':
                            self.info_screen_run = False
                        elif window == 'gameover':
                            self.gameover_screen_run = False

                        self.running = False
                        pg.quit()
                        return

                    for button in buttons:
                        button.ishover()
                        if event.type == pg.MOUSEBUTTONDOWN:
                            if button.ispressed():
                                return button

                pg.display.flip()

    def draw_text_mid(self, text, size, color, x, y):
        font = pg.font.Font(self.font_name, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.midtop = (x, y)
        self.screen.blit(text_surface, text_rect)

    def draw_text(self, text, size, color, x, y):
        font = pg.font.Font(self.font_name, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect = (x, y)
        self.screen.blit(text_surface, text_rect)


g = Game()
g.start()

pg.quit()
