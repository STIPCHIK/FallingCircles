import cv2
from config import *
import numpy as np

# Function for adding png to screen (for drawing Hamsters)
# Generated by ChatGPT
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


# Function for finding working camera ports
# Source: https://stackoverflow.com/questions/64667524/why-webcam-does-not-appear-in-python-opencv
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

# Get image from camera and prepare it
def prepare_cap_image(cap):
    ret, frame = cap.read()
    if not ret or frame is None:
        print("Ошибка чтения кадра.")
        return False

    # If we can't get image end the game
    if not ret:
        return False

    frame = cv2.resize(frame, (WIDTH, HEIGHT))

    # Flip image left to right and convert to RGB
    flipped = np.fliplr(frame)

    return cv2.cvtColor(flipped, cv2.COLOR_BGR2RGB)

# Function of finding tip finger position
def find_tip_position(results, flippedRGB):
    # Source: function from Canvas
    if results.multi_hand_landmarks is not None:
        x_tip = int(results.multi_hand_landmarks[0].landmark[8].x * flippedRGB.shape[1])
        y_tip = int(results.multi_hand_landmarks[0].landmark[8].y * flippedRGB.shape[0])
        if SHOW_FINGER_POINT:
            cv2.circle(flippedRGB, (x_tip, y_tip), 10, (255, 0, 0), -1)
        return x_tip, y_tip
    else:
        return -1, -1


# Functions for changing image color

def make_image_reddish(image, intensity=50):
    # Check image intensity
    intensity = max(0, min(intensity, 255))

    # Split image to channels
    r, g, b = cv2.split(image)

    # Increase red channel intensity
    r = cv2.add(r, intensity)

    # Merge channels
    reddish_image = cv2.merge((r, g, b))

    return reddish_image

def make_image_purplish(image, intensity=50):
    # Check intensity
    intensity = max(0, min(intensity, 255))

    # Split image to channels
    r, g, b = cv2.split(image)

    # Increase intensity of red and blue channels
    r = cv2.add(r, intensity)
    b = cv2.add(b, intensity)

    # Merge channels
    purplish_image = cv2.merge((r, g, b))

    return purplish_image

def draw_god_mode_watermark(image, text="GOD MODE", font=cv2.FONT_HERSHEY_SIMPLEX, font_scale=4, color=(0, 0, 0), thickness=10, alpha=0.1):
    overlay = image.copy()
    output = image.copy()
    text_size = cv2.getTextSize(text, font, font_scale, thickness)[0]
    text_x = (image.shape[1] - text_size[0]) // 2
    text_y = (image.shape[0] + text_size[1]) // 2
    cv2.putText(overlay, text, (text_x, text_y), font, font_scale, color, thickness)
    cv2.addWeighted(overlay, alpha, output, 1 - alpha, 0, output)
    return output

# Function for finding fingers position
# Depends on code from Canvas
def find_index_finger_positions(results, image):
    index_fingers = []
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            x = int(hand_landmarks.landmark[8].x * image.shape[1])  # ID 8 - кончик указательного пальца
            y = int(hand_landmarks.landmark[8].y * image.shape[0])
            index_fingers.append((x, y))
    return index_fingers