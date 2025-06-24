import threading
import time
import tkinter as tk
from tkinter import messagebox, scrolledtext

from PIL import ImageGrab
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

    def start_detection(self):
        if not self.running:
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
            # Capture screen region
            img = ImageGrab.grab(bbox=(500, 180, 1400, 280))
            text = pytesseract.image_to_string(img, lang='chi_tra')
            self.log(f"OCR: {text.strip()}")

            keywords = ['野生', '菇菇王', '出現']
            if all(k in text for k in keywords):
                self.log("發現王!")
                winsound.PlaySound('SystemExclamation', winsound.SND_ALIAS)
                messagebox.showinfo("通知", "偵測到菇菇王出現!")
            else:
                pyautogui.click(1375, 655)
                self.switch_count += 1
                self.log(f"未發現王，執行換頻 {self.switch_count} 次")

            for _ in range(5):
                if not self.running:
                    break
                time.sleep(1)


if __name__ == '__main__':
    root = tk.Tk()
    app = DetectBossApp(root)
    root.mainloop()

