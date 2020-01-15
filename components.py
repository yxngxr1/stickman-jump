import pygame as pg


class Button:
    def __init__(self, game, text, s_font, s_rect, c, c_hover, c_press, x, y):
        self.game = game
        self.text = text
        self.size_font = s_font
        self.w, self.h = s_rect
        self.color = c
        self.color_hover = c_hover
        self.color_press = c_press
        self.x, self.y = x, y
        self.x_rect = self.x - self.w // 2
        self.y_rect = self.y - (self.h - self.size_font) // 3
        self.OnButton = False
        self.draw_text()
        self.draw_rect()

    def draw_text(self):
        self.game.draw_text(self.text, self.size_font, self.color, self.x, self.y)

    def draw_rect(self):
        x = self.x_rect
        y = self.y_rect
        w = self.w
        h = self.h
        pg.draw.rect(self.game.screen, self.color, (x, y, w, h), 5)

    def draw_rect_hover(self):
        x = self.x_rect
        y = self.y_rect
        w = self.w
        h = self.h
        pg.draw.rect(self.game.screen, self.color_hover, (x, y, w, h), 5)

    def draw_rect_press(self):
        x = self.x_rect
        y = self.y_rect
        w = self.w
        h = self.h
        pg.draw.rect(self.game.screen, self.color_press, (x, y, w, h), 5)

    def ishover(self):
        pos = pg.mouse.get_pos()
        hover = pos[0] in range(self.x_rect, self.x_rect + self.w) \
            and pos[1] in range(self.y_rect, self.y_rect + self.h)
        if hover:
            if not self.OnButton:
                self.game.hover_sound.play()
            self.OnButton = True
            self.draw_rect_hover()
        else:
            self.OnButton = False
            self.draw_rect()

    def ispressed(self):
        pos = pg.mouse.get_pos()
        pressed = pos[0] in range(self.x_rect, self.x_rect + self.w) \
            and pos[1] in range(self.y_rect, self.y_rect + self.h)
        if pressed:
            self.game.press_sound.play()
            self.draw_rect_press()
        else:
            self.draw_rect()

        return pressed
