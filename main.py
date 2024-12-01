from LoadingScreen import *
from config import *
loading_screen = LoadingScreen(WIDTH, HEIGHT)
loading_screen.show()
loading_screen.multiple_update(50)
import mediapipe as mp
loading_screen.multiple_update(15)
from ObjectClasses import *
loading_screen.multiple_update(5)
from ImageFunctions import *
loading_screen.multiple_update(5)
from Gamemods import *
loading_screen.multiple_update(5)
from Music import *
loading_screen.multiple_update(30)

hardmode = False
extrememode = False

# Инициализация камеры и детектора рук

handsDetector = mp.solutions.hands.Hands(max_num_hands=MAX_HANDS_COUNT)

sl, wl = list_ports()

cap = cv2.VideoCapture(max(wl))

# Генерируем круги, обозначаем хомяков и хайндеры
cur_aims = [gen_new_circle(STARTING_HEIGHT_RANDOM, WIDTH, HEIGHT) for _ in range(STARTING_CIRCLES_COUNT)]

hamsters = []

hinders = []
diagonal_hinders = []
loading_screen.multiple_update(15)

loading_screen.close()

# Основной цикл игры
while cap.isOpened():
    flippedRGB = prepare_cap_image(cap)
    if flippedRGB is False:
        break

    # Рисуем круги и обновляем их позиции
    for circle in cur_aims:
        circle.update()
        cv2.circle(flippedRGB, (circle.x, circle.y), circle.radius, circle.color, 5)

    # Рисуем курсор и обновляем его позицию
    results = handsDetector.process(flippedRGB)
    index_finger_positions = find_index_finger_positions(results, flippedRGB)


    # Счётчик кругов под экраном
    count_under_screen = 0

    for circle in cur_aims:
        # Проверяем, не ушёл ли круг за экран
        if circle.y > HEIGHT + circle.radius:
            # Если круги не респавнятся, то удаляем круг
            if Circle.respawn or GOD_MODE:
                new_circle = gen_new_circle(STARTING_HEIGHT_RANDOM, WIDTH, HEIGHT)
                circle.x, circle.y = new_circle.x, new_circle.y
            else:
                count_under_screen += 1
        # Проверяем, не соприкоснулся ли круг с курсором
        for x_tip, y_tip in index_finger_positions:
            if SHOW_FINGER_POINT:
                cv2.circle(flippedRGB, (x_tip, y_tip), 10, (255, 0, 0), -1)
            if (x_tip - circle.x) ** 2 + (y_tip - circle.y) ** 2 < circle.radius ** 2:
                score += 1
                pickup_sound.play()
                cv2.circle(flippedRGB, (circle.x - 1, circle.y), circle.radius, (0, 255, 0), 7)
                new_circle = gen_new_circle(STARTING_HEIGHT_RANDOM, WIDTH, HEIGHT)
                new_hamster = check_spawn_hamster(score)
                if new_hamster:
                    hamsters.append(new_hamster)
                circle.x, circle.y = new_circle.x, new_circle.y
                break  # Исключить двойное засчитывание круга

    # Если все круги под экраном, то конец игры
    if count_under_screen == len(cur_aims) and not GOD_MODE:
        gameover(flippedRGB, score)
        # Restart the game when cycle closed
        score = 0
        hardmode = False
        extrememode = False
        cur_aims = [gen_new_circle(STARTING_HEIGHT_RANDOM, WIDTH, HEIGHT) for _ in range(STARTING_CIRCLES_COUNT)]
        hamsters.clear()
        hinders.clear()
        diagonal_hinders.clear()
        start_normalmode()

    # Если остался один круг, то создаём хомяка (если их количество меньше максимального)
    if count_under_screen == len(cur_aims) - 1 and len(hamsters) < MAX_HAMSTERS:
        hamsters.append(Hamster(randint(0, WIDTH), randint(0, HEIGHT), [choice([-1,1]) * randint(Circle.speed[1]*2, Circle.speed[1]*3), choice([-1,1]) * randint(Circle.speed[1]*2, Circle.speed[1]*3)]))

    # Рисуем хомяков и обновляем их позиции
    for hamster in hamsters:
        hamster.update()
        hamster.draw(flippedRGB)
        # Если хомяк соприкоснулся с курсором, то удаляем хомяка и добавляем новый круг
        if (x_tip - hamster.x) ** 2 + (y_tip - hamster.y) ** 2 < 10000:
            # Воспроизводим звук
            hamster_sound.play()
            cur_aims.append(gen_new_circle(STARTING_HEIGHT_RANDOM, WIDTH, HEIGHT))
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
        hinders.append(gen_new_hinder(WIDTH, HEIGHT, randint(50,score), EXTREME_MODE_COLOR, Circle.speed[1]))

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

    # Функции сложного и экстрим режима

    if hardmode:
        flippedRGB = hard_mode(flippedRGB)

    if extrememode:
        flippedRGB = extreme_mode(flippedRGB)

    # Рисуем водяной знак о том, что включен режим бога
    if GOD_MODE:
        flippedRGB = draw_god_mode_watermark(flippedRGB)

    # Показываем изображение
    res_image = cv2.cvtColor(flippedRGB, cv2.COLOR_RGB2BGR)
    cv2.imshow("Falling Circles", res_image)
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    elif key == ord('r'):
        # Перезапускаем игру
        score = 0
        hardmode = False
        extrememode = False
        cur_aims = [gen_new_circle(STARTING_HEIGHT_RANDOM, WIDTH, HEIGHT) for _ in range(STARTING_CIRCLES_COUNT)]
        hamsters.clear()
        hinders.clear()
        diagonal_hinders.clear()
        start_normalmode()

# Закрываем окно и освобождаем ресурсы
handsDetector.close()