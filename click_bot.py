import pyautogui
import cv2
import numpy as np
import time
import random
from pynput import keyboard
import threading

template_path = 'image.png'
template = cv2.imread(template_path, cv2.IMREAD_UNCHANGED)
template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
w, h = template_gray.shape[::-1]

stop_flag = False

def on_press(key):
    global stop_flag
    try:
        if key == keyboard.Key.f8:
            print("F8 pressed. Stopping bot.")
            stop_flag = True
            return False 
    except:
        pass

def listen_for_hotkey():
    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()

def find_and_click():
    screenshot = pyautogui.screenshot()
    screenshot_np = np.array(screenshot)
    screenshot_gray = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2GRAY)

    result = cv2.matchTemplate(screenshot_gray, template_gray, cv2.TM_CCOEFF_NORMED)
    threshold = 0.8
    loc = np.where(result >= threshold)

    for pt in zip(*loc[::-1]):
        pyautogui.moveTo(pt[0] + w // 2, pt[1] + h // 2)
        pyautogui.click()
        print(f"Clicked at {pt[0] + w // 2}, {pt[1] + h // 2}")
        return True
    return False

def move_mouse_randomly():
    screen_width, screen_height = pyautogui.size()
    x = random.randint(0, screen_width)
    y = random.randint(0, screen_height)
    pyautogui.moveTo(x, y, duration=random.uniform(0.2, 0.5))
    print(f"Moved mouse to {x}, {y} (random idle move)")

listener_thread = threading.Thread(target=listen_for_hotkey)
listener_thread.daemon = True
listener_thread.start()

print("== Bot is running. Press F8 to stop. ==")

while not stop_flag:
    found = find_and_click()
    if not found:
        move_mouse_randomly()
        time.sleep(1)
    else:
        time.sleep(2)

print("Bot exited.")
