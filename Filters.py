import cv2


# Функция для изменения цвета изображения

def make_image_reddish(image, intensity=50):
    # Проверяем, что интенсивность находится в допустимых пределах
    intensity = max(0, min(intensity, 255))

    # Разделяем изображение на каналы
    r, g, b = cv2.split(image)

    # Увеличиваем красный канал (интенсивность)
    r = cv2.add(r, intensity)

    # Соединяем каналы обратно в изображение
    reddish_image = cv2.merge((r, g, b))

    return reddish_image

def make_image_purplish(image, intensity=50):
    # Проверяем, что интенсивность находится в допустимых пределах
    intensity = max(0, min(intensity, 255))

    # Разъединяем изображение на каналы
    r, g, b = cv2.split(image)

    # Меняем интенсивность красного и синего каналов
    r = cv2.add(r, intensity)
    b = cv2.add(b, intensity)

    # Соединим каналы обратно в изображение
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