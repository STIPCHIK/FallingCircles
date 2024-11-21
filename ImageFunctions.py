import cv2


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