import pygame
# Инициализация миксера, музыки и звуков

pygame.mixer.init()

pickup_sound = pygame.mixer.Sound('static/sounds/pickup.wav')
levelup_sound = pygame.mixer.Sound('static/sounds/levelup.wav')
gameover_sound = pygame.mixer.Sound('static/sounds/death.wav')
hamster_sound = pygame.mixer.Sound('static/sounds/hamster.wav')

default_music = 'static/music/default_music.mp3'
hardmode_music = 'static/music/hardmode_music.mp3'
extrememode_music = 'static/music/extrememode_music.mp3'

# Функции для воспроизведения музыки

def play_music(music_file):
    pygame.mixer.music.load(music_file)
    pygame.mixer.music.play(-1)

# Воспроизведение музыки по умолчанию
play_music(default_music)