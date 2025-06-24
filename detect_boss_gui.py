import threading
import time
import tkinter as tk
from tkinter import messagebox, scrolledtext
from PIL import ImageGrab, ImageTk

import pytesseract
import pyautogui
import winsound


# Set tesseract command path
pytesseract.pytesseract.tesseract_cmd = r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"


class DetectBossApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Detect Boss")

        self.running = False
        self.switch_count = 0

        # Display mouse position
        self.pos_label = tk.Label(root, text="Mouse: (0, 0)")
        self.pos_label.pack()
        self.update_mouse_pos()

        # Detection region entries
        region_frame = tk.Frame(root)
        region_frame.pack(pady=5)
        tk.Label(region_frame, text="偵測區域 x1 y1 x2 y2:").pack(side=tk.LEFT)
        self.region_vars = [tk.StringVar(value=str(v)) for v in (500, 180, 1400, 280)]
        for var in self.region_vars:
            tk.Entry(region_frame, textvariable=var, width=5).pack(side=tk.LEFT)
        tk.Button(region_frame, text="拖曳設定", command=self.select_detection_region).pack(side=tk.LEFT, padx=5)

        # Button click region entries
        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=5)
        tk.Label(btn_frame, text="按鈕區域 x1 y1 x2 y2:").pack(side=tk.LEFT)
        self.btn_vars = [tk.StringVar(value=str(v)) for v in (1375, 655, 1375, 655)]
        for var in self.btn_vars:
            tk.Entry(btn_frame, textvariable=var, width=5).pack(side=tk.LEFT)
        tk.Button(btn_frame, text="拖曳設定", command=self.select_button_region).pack(side=tk.LEFT, padx=5)

        # Detection interval
        interval_frame = tk.Frame(root)
        interval_frame.pack(pady=5)
        tk.Label(interval_frame, text="偵測間隔(秒):").pack(side=tk.LEFT)
        self.interval_var = tk.StringVar(value="5")
        tk.Entry(interval_frame, textvariable=self.interval_var, width=5).pack(side=tk.LEFT)

        # Keywords
        keywords_frame = tk.Frame(root)
        keywords_frame.pack(pady=5)
        tk.Label(keywords_frame, text="偵測文字(以空白分隔):").pack(side=tk.LEFT)
        self.keywords_var = tk.StringVar(value="野生 菇菇王 出現")
        tk.Entry(keywords_frame, textvariable=self.keywords_var, width=30).pack(side=tk.LEFT)

        self.start_btn = tk.Button(root, text="開始偵測", command=self.start_detection)
        self.start_btn.pack(pady=5)

        self.stop_btn = tk.Button(root, text="停止偵測", command=self.stop_detection, state=tk.DISABLED)
        self.stop_btn.pack(pady=5)

        self.log_text = scrolledtext.ScrolledText(root, width=60, height=15, state=tk.DISABLED)
        self.log_text.pack(padx=10, pady=10)

    def log(self, message: str):
        self.log_text.configure(state=tk.NORMAL)
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.log_text.configure(state=tk.DISABLED)

    def update_mouse_pos(self):
        x, y = pyautogui.position()
        self.pos_label.config(text=f"Mouse: ({x}, {y})")
        self.root.after(100, self.update_mouse_pos)

    def select_region(self, callback):
        self.root.withdraw()
        screenshot = pyautogui.screenshot()
        top = tk.Toplevel()
        top.attributes('-fullscreen', True)
        canvas = tk.Canvas(top, width=screenshot.width, height=screenshot.height)
        canvas.pack(fill=tk.BOTH, expand=True)
        img = ImageTk.PhotoImage(screenshot)
        canvas.create_image(0, 0, image=img, anchor='nw')
        coords = {}
        rect = None

        def on_press(event):
            coords['x1'] = event.x
            coords['y1'] = event.y
            nonlocal rect
            rect = canvas.create_rectangle(event.x, event.y, event.x, event.y, outline='red')

        def on_move(event):
            if rect:
                canvas.coords(rect, coords['x1'], coords['y1'], event.x, event.y)

        def on_release(event):
            x1, y1 = coords['x1'], coords['y1']
            x2, y2 = event.x, event.y
            if x1 > x2:
                x1, x2 = x2, x1
            if y1 > y2:
                y1, y2 = y2, y1
            top.destroy()
            self.root.deiconify()
            callback(x1, y1, x2, y2)

        canvas.bind('<ButtonPress-1>', on_press)
        canvas.bind('<B1-Motion>', on_move)
        canvas.bind('<ButtonRelease-1>', on_release)
        top.grab_set()
        self.root.wait_window(top)

    def select_detection_region(self):
        def callback(x1, y1, x2, y2):
            values = [x1, y1, x2, y2]
            for var, val in zip(self.region_vars, values):
                var.set(str(int(val)))

        self.select_region(callback)

    def select_button_region(self):
        def callback(x1, y1, x2, y2):
            values = [x1, y1, x2, y2]
            for var, val in zip(self.btn_vars, values):
                var.set(str(int(val)))

        self.select_region(callback)

    def start_detection(self):
        if not self.running:
            self.detection_region = tuple(int(v.get()) for v in self.region_vars)
            self.button_region = tuple(int(v.get()) for v in self.btn_vars)
            try:
                self.interval = max(1, int(self.interval_var.get()))
            except ValueError:
                self.interval = 5
            self.keywords = [k for k in self.keywords_var.get().split() if k]

            self.running = True
            self.start_btn.configure(state=tk.DISABLED)
            self.stop_btn.configure(state=tk.NORMAL)
            self.log("開始偵測")
            threading.Thread(target=self.detect_loop, daemon=True).start()

    def stop_detection(self):
        if self.running:
            self.running = False
            self.start_btn.configure(state=tk.NORMAL)
            self.stop_btn.configure(state=tk.DISABLED)
            self.log("停止偵測")

    def detect_loop(self):
        while self.running:
            img = ImageGrab.grab(bbox=self.detection_region)
            text = pytesseract.image_to_string(img, lang='chi_tra')
            self.log(f"OCR: {text.strip()}")

            if all(k in text for k in self.keywords):
                self.log("發現王!")
                winsound.PlaySound('SystemExclamation', winsound.SND_ALIAS)
                messagebox.showinfo("通知", "偵測到菇菇王出現!")
            else:
                cx = (self.button_region[0] + self.button_region[2]) // 2
                cy = (self.button_region[1] + self.button_region[3]) // 2
                pyautogui.click(cx, cy)
                self.switch_count += 1
                self.log(f"未發現王，執行換頻 {self.switch_count} 次")

            for _ in range(self.interval):
                if not self.running:
                    break
                time.sleep(1)


if __name__ == '__main__':
    root = tk.Tk()
    app = DetectBossApp(root)
    root.mainloop()

