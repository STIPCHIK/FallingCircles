import pygame.mixer

from ObjectClasses import Circle, gen_new_hamster
from Music import *
from config import *
import cv2
import numpy as np
from random import randint
from ImageFunctions import make_image_reddish, make_image_purplish
from  ObjectClasses import gen_new_circle

EXTREME_MODE_IMAGE_INTENSITY_CHANGE_SIGN = EXTREME_MODE_IMAGE_INTENSITY_CHANGE_SIGN_DEFAULT
EXTREME_MODE_IMAGE_CUR_INTENSITY = EXTREME_MODE_IMAGE_DEFAULT_INTENSITY


def start_hardmode():
    Circle.speed = [0,7]
    Circle.color = HARD_MODE_COLOR
    Circle.respawn = False
    Circle.radius = 18
    levelup_sound.play()
    play_music(hardmode_music)

def check_spawn_hamster(score):
    if score > HARD_MODE_STARTING_POINT and randint(1,HAMSTER_SPAWN_CHANCE) == 1:
        return gen_new_hamster()
    return None



# Function for extreme mod starting
def start_extrememode():
    Circle.speed = [0,10]
    Circle.color = EXTREME_MODE_COLOR
    Circle.respawn = False
    Circle.radius = 15
    levelup_sound.play()
    play_music(extrememode_music)

# Function for normal mod starting
def start_normalmode():
    Circle.speed = [0, DEFAULT_SPEED]
    Circle.color = DEFAULT_CIRCLE_COLOR
    Circle.respawn = START_RESPAWN_CIRCLES
    Circle.radius = DEFAULT_CIRCLE_RADIUS
    pygame.mixer.Sound.stop(gameover_sound)
    play_music(default_music)

# Gameover function
def gameover(flippedRGB, score):
    # Draw Game Over sign
    cv2.putText(flippedRGB, "Game Over", (WIDTH // 2 - 250, HEIGHT // 2), cv2.FONT_HERSHEY_SIMPLEX, 3, HARD_MODE_COLOR, 7, cv2.LINE_AA)
    cv2.putText(flippedRGB, f"Score: {score}", (WIDTH // 2 - 100, HEIGHT // 2 + 100), cv2.FONT_HERSHEY_SIMPLEX, 2, HARD_MODE_COLOR, 5, cv2.LINE_AA)
    cv2.putText(flippedRGB, "Press 'R' to restart", (WIDTH // 2 - 200, HEIGHT // 2 + 200), cv2.FONT_HERSHEY_SIMPLEX, 1, HARD_MODE_COLOR, 3, cv2.LINE_AA)
    gameover_sound.play()
    pygame.mixer.music.stop()
    # Cycle for screen color changing
    while True:
        flippedRGB[:, :, 0] = np.minimum(255, flippedRGB[:, :, 0] + 1)
        flippedRGB[:, :, 1] = np.maximum(0, flippedRGB[:, :, 1] - 1)
        flippedRGB[:, :, 2] = np.maximum(0, flippedRGB[:, :, 2] - 1)
        res_image = cv2.cvtColor(flippedRGB, cv2.COLOR_RGB2BGR)
        cv2.imshow("Falling Circles", res_image)
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            exit()
        elif key == ord('r'):
            return

# Hard mode function
def hard_mode(flippedRGB):
    cv2.putText(flippedRGB, "HARDMODE", (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, HARD_MODE_COLOR, 3, cv2.LINE_AA)
    return make_image_reddish(flippedRGB, intensity=50)

# Extreme mode function
def extreme_mode(flippedRGB):
    global EXTREME_MODE_IMAGE_CUR_INTENSITY, EXTREME_MODE_IMAGE_INTENSITY_CHANGE_SIGN
    cv2.putText(flippedRGB, "EXTREMEMODE", (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, EXTREME_MODE_COLOR, 3,
                        cv2.LINE_AA)
    if EXTREME_MODE_IMAGE_CUR_INTENSITY >= EXTREME_MODE_IMAGE_MAX_INTENSITY:
        EXTREME_MODE_IMAGE_INTENSITY_CHANGE_SIGN = -1
    elif EXTREME_MODE_IMAGE_CUR_INTENSITY <= EXTREME_MODE_IMAGE_MIN_INTENSITY:
        EXTREME_MODE_IMAGE_INTENSITY_CHANGE_SIGN = 1
    EXTREME_MODE_IMAGE_CUR_INTENSITY += EXTREME_MODE_IMAGE_INTENSITY_CHANGE_SIGN * EXTREME_MODE_IMAGE_INTENSITY_CHANGE_SPEED
    return make_image_purplish(flippedRGB, intensity=EXTREME_MODE_IMAGE_CUR_INTENSITY)
