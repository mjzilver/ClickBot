import pyautogui
import cv2
import numpy as np
import time
import random
from threading import Lock

class BotCore:
    def __init__(self, log_func):
        self.templates = []
        self.template_grays = []
        self.template_sizes = [] 
        self.threshold = 0.8
        self.scaling_tolerance = 0.2
        self.last_click_time = 0
        self.delay = 1000

        self.stop_flag = True
        self.flag_lock = Lock()

        self.random_movement_enabled = True
        self.random_delay_min = 0.5
        self.random_delay_max = 2.0
        self.random_move_duration_min = 0.2
        self.random_move_duration_max = 0.5
        self.random_move_thread = None

        self.log = log_func 

    def capture_screenshot(self):
        return pyautogui.screenshot()

    def load_image(self, path):
        img = cv2.imread(path, cv2.IMREAD_UNCHANGED)
        if img is None:
            self.log(f"Failed to load image: {path}", color="red")
            return False

        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        w, h = img_gray.shape[::-1]

        self.templates.append(img)
        self.template_grays.append(img_gray)
        self.template_sizes.append((w, h))
        self.log(f"Loaded image: {path} ({w}x{h})")
        return True

    def find_and_click(self):
        screenshot = pyautogui.screenshot()
        screenshot_np = np.array(screenshot)
        screenshot_gray = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2GRAY)

        for index, template_gray in enumerate(self.template_grays):
            w, h = self.template_sizes[index]
            result = cv2.matchTemplate(screenshot_gray, template_gray, cv2.TM_CCOEFF_NORMED)
            loc = np.where(result >= self.threshold)

            for pt in zip(*loc[::-1]):
                click_x = pt[0] + w // 2
                click_y = pt[1] + h // 2
                pyautogui.moveTo(click_x, click_y)
                pyautogui.click()
                self.log(f"Clicked at {click_x}, {click_y} using template #{index}", color="green")
                return True

        return False

    def move_mouse_randomly(self):
        screen_width, screen_height = pyautogui.size()
        x = random.randint(0, screen_width)
        y = random.randint(0, screen_height)
        duration = random.uniform(self.random_move_duration_min, self.random_move_duration_max)
        pyautogui.moveTo(x, y, duration=duration)
        self.log(f"Moved mouse to {x}, {y} (random idle move, duration {duration:.2f}s)")
        
    def random_movement(self):
        while not self.stop_flag:
            if self.random_movement_enabled and (time.time() - self.last_click_time > self.random_delay_max):
                self.move_mouse_randomly()
                time.sleep(random.uniform(self.random_delay_min, self.random_delay_max))
            else:
                time.sleep(1)

    def start(self, on_exit=None):
        import threading

        def bot_loop():
            last_action_time = time.perf_counter()
            delay_secs = self.delay / 1000.0
            
            while True:
                with self.flag_lock:
                    if self.stop_flag:
                        break
                    
                now = time.perf_counter()
                elapsed = now - last_action_time
                
                if elapsed < delay_secs:
                    time.sleep(delay_secs - elapsed)
                    continue
                    
                found = self.find_and_click()
                if found:
                    last_action_time = now
                    self.last_click_time = time.time()

            self.log("Bot thread exiting.")
            if on_exit:
                on_exit()

        with self.flag_lock:
            if not self.stop_flag:
                self.log("Bot is already running")
                return False
            self.stop_flag = False

        self.thread = threading.Thread(target=bot_loop)
        self.thread.daemon = True
        self.thread.start()
        self.log("Bot started.")
        
        if self.random_movement_enabled:
            self.random_move_thread = threading.Thread(target=self.random_movement)
            self.random_move_thread.daemon = True
            self.random_move_thread.start()
        
        return True

    def stop(self):
        with self.flag_lock:
            self.stop_flag = True
        self.log("Bot stopping...")
