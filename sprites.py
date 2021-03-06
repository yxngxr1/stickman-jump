from settings import *
import pygame as pg
from pygame import gfxdraw
import random
import os
vec = pg.math.Vector2  # 2d - вектор


def load_image(name):
    fullname = os.path.join('images', name)
    image = pg.image.load(fullname).convert_alpha()
    return image


class Player(pg.sprite.Sprite):
    def __init__(self, game):
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.walkRight_images = [load_image('hero/{}.png'.format(i)) for i in range(1, 10)]
        self.walkLeft_images = [pg.transform.flip(load_image('hero/{}.png'.format(i)), True, False) for i in range(1, 10)]
        self.jump_image = load_image('hero/jump.png')
        self.fallLeft_images = [load_image('hero/fall{}.png'.format(i)) for i in range(1, 3)]
        self.fallRight_images = [pg.transform.flip(load_image('hero/fall{}.png'.format(i)), True, False) for i in range(1, 3)]
        self.standing_image = load_image('hero/standing.png')
        self.right = False
        self.left = False
        self.jumping = False
        self.OnGround = False
        self.walkcount = 0
        self.jumpcount = 0
        self.fallcount = 0
        self.image = self.standing_image
        self.rect = self.image.get_rect()
        self.width = self.rect[2]
        self.height = self.rect[3]
        self.rect.midbottom = (WIDTH / 2,HEIGHT - HEIGHT / 4)
        self.pos = vec(WIDTH / 2,HEIGHT - HEIGHT / 4)
        self.vel = vec(0, 0)  # скорость
        self.acc = vec(0, 0)  # ускорение


    def jump(self):
        hits = pg.sprite.spritecollide(self, self.game.platforms, False)
        if hits:
            if self.game.player.pos.y < hits[0].rect.bottom:
                self.game.jump_sound.play()

                if hits[0].color == YELLOW:
                    hits[0].clear = True

                elif hits[0].color == RED:
                    self.vel.y = -PLAYER_JUMP * 1.4
                    return

                self.vel.y = -PLAYER_JUMP

    def update(self):
        self.acc = vec(0, self.game.gravity)
        keys = pg.key.get_pressed()

        if keys[pg.K_SPACE]:
            if self.vel.y >= 0:
                self.jumping = True
                self.jump()
        else:
            self.jumping = False
            self.jumpcount = 0

        if keys[pg.K_LEFT]:
            self.acc.x = -PLAYER_ACCELERATION
            self.left = True
            self.right = False

        elif keys[pg.K_RIGHT]:
            self.acc.x = PLAYER_ACCELERATION
            self.left = False
            self.right = True

        else:
            self.walkcount = 0
            self.left = False
            self.right = False

        # анимация игрока
        self.animations()

        # установка позиции игрока по отношению к его скорости и ускорению
        self.acc.x -= self.vel.x * PLAYER_FRICTION
        self.vel += self.acc
        self.pos += self.vel

        # замкнутое пространсвто по горизонтали
        if self.pos.x > WIDTH + self.width // 5:
            self.pos.x = 0 - self.width // 5
        if self.pos.x < 0 - self.width // 5:
            self.pos.x = WIDTH + self.width // 5

        self.rect.midbottom = self.pos

    def animations(self):
        if self.jumping:
            self.jumpcount += 1
        self.fallcount += FPS // 6
        self.walkcount += FPS // 2

        if (self.walkcount // FPS) in range(0, 9):
            if self.right:
                if self.OnGround:
                    self.image = self.walkRight_images[self.walkcount // FPS]
                else:
                    if (self.fallcount // FPS) in range(0, 2) and self.vel.y > PLAYER_GRAVITY + FPS // 6:
                        self.image = self.fallRight_images[self.fallcount // FPS]

            elif self.left:
                if self.OnGround:
                    self.image = self.walkLeft_images[self.walkcount // FPS]
                else:
                    if (self.fallcount // FPS) in range(0, 2) and self.vel.y > PLAYER_GRAVITY + FPS // 6:
                        self.image = self.fallLeft_images[self.fallcount // FPS]
            else:
                if self.OnGround:
                    self.image = self.standing_image
                else:
                    if (self.fallcount // FPS) in range(0, 4):
                        if (self.fallcount // FPS) in range(0, 2) and self.vel.y > PLAYER_GRAVITY + FPS // 6:
                            self.image = self.fallRight_images[self.fallcount // FPS]
                        elif (self.fallcount // FPS) in range(2, 4) and self.vel.y > PLAYER_GRAVITY + FPS // 6:
                            self.image = self.fallLeft_images[self.fallcount // FPS - 2]
        self.mask = pg.mask.from_surface(self.image)
        if self.jumpcount > FPS // 3:
            self.jumping = False
            self.jumpcount = 0

        if self.jumping:
            self.image = self.jump_image

        if self.OnGround:
            self.fallcount = 0

        self.walkcount = 0 if self.walkcount == 540 else self.walkcount


class Platform(pg.sprite.Sprite):
    def __init__(self, game, color, x, y, w, h):
        self.groups = game.all_sprites, game.platforms
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.w, self.h = w, h
        self.color = color
        if self.color == GREEN:
            self.run_platform = True
            self.vel = random.choice(range(2, 4))
        if self.color == YELLOW:
            self.clearcount = 0
            self.clear = False
        self.image = pg.Surface((w, h))
        self.image.set_colorkey((BLACK))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        if random.randrange(20) == 1:
            Powerup(self.game, self)

    def update(self):
        if self.color == GREY:
            pg.draw.rect(self.image, self.color, [0, 0, self.w, self.h])

        elif self.color == GREEN:
            self.rect.x += self.vel
            if self.rect.x >= WIDTH - self.w:
                self.vel =- self.vel
            if self.rect.x <= 0:
                self.vel = abs(self.vel)
            pg.draw.rect(self.image, self.color, [0, 0, self.w, self.h], 5)

        elif self.color == YELLOW:
            if self.clear:
                self.clearcount += 1
                if self.clearcount > FPS // 2:
                    self.kill()
                    self.game.add_new_platform(-270)
            pg.draw.rect(self.image, self.color, [0, 0, self.w, self.h], 5)

        else:
            pg.draw.rect(self.image, self.color, [0, 0, self.w, self.h], 5)


class Background(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.image = load_image(BACKGROUND)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def update(self):
        if self.rect.y >= HEIGHT:
            self.rect.y = -HEIGHT


class Powerup(pg.sprite.Sprite):
    def __init__(self, game, platform):
        self.groups = game.all_sprites, game.powerups
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.platform = platform
        self.type = random.choice(['big jump', 'small gravity'])
        self.image = pg.Surface((40, 40))
        self.image.set_colorkey((BLACK))
        self.rect = self.image.get_rect()
        self.rect.centerx = self.platform.rect.centerx
        self.rect.bottom = self.platform.rect.top - 10

    def update(self):
        self.rect.centerx = self.platform.rect.centerx
        self.rect.bottom = self.platform.rect.top - 10
        if self.type == 'big jump':
            gfxdraw.aacircle(self.image, 12, 12, 12, YELLOW)
            gfxdraw.filled_circle(self.image, 12, 12, 12, YELLOW)
        elif self.type == 'small gravity':
            gfxdraw.aacircle(self.image, 12, 12, 12, VIOLET)
            gfxdraw.filled_circle(self.image, 12, 12, 12, VIOLET)
        self.mask = pg.mask.from_surface(self.image)
        if not self.game.platforms.has(self.platform):
            self.kill()


class Enemy(pg.sprite.Sprite):
    def __init__(self, game):
        self.groups = game.all_sprites, game.enemies
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image_left = pg.transform.scale(load_image('enemy/enemy.png'), (50, 75))
        self.image_right = pg.transform.scale(pg.transform.flip(load_image('enemy/enemy.png'), True, False), (50, 75))

        self.image = self.image_right
        self.rect = self.image.get_rect()

        self.rect.centerx = random.choice([-150, WIDTH + 150])
        self.rect.y = random.randrange(HEIGHT // 3) - random.choice([-100, 100, 300, 500])
        self.vx = random.choice([1, 1.5, 2, 2.5])
        if self.rect.centerx > WIDTH:
            self.vx = -self.vx
        self.vy = 0
        self.dy = random.choice([0.2, 0.3, 0.4])
        self.dmax = random.choice([2, 3, 4])

    def update(self):
        self.rect.x += self.vx
        self.vy += self.dy
        if self.vy >= self.dmax or self.vy <= -self.dmax:
            self.dy = -self.dy

        if self.vx < 0:
            self.image = self.image_left
        else:
            self.image = self.image_right
        self.mask = pg.mask.from_surface(self.image)
        self.rect.y += self.vy
        if self.rect.left > WIDTH + 500 or self.rect.right < - 500:
            self.kill()
