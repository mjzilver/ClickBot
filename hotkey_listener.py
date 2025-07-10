from pynput import keyboard

class HotkeyListener:
    def __init__(self, stop_callback, log_func):
        self.stop_callback = stop_callback
        self.log = log_func

    def on_press(self, key):
        try:
            if key == keyboard.Key.f8:
                self.log("F8 pressed. Stopping bot.")
                self.stop_callback()
        except:
            pass

    def start(self):
        listener = keyboard.Listener(on_press=self.on_press)
        listener.daemon = True
        listener.start()
