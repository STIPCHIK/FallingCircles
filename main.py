import cv2
import mediapipe as mp
import numpy as np
from random import randint, choice
import pygame

from Settings import *
from ObjectClasses import *
from Filters import *
from ImageFunctions import *

# Инициализация миксера, музыки и звуков

pygame.mixer.init()

pickup_sound = pygame.mixer.Sound('static/sounds/pickup.wav')
levelup_sound = pygame.mixer.Sound('static/sounds/levelup.wav')
gameover_sound = pygame.mixer.Sound('static/sounds/death.wav')

default_music = 'static/music/default_music.mp3'
hardmode_music = 'static/music/hardmode_music.mp3'
extrememode_music = 'static/music/extrememode_music.mp3'

# Функции для воспроизведения музыки

def play_music(music_file):
    pygame.mixer.music.load(music_file)
    pygame.mixer.music.play(-1)

# Воспроизведение музыки по умолчанию
play_music(default_music)

# Инициализация камеры и детектора рук

handsDetector = mp.solutions.hands.Hands()

sl, wl = list_ports()


def start_hardmode():
    global SPEED, HARD_MODE_COLOR, CIRCLE_COLOR, RESPAWN_CIRCLES, CIRCLE_RADIUS
    SPEED = 7
    CIRCLE_COLOR = HARD_MODE_COLOR
    RESPAWN_CIRCLES = False
    CIRCLE_RADIUS = 18
    levelup_sound.play()
    play_music(hardmode_music)

    for i in cur_aims:
        i.speed = [0,SPEED]
        i.radius = CIRCLE_RADIUS
        i.color = CIRCLE_COLOR

# Функция для начала экстремод
def start_extrememode():
    global SPEED, EXTREME_MODE_COLOR, CIRCLE_COLOR, RESPAWN_CIRCLES, CIRCLE_RADIUS
    SPEED = 10
    CIRCLE_COLOR = EXTREME_MODE_COLOR
    RESPAWN_CIRCLES = False
    CIRCLE_RADIUS = 15
    levelup_sound.play()
    play_music(extrememode_music)
    for i in cur_aims:
        i.speed = [0,SPEED]
        i.radius = CIRCLE_RADIUS
        i.color = CIRCLE_COLOR

cap = cv2.VideoCapture(max(wl))



# Функция для начала хардмода
def start_hardmode():
    global SPEED, HARD_MODE_COLOR, CIRCLE_COLOR, RESPAWN_CIRCLES, CIRCLE_RADIUS
    SPEED = 7
    CIRCLE_COLOR = HARD_MODE_COLOR
    RESPAWN_CIRCLES = False
    CIRCLE_RADIUS = 18
    levelup_sound.play()
    play_music(hardmode_music)

    for i in cur_aims:
        i.speed = [0,SPEED]
        i.radius = CIRCLE_RADIUS
        i.color = CIRCLE_COLOR

# Функция для начала экстремод
def start_extrememode():
    global SPEED, EXTREME_MODE_COLOR, CIRCLE_COLOR, RESPAWN_CIRCLES, CIRCLE_RADIUS
    SPEED = 10
    CIRCLE_COLOR = EXTREME_MODE_COLOR
    RESPAWN_CIRCLES = False
    CIRCLE_RADIUS = 15
    levelup_sound.play()
    play_music(extrememode_music)
    for i in cur_aims:
        i.speed = [0,SPEED]
        i.radius = CIRCLE_RADIUS
        i.color = CIRCLE_COLOR

# Генерируем круги, обозначаем хомяков и хайндеры
cur_aims = [gen_new_circle(STARTING_HEIGHT_RANDOM, WIDTH, HEIGHT, CIRCLE_RADIUS, CIRCLE_COLOR, SPEED) for _ in range(STARTING_CIRCLES_COUNT)]

hamsters = []

hinders = []
diagonal_hinders = []


# Переменная обозначающая конец игры
gameover = False


# Основной цикл игры
while cap.isOpened():
    # Считываем изображение с камеры и изменяем его размер
    ret, frame = cap.read()
    if not ret or frame is None:
        print("Ошибка чтения кадра.")
        break
    frame = cv2.resize(frame, (WIDTH, HEIGHT))

    # Отражаем изображение по горизонтали и конвертируем его в RGB
    flipped = np.fliplr(frame)
    flippedRGB = cv2.cvtColor(flipped, cv2.COLOR_BGR2RGB)

    # Если изображение не считывается (или зажата кнопка Q), то заканчиваем игру
    if cv2.waitKey(1) & 0xFF == ord('q') or not ret:
        break

    # Отражаем изображение по горизонтали и конвертируем его в RGB
    flipped = np.fliplr(frame)
    flippedRGB = cv2.cvtColor(flipped, cv2.COLOR_BGR2RGB)

    # Рисуем круги и обновляем их позиции
    for circle in cur_aims:
        circle.update()
        cv2.circle(flippedRGB, (circle.x, circle.y), circle.radius, circle.color, 5)

    # Рисуем курсор и обновляем его позицию
    results = handsDetector.process(flippedRGB)
    if results.multi_hand_landmarks is not None:
        x_tip = int(results.multi_hand_landmarks[0].landmark[8].x * flippedRGB.shape[1])
        y_tip = int(results.multi_hand_landmarks[0].landmark[8].y * flippedRGB.shape[0])
        if SHOW_FINGER_POINT:
            cv2.circle(flippedRGB, (x_tip, y_tip), 10, (255, 0, 0), -1)
    else:
        x_tip = -1
        y_tip = -1

    # Счётчик кругов под экраном
    count_under_screen = 0

    for circle in cur_aims:
        # Проверяем, не ушёл ли круг за экран
        if circle.y > HEIGHT + circle.radius:
            # Если круги не респавнятся, то удаляем круг
            if RESPAWN_CIRCLES or GOD_MODE:
                new_circle = gen_new_circle(STARTING_HEIGHT_RANDOM, WIDTH, HEIGHT, CIRCLE_RADIUS, CIRCLE_COLOR, SPEED)
                circle.x, circle.y = new_circle.x, new_circle.y
            else:
                count_under_screen += 1
        # Проверяем, не соприкоснулся ли круг с курсором
        if (x_tip - circle.x) ** 2 + (y_tip - circle.y) ** 2 < circle.radius ** 2:
            score += 1
            pickup_sound.play()
            # Красим круг в зелёный цвет
            cv2.circle(flippedRGB, (circle.x - 1, circle.y), circle.radius, (0, 255, 0), 7)
            # Генерируем новый круг (А точнее заменяем координаты старого на новые для оптимизации)
            new_circle = gen_new_circle(STARTING_HEIGHT_RANDOM, WIDTH, HEIGHT, CIRCLE_RADIUS, CIRCLE_COLOR, SPEED)
            circle.x, circle.y = new_circle.x, new_circle.y

    # Если все круги под экраном, то конец игры
    if count_under_screen == len(cur_aims) or (gameover and not GOD_MODE):
        # Рисуем надпись Game Over
        cv2.putText(flippedRGB, "Game Over", (WIDTH // 2 - 250, HEIGHT // 2), cv2.FONT_HERSHEY_SIMPLEX, 3, HARD_MODE_COLOR, 7, cv2.LINE_AA)
        cv2.putText(flippedRGB, f"Score: {score}", (WIDTH // 2 - 100, HEIGHT // 2 + 100), cv2.FONT_HERSHEY_SIMPLEX, 2, HARD_MODE_COLOR, 5, cv2.LINE_AA)
        brek = False
        gameover_sound.play()
        pygame.mixer.music.stop()
        # Цикл для изменения цвета экрана
        while not brek:
            flippedRGB[:, :, 0] = np.minimum(255, flippedRGB[:, :, 0] + 1)
            flippedRGB[:, :, 1] = np.maximum(0, flippedRGB[:, :, 1] - 1)
            flippedRGB[:, :, 2] = np.maximum(0, flippedRGB[:, :, 2] - 1)
            res_image = cv2.cvtColor(flippedRGB, cv2.COLOR_RGB2BGR)
            cv2.imshow("Hands", res_image)
            cv2.waitKey(1)
        gameover = True

    # Если остался один круг, то создаём хомяка (если их количество меньше максимального)
    if count_under_screen == len(cur_aims) - 1 and len(hamsters) < MAX_HAMSTERS:
        hamsters.append(Hamster(randint(0, WIDTH), randint(0, HEIGHT), [choice([-1,1]) * randint(SPEED*2, SPEED*3), choice([-1,1]) * randint(SPEED*2, SPEED*3)]))

    # Рисуем хомяков и обновляем их позиции
    for hamster in hamsters:
        hamster.update()
        hamster.draw(flippedRGB)
        # Если хомяк соприкоснулся с курсором, то удаляем хомяка и добавляем новый круг
        if (x_tip - hamster.x) ** 2 + (y_tip - hamster.y) ** 2 < 10000:
            cur_aims.append(gen_new_circle(STARTING_HEIGHT_RANDOM, WIDTH, HEIGHT, CIRCLE_RADIUS, CIRCLE_COLOR, SPEED))
            hamsters.remove(hamster)

    # Проверка на начало хардмода и экстриммода
    if score >= HARD_MODE_STARTING_POINT and not hardmode and not extrememode:
        hardmode = True
        start_hardmode()
    if score >= EXTREME_MODE_STARTING_POINT and not extrememode:
        hardmode = False
        extrememode = True
        start_extrememode()

    # Проверка на начало создания хайндеров и диагональных хайндеров
    if score >= HINDERS_STARTING_POINT and len(hinders) < MAX_HINDERS:
        hinders.append(gen_new_hinder(WIDTH, HEIGHT, randint(50,score), EXTREME_MODE_COLOR, SPEED))

    if score >= DIAGONAL_HINDERS_STARTING_POINT and len(diagonal_hinders) < MAX_DIAGONAL_HINDERS:
        diagonal_hinders.append(gen_new_diagonal_hinder(choice([-1,1])*randint(10,50), randint(50,score), EXTREME_MODE_COLOR))

    # Обновляем и рисуем хайндеры и диагональные хайндеры
    for hinder in hinders:
        hinder.update()
        hinder.draw(flippedRGB)
        if hinder.x + hinder.size*2 < 0 or hinder.x - hinder.size*2 > WIDTH:
            hinders.remove(hinder)
        if hinder.y + hinder.size*2 < 0 or hinder.y - hinder.size*2 > HEIGHT:
            hinders.remove(hinder)

    for hinder in diagonal_hinders:
        hinder.update()
        hinder.draw(flippedRGB)
        if (hinder.x + hinder.size*2 < 0 and hinder.speed[0] < 0) or (hinder.x - hinder.size*2 > WIDTH and hinder.speed[0] > 0):
            diagonal_hinders.remove(hinder)

    # Увеличиваем количество хайндеров и диагональных хайндеров (зависит от количества очков)

    MAX_HINDERS = (score - EXTREME_MODE_STARTING_POINT) // 50 + 2
    MAX_DIAGONAL_HINDERS = (score - EXTREME_MODE_STARTING_POINT) // 50 + 1

    # Рисуем количество очков и режим игры
    cv2.putText(flippedRGB, f"Score: {score}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)


    if hardmode:
        flippedRGB = make_image_reddish(flippedRGB, intensity=50)
        cv2.putText(flippedRGB, "HARDMODE", (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, HARD_MODE_COLOR, 3, cv2.LINE_AA)

    if extrememode:
        cv2.putText(flippedRGB, "EXTREMEMODE", (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, EXTREME_MODE_COLOR, 3,
                    cv2.LINE_AA)
        if EXTREME_MODE_IMAGE_CUR_INTENSITY >= EXTREME_MODE_IMAGE_MAX_INTENSITY:
            EXTREME_MODE_IMAGE_INTENSITY_CHANGE_SIGN = -1
        elif EXTREME_MODE_IMAGE_CUR_INTENSITY <= EXTREME_MODE_IMAGE_MIN_INTENSITY:
            EXTREME_MODE_IMAGE_INTENSITY_CHANGE_SIGN = 1
        EXTREME_MODE_IMAGE_CUR_INTENSITY += EXTREME_MODE_IMAGE_INTENSITY_CHANGE_SIGN * EXTREME_MODE_IMAGE_INTENSITY_CHANGE_SPEED
        flippedRGB = make_image_purplish(flippedRGB, intensity=EXTREME_MODE_IMAGE_CUR_INTENSITY)

    # Рисуем водяной знак о том, что включен режим бога
    if GOD_MODE:
        flippedRGB = draw_god_mode_watermark(flippedRGB)

    # Показываем изображение
    res_image = cv2.cvtColor(flippedRGB, cv2.COLOR_RGB2BGR)
    cv2.imshow("Hands", res_image)

# Закрываем окно и освобождаем ресурсы
handsDetector.close()