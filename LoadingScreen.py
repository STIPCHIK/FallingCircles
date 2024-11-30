import cv2
import numpy as np
from random import randint

class LoadingScreen:
    def __init__(self, width, height, text="Loading...", font=cv2.FONT_HERSHEY_SIMPLEX, font_scale=2, color=(255, 255, 255), thickness=3, bg_color=(0, 0, 0)):
        self.width = width
        self.height = height
        self.text = text
        self.font = font
        self.font_scale = font_scale
        self.color = color
        self.thickness = thickness
        self.bg_color = bg_color
        self.image = np.zeros((height, width, 3), dtype=np.uint8)
        self.image[:] = bg_color
        self._draw_text()
        self._draw_circle()

    def _draw_text(self):
        text_size = cv2.getTextSize(self.text, self.font, self.font_scale, self.thickness)[0]
        text_x = (self.width - text_size[0]) // 2
        text_y = (self.height + text_size[1]) // 2
        cv2.putText(self.image, self.text, (text_x, text_y), self.font, self.font_scale, self.color, self.thickness)

    def _draw_circle(self):
        cv2.circle(self.image, (self.width // 2, self.height // 2+150), 50, (0, 0, 255
        ), 3)
    def _draw_random_circle(self):
        cv2.circle(self.image, (randint(0, self.width), randint(0,self.height)), 50, (randint(0,255), randint(0,255), randint(0,255)
        ), 3)
    def show(self, window_name="Loading"):
        cv2.imshow(window_name, self.image)
        cv2.waitKey(1)

    def close(self, window_name="Loading"):
        cv2.destroyWindow(window_name)

    def update(self, window_name="Loading"):
        self._draw_random_circle()
        self.show()
    def multiple_update(self, times, window_name="Loading"):
        for _ in range(times):
            self.update(window_name)