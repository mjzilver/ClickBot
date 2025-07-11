import tkinter as tk
from tkinter import filedialog
from tkinter.scrolledtext import ScrolledText
from bot_core import BotCore
from hotkey_listener import HotkeyListener
from datetime import datetime

class BotGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Click Bot")

        self.bot = BotCore(self.log)
        self.hotkey = HotkeyListener(self.stop_bot, self.log)

        self.create_widgets()
        self.hotkey.start()
        
        self.root.after(100, self.on_gui_ready)

    def create_widgets(self):
        main_frame = tk.Frame(self.root, padx=15, pady=15)
        main_frame.pack()

        # --- Image selection group ---
        image_frame = tk.LabelFrame(main_frame, text="Target Image", padx=10, pady=10)
        image_frame.pack(fill='x', pady=5)

        self.image_path_var = tk.StringVar()
        tk.Label(image_frame, text="Image Path:").grid(row=0, column=0, sticky="w")
        self.image_entry = tk.Entry(image_frame, textvariable=self.image_path_var, width=40, state='readonly')
        self.image_entry.grid(row=0, column=1, padx=5)
        upload_btn = tk.Button(image_frame, text="Upload Image", command=self.upload_image)
        upload_btn.grid(row=0, column=2, padx=5)

        # --- Bot control group ---
        control_frame = tk.LabelFrame(main_frame, text="Bot Controls", padx=10, pady=10)
        control_frame.pack(fill='x', pady=5)

        start_btn = tk.Button(control_frame, text="Start Bot", width=12, command=self.start_bot)
        start_btn.grid(row=0, column=0, padx=5, pady=5)
        stop_btn = tk.Button(control_frame, text="Stop Bot", width=12, command=self.stop_bot)
        stop_btn.grid(row=0, column=1, padx=5, pady=5)
        
        self.status_label = tk.Label(control_frame, text="Status: Not Running", fg="red")
        self.status_label.grid(row=0, column=2, padx=5, pady=5)

        tk.Label(control_frame, text="Matching Threshold:").grid(row=1, column=0, sticky="w", padx=5)
        self.threshold_var = tk.DoubleVar(value=self.bot.threshold)
        self.threshold_scale = tk.Scale(control_frame, from_=0.5, to=1.0, resolution=0.01, orient=tk.HORIZONTAL, variable=self.threshold_var, length=100)
        self.threshold_scale.grid(row=1, column=1, columnspan=2, sticky="w", padx=5)

        # --- Random movement settings group ---
        random_frame = tk.LabelFrame(main_frame, text="Random Idle Movement Settings", padx=10, pady=10)
        random_frame.pack(fill='x', pady=5)

        self.random_move_var = tk.BooleanVar(value=self.bot.random_movement_enabled)
        self.random_move_check = tk.Checkbutton(random_frame, text="Enable random idle movement", variable=self.random_move_var)
        self.random_move_check.pack(anchor="w")
        
        # --- Random Move Timing Section ---
        timing_frame = tk.Frame(random_frame)
        timing_frame.pack(fill='x', pady=(5, 10))

        tk.Label(timing_frame, text="Random Move Timing (s):", anchor='w').grid(row=0, column=0, columnspan=4, sticky='w', padx=5, pady=(0, 5))

        tk.Label(timing_frame, text="Delay Min:").grid(row=1, column=0, sticky="w", padx=(5, 2))
        self.delay_min_var = tk.DoubleVar(value=self.bot.random_delay_min)
        tk.Entry(timing_frame, textvariable=self.delay_min_var, width=6).grid(row=1, column=1, padx=(0, 10))

        tk.Label(timing_frame, text="Max:").grid(row=1, column=2, sticky="e", padx=(5, 2))
        self.delay_max_var = tk.DoubleVar(value=self.bot.random_delay_max)
        tk.Entry(timing_frame, textvariable=self.delay_max_var, width=6).grid(row=1, column=3, padx=(0, 5))

        tk.Label(timing_frame, text="Duration Min:").grid(row=2, column=0, sticky="w", padx=(5, 2))
        self.duration_min_var = tk.DoubleVar(value=self.bot.random_move_duration_min)
        tk.Entry(timing_frame, textvariable=self.duration_min_var, width=6).grid(row=2, column=1, padx=(0, 10))

        tk.Label(timing_frame, text="Max:").grid(row=2, column=2, sticky="e", padx=(5, 2))
        self.duration_max_var = tk.DoubleVar(value=self.bot.random_move_duration_max)
        tk.Entry(timing_frame, textvariable=self.duration_max_var, width=6).grid(row=2, column=3, padx=(0, 5))

        update_btn = tk.Button(random_frame, text="Update Settings", command=self.update_settings)
        update_btn.pack()

        # --- Hotkey info ---
        info_label = tk.Label(main_frame, text="Press F8 anytime to STOP the bot globally.", fg="blue")
        info_label.pack(pady=(10, 5))

        # --- Log box ---
        self.log_text = ScrolledText(main_frame, state='disabled', height=15, width=70)
        self.log_text.pack(pady=(0, 10))

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_gui_ready(self):
        default_image = "image.png"
        if self.bot.load_image(default_image):
            self.image_path_var.set(default_image)
        else:
            self.log(f"Failed to load default image: {default_image}", color="red")

    def log(self, msg, color=None):
        timestamp = datetime.now().strftime("[%H:%M:%S] ")
        self.log_text.configure(state='normal')
        if color:
            self.log_text.insert(tk.END, timestamp + msg + "\n", color)
            self.log_text.tag_config(color, foreground=color)
        else:
            self.log_text.insert(tk.END, timestamp + msg + "\n")
        self.log_text.see(tk.END)
        self.log_text.configure(state='disabled')

    def upload_image(self):
        path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.bmp"), ("All files", "*.*")]
        )
        if path:
            if self.bot.load_image(path):
                self.image_path_var.set(path)

    def start_bot(self):
        if self.bot.template_gray is None:
            self.log("Please upload a target image first.", color="red")
            return
        if not self.bot.stop_flag:
            self.log("Bot is already running.")
            return
        
        self.update_settings()
        started = self.bot.start(on_exit=self.on_bot_exit)
        if started:
            self.log("Bot started successfully.")
            self.status_label.config(text="Status: Running", fg="green")
        else:
            self.log("Failed to start bot.", color="red")
        
    def stop_bot(self):
        if self.bot.stop_flag:
            self.log("Bot is not running, no action taken.")
            return
        self.status_label.config(text="Status: Stopping...", fg="yellow")
        self.bot.stop()
        
    def on_bot_exit(self):
        self.log("Bot has exited.")
        self.status_label.config(text="Status: Not Running", fg="red")

    def update_settings(self):
        try:
            dmin = self.delay_min_var.get()
            dmax = self.delay_max_var.get()
            dur_min = self.duration_min_var.get()
            dur_max = self.duration_max_var.get()
            if dmin < 0 or dmax < 0 or dur_min < 0 or dur_max < 0:
                raise ValueError("Values must be non-negative.")
            if dmin > dmax:
                raise ValueError("Delay min must be <= max.")
            if dur_min > dur_max:
                raise ValueError("Duration min must be <= max.")
            self.bot.set_random_move_settings(dmin, dmax, dur_min, dur_max)
            
            self.bot.random_movement_enabled = self.random_move_var.get()
            self.bot.threshold = self.threshold_var.get()
            
            self.log("Bot settings updated successfully.")
        except Exception as e:
            self.log(f"Error updating settings: {e}", color="red")

    def on_closing(self):
        self.stop_bot()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = BotGUI(root)
    root.mainloop()
