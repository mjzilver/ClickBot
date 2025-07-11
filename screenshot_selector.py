import tkinter as tk
from PIL import ImageTk, Image
from datetime import datetime

class ScreenshotSelector:
    def __init__(self, root, screenshot, log_callback, load_image_callback):
        self.root = root
        self.screenshot = screenshot
        self.log = log_callback
        self.load_image = load_image_callback

        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        self.max_size = (1024, 768)
        self.orig_size = self.screenshot.size
        self.scale_w = min(self.max_size[0] / self.orig_size[0], 1)
        self.scale_h = min(self.max_size[1] / self.orig_size[1], 1)

        self.display_size = (int(self.orig_size[0] * self.scale_w), int(self.orig_size[1] * self.scale_h))
        self.display_screenshot = self.screenshot.resize(self.display_size, Image.Resampling.LANCZOS)

        self.selection = {"x0": None, "y0": None, "x1": None, "y1": None, "rect": None}

        self.create_selection_window()

    def create_selection_window(self):
        self.sel_win = tk.Toplevel(self.root)
        self.sel_win.title("Select Template Region")

        self.img = ImageTk.PhotoImage(self.display_screenshot)
        self.canvas = tk.Canvas(self.sel_win, width=self.display_size[0], height=self.display_size[1])
        self.canvas.pack()
        self.canvas.image = self.img  # Keep reference
        self.canvas.create_image(0, 0, anchor="nw", image=self.img)

        self.canvas.bind("<Button-1>", self.on_mouse_down)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_up)

        btn = tk.Button(self.sel_win, text="Confirm Selection", command=self.confirm_selection)
        btn.pack(pady=5)

    def on_mouse_down(self, event):
        self.selection["x0"], self.selection["y0"] = event.x, event.y
        if self.selection["rect"]:
            self.canvas.delete(self.selection["rect"])
        self.selection["rect"] = self.canvas.create_rectangle(event.x, event.y, event.x, event.y, outline="red")

    def on_mouse_drag(self, event):
        self.selection["x1"], self.selection["y1"] = event.x, event.y
        self.canvas.coords(self.selection["rect"], self.selection["x0"], self.selection["y0"], event.x, event.y)

    def on_mouse_up(self, event):
        self.selection["x1"], self.selection["y1"] = event.x, event.y

    def confirm_selection(self):
        try:
            x0 = self.selection["x0"]
            y0 = self.selection["y0"]
            x1 = self.selection["x1"]
            y1 = self.selection["y1"]

            if None in (x0, y0, x1, y1):
                self.log("No region selected.", color="red")
                return

            left = int(min(x0, x1) / self.scale_w)
            upper = int(min(y0, y1) / self.scale_h)
            right = int(max(x0, x1) / self.scale_w)
            lower = int(max(y0, y1) / self.scale_h)

            cropped = self.screenshot.crop((left, upper, right, lower))
            crop_filename = f"captures/template_{self.timestamp}.png"
            cropped.save(crop_filename)

            self.log(f"Template region saved as {crop_filename}.", color="blue")
            self.sel_win.destroy()

            if self.load_image(crop_filename):
                pass
            else:
                self.log("Failed to load template image.", color="red")

        except Exception as e:
            self.log(f"Error during template selection: {e}", color="red")
