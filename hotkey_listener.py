import time
from pynput import keyboard

class HotkeyListener:
    def __init__(self, stop_callback, screen_capture_callback, log_func):
        self.stop_callback = stop_callback
        self.screen_capture_callback = screen_capture_callback
        self.log = log_func

    def on_press(self, key):
        try:
            if key == keyboard.Key.f8:
                self.log("F8 pressed. Stopping bot.", color="blue")
                self.stop_callback()
            if key == keyboard.Key.f9:
                self.log("F9 pressed. Capturing screenshot.", color="blue")
                self.screen_capture_callback()
                time.sleep(0.1)  # debounce                
        except:
            pass

    def start(self):
        listener = keyboard.Listener(on_press=self.on_press)
        listener.daemon = True
        listener.start()
