import pyautogui
import cv2
import numpy as np
import time
import random
from threading import Lock

class BotCore:
    def __init__(self, log_func):
        self.template = None
        self.template_gray = None
        self.w = 0
        self.h = 0
        self.threshold = 0.8

        self.stop_flag = True
        self.flag_lock = Lock()

        self.random_movement_enabled = True
        self.random_delay_min = 0.5
        self.random_delay_max = 2.0
        self.random_move_duration_min = 0.2
        self.random_move_duration_max = 0.5

        self.log = log_func

    def load_image(self, path):
        img = cv2.imread(path, cv2.IMREAD_UNCHANGED)
        if img is None:
            return False
        self.template = img
        self.template_gray = cv2.cvtColor(self.template, cv2.COLOR_BGR2GRAY)
        self.w, self.h = self.template_gray.shape[::-1]
        self.log(f"Loaded image: {path} ({self.w}x{self.h})")
        return True

    def find_and_click(self):
        if self.template_gray is None:
            return False

        screenshot = pyautogui.screenshot()
        screenshot_np = np.array(screenshot)
        screenshot_gray = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2GRAY)

        result = cv2.matchTemplate(screenshot_gray, self.template_gray, cv2.TM_CCOEFF_NORMED)
        loc = np.where(result >= self.threshold)

        for pt in zip(*loc[::-1]):
            pyautogui.moveTo(pt[0] + self.w // 2, pt[1] + self.h // 2)
            pyautogui.click()
            self.log(f"Clicked at {pt[0] + self.w // 2}, {pt[1] + self.h // 2}")
            return True
        return False

    def move_mouse_randomly(self):
        screen_width, screen_height = pyautogui.size()
        x = random.randint(0, screen_width)
        y = random.randint(0, screen_height)
        duration = random.uniform(self.random_move_duration_min, self.random_move_duration_max)
        pyautogui.moveTo(x, y, duration=duration)
        self.log(f"Moved mouse to {x}, {y} (random idle move, duration {duration:.2f}s)")

    def set_random_move_settings(self, delay_min, delay_max, duration_min, duration_max):
        self.random_delay_min = delay_min
        self.random_delay_max = delay_max
        self.random_move_duration_min = duration_min
        self.random_move_duration_max = duration_max

    def start(self, on_exit=None):
        import threading

        def bot_loop():
            while True:
                with self.flag_lock:
                    if self.stop_flag:
                        break
                found = self.find_and_click()
                if not found and self.random_movement_enabled:
                    self.move_mouse_randomly()
                    delay = random.uniform(self.random_delay_min, self.random_delay_max)
                    time.sleep(delay)
                else:
                    time.sleep(2)
            self.log("Bot thread exiting.")
            if on_exit:
                on_exit()

        with self.flag_lock:
            if not self.stop_flag:
                self.log("Bot is already running!")
                return False
            self.stop_flag = False

        self.thread = threading.Thread(target=bot_loop)
        self.thread.daemon = True
        self.thread.start()
        self.log("Bot started.")
        return True

    def stop(self):
        with self.flag_lock:
            self.stop_flag = True
        self.log("Bot stopped.")
