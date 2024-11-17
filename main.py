from pickle import FALSE

import cv2
import mediapipe as mp
import numpy as np
from random import randint, choice
import pygame

# Функция для добавления PNG изображения на изображение (для рисования хомяка)
def add_png_to_image(base_image, png_path, x_offset, y_offset):

    png_image = cv2.imread(png_path, cv2.IMREAD_UNCHANGED)
    b, g, r, a = cv2.split(png_image)
    overlay_color = cv2.merge((r, g, b))
    overlay_alpha = a / 255.0
    base_h, base_w = base_image.shape[:2]
    overlay_h, overlay_w = overlay_color.shape[:2]
    start_x = max(x_offset, 0)
    start_y = max(y_offset, 0)
    end_x = min(x_offset + overlay_w, base_w)
    end_y = min(y_offset + overlay_h, base_h)
    if start_x >= end_x or start_y >= end_y:
        return base_image
    visible_overlay = overlay_color[start_y - y_offset:end_y - y_offset, start_x - x_offset:end_x - x_offset]
    visible_alpha = overlay_alpha[start_y - y_offset:end_y - y_offset, start_x - x_offset:end_x - x_offset]
    roi = base_image[start_y:end_y, start_x:end_x]
    for c in range(0, 3):
        roi[:, :, c] = roi[:, :, c] * (1 - visible_alpha) + visible_overlay[:, :, c] * visible_alpha
    return base_image



# Класс для всех движущихся объектов
class MovingObject:
    def __init__(self, x:int, y:int, speed:list[int]):
        self.x = x
        self.y = y
        self.speed = speed

    def update(self):
        self.x += self.speed[0]
        self.y += self.speed[1]


    def __str__(self):
        return f"Object at ({self.x}, {self.y}) with speed {self.speed}"

# Класс падающих кругов

class Circle(MovingObject):
    def __init__(self, x, y, radius, color, speed:int):
        super().__init__(x, y, [0, speed])
        self.radius = radius
        self.color = color

    def draw(self, screen):
        cv2.circle(screen, (self.x, self.y), self.radius, self.color, 5)

# Класс хомяков, которые скачут по экрану (как DVD), когда у игрока остаётся 1 круг. При соприкосновении с хомяком игрок получает новый круг

class Hamster(MovingObject):
    def __init__(self, x, y, speed:list[int], image_path:str = 'static/images/hamster.png'):
        super().__init__(x, y, speed)
        self.image_path = image_path
        self.image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)

    def update(self):
        self.x += self.speed[0]
        self.y += self.speed[1]
        if self.x < 0:
            self.x = 0
            self.speed[0] *= -1
        elif self.x + self.image.shape[1] > WIDTH:
            self.x = WIDTH - self.image.shape[1]
            self.speed[0] *= -1
        if self.y < 0:
            self.y = 0
            self.speed[1] *= -1
        elif self.y + self.image.shape[0] > HEIGHT:
            self.y = HEIGHT - self.image.shape[0]
            self.speed[1] *= -1

    def draw(self, screen):
        add_png_to_image(screen, self.image_path, self.x, self.y)

    def __str__(self):
        return f"Hamster at ({self.x}, {self.y}) with speed {self.speed}"


# Класс хайндеров, которые являются восьмиугольниками и закрывают обзор игроку
# Их количество увеличивается по мере прохождения игры

class Hinder(MovingObject):
    def __init__(self, x, y, speed:list[int], size:int=30, color:tuple[int]=(0,0,0)):
        super().__init__(x, y, speed)
        self.shape = [[x,y],[x+size,y],[x+size+size//2,y+size//2],[x+size+size//2,y+size+size//2],[x+size,y+size+size],[x,y+size+size],[x-size//2,y+size//2+size],[x-size//2,y+size//2]]
        self.x += size//2
        self.y += size
        self.color = list(color)
        self.size = size

    def update(self):
        self.x += self.speed[0]
        self.y += self.speed[1]
        for i in range(len(self.shape)):
            self.shape[i][0] += self.speed[0]
            self.shape[i][1] += self.speed[1]
        self.color[0] = (self.color[0] + 5) % 255
        self.color[1] = (self.color[1] + 5) % 255
        self.color[2] = (self.color[2] - 5) % 255

    def draw(self, screen):
        cv2.fillPoly(screen, [np.array(self.shape, dtype=np.int32)], tuple(self.color))

# Класс диагональных хайндеров, которые являются параллелограммами и закрывают обзор игроку.
# Их количество также увеличивается по мере прохождения игры

class DiagonalHinder(MovingObject):
    def __init__(self,speed:int, size:int=100, color:tuple[int]=(0,0,0)):
        global WIDTH, HEIGHT
        super().__init__(-300 if speed > 0 else WIDTH+300, 0, [speed,0])
        if speed > 0:
            self.shape = [[-300, 0],[-300+size,0],[-300 + size + size,HEIGHT],[-300+size,HEIGHT]]
        else:
            self.shape = [[WIDTH+300, 0],[WIDTH+300-size,0],[WIDTH+300 - size - size,HEIGHT],[WIDTH+300-size,HEIGHT]]
        self.x += -300 if speed > 0 else WIDTH+300
        self.y += 0
        self.color = list(color)
        self.size = size

    def update(self):
        self.x += self.speed[0]
        for i in range(len(self.shape)):
            self.shape[i][0] += self.speed[0]
        self.color[0] = (self.color[0] - 5) % 255
        self.color[1] = (self.color[1] + 5) % 255
        self.color[2] = (self.color[2] - 5) % 255

    def draw(self, screen):
        cv2.fillPoly(screen, [np.array(self.shape, dtype=np.int32)], tuple(self.color))

# Функции для генерации хайндеров и кругов

def gen_new_diagonal_hinder(speed, size, color):
    return DiagonalHinder(choice([-1,1])*randint(10,50), size, color)

def gen_new_hinder(width, height, size, color, speed):
    return Hinder(randint(100, width - 100), randint(100, height - 230), [randint(-speed, speed), randint(-speed, speed)], size, color)

def gen_new_circle(starting_height_random, width, height, radius, color, speed):
    if starting_height_random:
        return Circle(randint(100, width - 100), randint(100, height - 230), radius, color, speed)
    else:
        return Circle(randint(100, width - 100), 0, radius, color, speed)


# Функция для определения рабочих портов камеры

def list_ports():
    is_working = True
    dev_port = 0
    working_ports = []
    available_ports = []
    while is_working:
        camera = cv2.VideoCapture(dev_port)
        if not camera.isOpened():
            is_working = False
            print(f"Порт {dev_port} не работает.")
        else:
            is_reading, img = camera.read()
            w = camera.get(3)
            h = camera.get(4)
            if is_reading:
                print(f"Порт {dev_port} работает и считывает изображение ({h} x {w})")
                working_ports.append(dev_port)
            else:
                print(f"Порт {dev_port} для камеры ({h} x {w}) есть, но не считывает изображение.")
                available_ports.append(dev_port)
        dev_port += 1
    return available_ports, working_ports

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

cap = cv2.VideoCapture(max(wl))

# ========================== НАСТРОЙКИ ИГРЫ ==========================

STARTING_HEIGHT_RANDOM = False
STARTING_CIRCLES_COUNT = 5
WIDTH, HEIGHT = 854, 480
CIRCLE_RADIUS = 20
SPEED = 5

DEFAULT_MODE_COLOR = (0, 0, 255)
HARD_MODE_COLOR = (200, 0, 0)
EXTREME_MODE_COLOR = (100, 0, 100)
CIRCLE_COLOR = (0, 0, 255)
RESPAWN_CIRCLES = True
hardmode = False
extrememode = False
SHOW_FINGER_POINT = True

HARD_MODE_STARTING_POINT = 50
EXTREME_MODE_STARTING_POINT = 100
HINDERS_STARTING_POINT = 120
DIAGONAL_HINDERS_STARTING_POINT = 150

MAX_HAMSTERS = 1
MAX_HINDERS = 1
MAX_DIAGONAL_HINDERS = 2

GOD_MODE = False

score = 0

# =====================================================================

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
    frame = cv2.resize(frame, (WIDTH, HEIGHT))

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
        cv2.putText(flippedRGB, "HARDMODE", (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, HARD_MODE_COLOR, 3, cv2.LINE_AA)
    if extrememode:
        cv2.putText(flippedRGB, "EXTEMEMODE", (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, EXTREME_MODE_COLOR, 3,
                    cv2.LINE_AA)

    # Показываем изображение
    res_image = cv2.cvtColor(flippedRGB, cv2.COLOR_RGB2BGR)
    cv2.imshow("Hands", res_image)

# Закрываем окно и освобождаем ресурсы
handsDetector.close()