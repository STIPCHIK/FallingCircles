from random import randint, choice
import cv2
import numpy as np
from Settings import *

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
    def __init__(self, x, y, radius, color, speed: int):
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