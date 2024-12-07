import pygame
# Initialise mixer, sounds and music

pygame.mixer.init()

pickup_sound = pygame.mixer.Sound('static/sounds/pickup.wav')
levelup_sound = pygame.mixer.Sound('static/sounds/levelup.wav')
gameover_sound = pygame.mixer.Sound('static/sounds/death.wav')
hamster_sound = pygame.mixer.Sound('static/sounds/hamster.wav')

default_music = 'static/music/default_music.mp3'
hardmode_music = 'static/music/hardmode_music.mp3'
extrememode_music = 'static/music/extrememode_music.mp3'

# Function for music player

def play_music(music_file:str):
    pygame.mixer.music.load(music_file)
    pygame.mixer.music.play(-1)

# Default music
play_music(default_music)