import time
from pynput import keyboard

class HotkeyListener:
    def __init__(self, toggle_bot_callback, toggle_random_movement, log_func):
        self.toggle_bot_callback = toggle_bot_callback
        self.toggle_random_movement = toggle_random_movement
        self.log = log_func

    def on_press(self, key):
        try:
            if key == keyboard.Key.f8:
                self.log("F8 pressed. Stopping bot.", color="blue")
                self.toggle_bot_callback()
            if key == keyboard.Key.f9:
                self.log("F9 pressed. Toggling random movement.", color="blue")
                self.toggle_random_movement()
                        
        except:
            pass

    def start(self):
        listener = keyboard.Listener(on_press=self.on_press)
        listener.daemon = True
        listener.start()
