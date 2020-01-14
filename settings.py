# основные настройки
TITLE = 'Stickman Jump'
WIDTH = 500
HEIGHT = 700
FPS = 60
FONT = 'arial'
HIGHSCORE = 'data/highscore.txt'
BUTTON_SIZE = (350, 75)

# музыка
MUSIC_MENU = ['sounds/Death Note OST - Solitude.ogg', "sounds/Death Note OST - L's Theme B.ogg"]
MUSIC_GAMEPLAY = ['sounds/Mortal Combat.ogg', "sounds/Tony Igy - Pentagramma.ogg"]
MUSIC_GAMEOVER = ['sounds/Grouplove - Back in the 90s.ogg', "sounds/Maximum the Hormone - What's up, people!.ogg"]
MUSIC_VOLUME = 0.15 # громкость музыки
FADE_OUT = 300 # постепенное уменьшение громкости, перед завершением проигрывания

# звуки
SOUND_JUMP = 'sounds/jump.wav'
SOUND_DEATH = 'sounds/death.ogg'
SOUND_BTN_HOVER = 'sounds/hover.wav'
SOUND_BTN_PRESS = 'sounds/press.wav'
SOUND_VOLUME = [0.03, 0.15, 0.5, 0.6] # громкость звуков (для каждого)

# свойства игрока
PLAYER_ACCELERATION = 1.5
PLAYER_FRICTION = 0.12
PLAYER_GRAVITY = 1.1
PLAYER_JUMP = 20

# цвета
BLACK = (0, 0, 0)
GREY = (10, 10, 10)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
LIGHTGREY = (50, 50, 50)
LIGHTRED = (255, 100, 100)
LIGHTGREEN = (100, 255, 100)
LIGHTBLUE = (50, 50, 255)
YELLOW = (255, 255, 0)
PINK = (255, 200, 200)
VIOLET = (255, 0, 200)

# test map
START_MAP = [(0, HEIGHT - 100, WIDTH, 100),
            (50, HEIGHT - 200, 100, 20),
            (300, HEIGHT - 300, 100, 20),
            (50, HEIGHT - 400, 100, 20),
            (300, HEIGHT - 550, 100, 20),]
