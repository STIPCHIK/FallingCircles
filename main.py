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

# Initialise camera and mediapipe
handsDetector = mp.solutions.hands.Hands(max_num_hands=MAX_HANDS_COUNT)

sl, wl = list_ports()

cap = cv2.VideoCapture(max(wl))

# Generating circles
cur_aims = [gen_new_circle(STARTING_HEIGHT_RANDOM, WIDTH, HEIGHT) for _ in range(STARTING_CIRCLES_COUNT)]

hamsters = []

hinders = []
diagonal_hinders = []
loading_screen.multiple_update(15)

loading_screen.close()

# General game circle
while cap.isOpened():
    flippedRGB = prepare_cap_image(cap)
    if flippedRGB is False:
        break

    # Drawing circles and updating their position
    for circle in cur_aims:
        circle.update()
        cv2.circle(flippedRGB, (circle.x, circle.y), circle.radius, circle.color, 5)

    # Draw cursor and updating its position
    results = handsDetector.process(flippedRGB)
    index_finger_positions = find_index_finger_positions(results, flippedRGB)


    # Counting circles under screen
    count_under_screen = 0

    for circle in cur_aims:
        # Check that circles is under screen
        if circle.y > HEIGHT + circle.radius:
            # If circles spawn, spawning them
            if Circle.respawn or GOD_MODE:
                new_circle = gen_new_circle(STARTING_HEIGHT_RANDOM, WIDTH, HEIGHT)
                circle.x, circle.y = new_circle.x, new_circle.y
            else:
                count_under_screen += 1
        # Check colision between circles and fingers
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
                break  # Exclude double colision

    # If all circles are under screen, end the game
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

    # If only one circle exist spawn Hamster
    if count_under_screen == len(cur_aims) - 1 and len(hamsters) < MAX_HAMSTERS:
        hamsters.append(Hamster(randint(0, WIDTH), randint(0, HEIGHT), [choice([-1,1]) * randint(Circle.speed[1]*2, Circle.speed[1]*3), choice([-1,1]) * randint(Circle.speed[1]*2, Circle.speed[1]*3)]))

    # Draw hamsters and update their position
    for hamster in hamsters:
        hamster.update()
        hamster.draw(flippedRGB)
        # If colision between hamster and finger
        for x_tip, y_tip in index_finger_positions:
            if (x_tip - hamster.x) ** 2 + (y_tip - hamster.y) ** 2 < 10000:
                # Play sound
                hamster_sound.play()
                cur_aims.append(gen_new_circle(STARTING_HEIGHT_RANDOM, WIDTH, HEIGHT))
                hamsters.remove(hamster)

    # Check the beginning of hard mode and extreme mode
    if score >= HARD_MODE_STARTING_POINT and not hardmode and not extrememode:
        hardmode = True
        start_hardmode()
    if score >= EXTREME_MODE_STARTING_POINT and not extrememode:
        hardmode = False
        extrememode = True
        start_extrememode()

    # Check hinders spawn conditions
    if score >= HINDERS_STARTING_POINT and len(hinders) < MAX_HINDERS:
        hinders.append(gen_new_hinder(WIDTH, HEIGHT, randint(50,score), EXTREME_MODE_COLOR, Circle.speed[1]))

    if score >= DIAGONAL_HINDERS_STARTING_POINT and len(diagonal_hinders) < MAX_DIAGONAL_HINDERS:
        diagonal_hinders.append(gen_new_diagonal_hinder(choice([-1,1])*randint(10,50), randint(50,score), EXTREME_MODE_COLOR))

    # Update and draw hinders
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

    # Increase an amount of hinders (depends on score)

    MAX_HINDERS = (score - EXTREME_MODE_STARTING_POINT) // 50 + 2
    MAX_DIAGONAL_HINDERS = (score - EXTREME_MODE_STARTING_POINT) // 50 + 1

    # Draw the score counter
    cv2.putText(flippedRGB, f"Score: {score}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)

    # Functions of hard mode and extreme mode
    if hardmode:
        flippedRGB = hard_mode(flippedRGB)

    if extrememode:
        flippedRGB = extreme_mode(flippedRGB)

    # Drawing god mode watermark
    if GOD_MODE:
        flippedRGB = draw_god_mode_watermark(flippedRGB)

    # Show picture
    res_image = cv2.cvtColor(flippedRGB, cv2.COLOR_RGB2BGR)
    cv2.imshow("Falling Circles", res_image)
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    elif key == ord('r'):
        # Restart the game
        score = 0
        hardmode = False
        extrememode = False
        cur_aims = [gen_new_circle(STARTING_HEIGHT_RANDOM, WIDTH, HEIGHT) for _ in range(STARTING_CIRCLES_COUNT)]
        hamsters.clear()
        hinders.clear()
        diagonal_hinders.clear()
        start_normalmode()

# Close the game
handsDetector.close()