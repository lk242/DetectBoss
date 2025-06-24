import threading
import time
import tkinter as tk
from tkinter import messagebox, scrolledtext
from PIL import ImageGrab, ImageTk

import pytesseract
import pyautogui
import winsound

# // 設定 tesseract 執行檔路徑
TESSERACT_CMD = r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD

# // 預設偵測區域
DEFAULT_DETECTION_REGION = (500, 180, 1400, 280)

# // 預設按鈕位置
DEFAULT_BUTTON_REGION = (1375, 655, 1375, 655)
# // 預設登入按鈕位置
DEFAULT_LOGIN_BUTTON_REGION = DEFAULT_BUTTON_REGION
# // 預設選角色按鈕位置
DEFAULT_CHAR_BUTTON_REGION = DEFAULT_BUTTON_REGION
# // 預設目錄按鈕位置
DEFAULT_MENU_BUTTON_REGION = DEFAULT_BUTTON_REGION
# // 預設隨機組隊按鈕位置
DEFAULT_RANDOM_BUTTON_REGION = DEFAULT_BUTTON_REGION
# // 預設確認按鈕位置
DEFAULT_CONFIRM_BUTTON_REGION = DEFAULT_BUTTON_REGION

# // 預設偵測間隔
DEFAULT_INTERVAL = "5"

# // 預設關鍵字
DEFAULT_KEYWORDS = "野生 菇菇王 出現"


class DetectBossApp:
    def __init__(self, iRoot: tk.Tk):
        self.root = iRoot
        self.root.title("Detect Boss")

        self.running = False
        self.switch_count = 0

        # // 顯示滑鼠座標
        self.pos_label = tk.Label(iRoot, text="Mouse: (0, 0)")
        self.pos_label.pack()
        self.update_mouse_pos()

        # // 偵測區域輸入框
        _region_frame = tk.Frame(iRoot)
        _region_frame.pack(pady=5)
        tk.Label(_region_frame, text="偵測區域 x1 y1 x2 y2:").pack(side=tk.LEFT)
        self.region_vars = [tk.StringVar(value=str(v)) for v in DEFAULT_DETECTION_REGION]
        for _var in self.region_vars:
            tk.Entry(_region_frame, textvariable=_var, width=5).pack(side=tk.LEFT)
        tk.Button(_region_frame, text="拖曳設定", command=self.select_detection_region).pack(side=tk.LEFT, padx=5)

        # // 登入按鈕設定
        self.login_btn_vars = self.create_button_inputs(iRoot, "登入", DEFAULT_LOGIN_BUTTON_REGION)
        # // 選角色按鈕設定
        self.char_btn_vars = self.create_button_inputs(iRoot, "選角色", DEFAULT_CHAR_BUTTON_REGION)
        # // 目錄按鈕設定
        self.menu_btn_vars = self.create_button_inputs(iRoot, "目錄", DEFAULT_MENU_BUTTON_REGION)
        # // 隨機組隊按鈕設定
        self.random_btn_vars = self.create_button_inputs(iRoot, "隨機組隊", DEFAULT_RANDOM_BUTTON_REGION)
        # // 確認按鈕設定
        self.confirm_btn_vars = self.create_button_inputs(iRoot, "確認", DEFAULT_CONFIRM_BUTTON_REGION)

        # // 偵測間隔設定
        _interval_frame = tk.Frame(iRoot)
        _interval_frame.pack(pady=5)
        tk.Label(_interval_frame, text="偵測間隔(秒):").pack(side=tk.LEFT)
        self.interval_var = tk.StringVar(value=DEFAULT_INTERVAL)
        tk.Entry(_interval_frame, textvariable=self.interval_var, width=5).pack(side=tk.LEFT)

        # // 關鍵字設定
        _keywords_frame = tk.Frame(iRoot)
        _keywords_frame.pack(pady=5)
        tk.Label(_keywords_frame, text="偵測文字(以空白分隔):").pack(side=tk.LEFT)
        self.keywords_var = tk.StringVar(value=DEFAULT_KEYWORDS)
        tk.Entry(_keywords_frame, textvariable=self.keywords_var, width=30).pack(side=tk.LEFT)

        self.start_btn = tk.Button(iRoot, text="開始偵測", command=self.start_detection)
        self.start_btn.pack(pady=5)

        self.stop_btn = tk.Button(iRoot, text="停止偵測", command=self.stop_detection, state=tk.DISABLED)
        self.stop_btn.pack(pady=5)

        self.log_text = scrolledtext.ScrolledText(iRoot, width=60, height=15, state=tk.DISABLED)
        self.log_text.pack(padx=10, pady=10)

    def log(self, message: str):
        self.log_text.configure(state=tk.NORMAL)
        _timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        self.log_text.insert(tk.END, f"[{_timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.log_text.configure(state=tk.DISABLED)

    def update_mouse_pos(self):
        _x, _y = pyautogui.position()
        self.pos_label.config(text=f"Mouse: ({_x}, {_y})")
        self.root.after(100, self.update_mouse_pos)

    def create_button_inputs(self, iRoot, iLabel, iDefault):
        # // 建立按鈕區域輸入框
        _frame = tk.Frame(iRoot)
        _frame.pack(pady=5)
        tk.Label(_frame, text=f"{iLabel} x1 y1 x2 y2:").pack(side=tk.LEFT)
        _vars = [tk.StringVar(value=str(v)) for v in iDefault]
        for _var in _vars:
            tk.Entry(_frame, textvariable=_var, width=5).pack(side=tk.LEFT)
        tk.Button(_frame, text="拖曳設定", command=lambda: self.select_button_region(_vars)).pack(side=tk.LEFT, padx=5)
        return _vars

    def select_region(self, iCallback):
        self.root.withdraw()
        _screenshot = pyautogui.screenshot()
        _top = tk.Toplevel()
        _top.attributes('-fullscreen', True)
        _canvas = tk.Canvas(_top, width=_screenshot.width, height=_screenshot.height)
        _canvas.pack(fill=tk.BOTH, expand=True)
        _img = ImageTk.PhotoImage(_screenshot)
        _canvas.create_image(0, 0, image=_img, anchor='nw')
        _coords = {}
        _rect = None

        def on_press(iEvent):
            _coords['x1'] = iEvent.x
            _coords['y1'] = iEvent.y
            nonlocal _rect
            _rect = _canvas.create_rectangle(iEvent.x, iEvent.y, iEvent.x, iEvent.y, outline='red')

        def on_move(iEvent):
            if _rect:
                _canvas.coords(_rect, _coords['x1'], _coords['y1'], iEvent.x, iEvent.y)

        def on_release(iEvent):
            _x1, _y1 = _coords['x1'], _coords['y1']
            _x2, _y2 = iEvent.x, iEvent.y
            if _x1 > _x2:
                _x1, _x2 = _x2, _x1
            if _y1 > _y2:
                _y1, _y2 = _y2, _y1
            _top.destroy()
            self.root.deiconify()
            iCallback(_x1, _y1, _x2, _y2)

        _canvas.bind('<ButtonPress-1>', on_press)
        _canvas.bind('<B1-Motion>', on_move)
        _canvas.bind('<ButtonRelease-1>', on_release)
        _top.grab_set()
        self.root.wait_window(_top)

    def select_detection_region(self):
        def _callback(iX1, iY1, iX2, iY2):
            _values = [iX1, iY1, iX2, iY2]
            for _var, _val in zip(self.region_vars, _values):
                _var.set(str(int(_val)))

        self.select_region(_callback)

    def select_button_region(self, iVars):
        def _callback(iX1, iY1, iX2, iY2):
            _values = [iX1, iY1, iX2, iY2]
            for _var, _val in zip(iVars, _values):
                _var.set(str(int(_val)))

        self.select_region(_callback)

    def click_center(self, iRegion):
        # // 點擊區域中心
        _cx = (iRegion[0] + iRegion[2]) // 2
        _cy = (iRegion[1] + iRegion[3]) // 2
        pyautogui.click(_cx, _cy)

    def start_detection(self):
        if not self.running:
            self.detection_region = tuple(int(_v.get()) for _v in self.region_vars)
            self.login_button = tuple(int(_v.get()) for _v in self.login_btn_vars)
            self.char_button = tuple(int(_v.get()) for _v in self.char_btn_vars)
            self.menu_button = tuple(int(_v.get()) for _v in self.menu_btn_vars)
            self.random_button = tuple(int(_v.get()) for _v in self.random_btn_vars)
            self.confirm_button = tuple(int(_v.get()) for _v in self.confirm_btn_vars)
            try:
                self.interval = max(1, int(self.interval_var.get()))
            except ValueError:
                self.interval = int(DEFAULT_INTERVAL)
            self.keywords = [_k for _k in self.keywords_var.get().split() if _k]

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
        _first = True
        while self.running:
            if _first:
                self.click_center(self.login_button)
                time.sleep(1)
                self.click_center(self.char_button)
                _first = False

            _img = ImageGrab.grab(bbox=self.detection_region)
            _text = pytesseract.image_to_string(_img, lang='chi_tra')
            self.log(f"OCR: {_text.strip()}")

            if all(_k in _text for _k in self.keywords):
                self.log("發現王!")
                winsound.PlaySound('SystemExclamation', winsound.SND_ALIAS)
                messagebox.showinfo("通知", "偵測到菇菇王出現!")
            else:
                self.click_center(self.menu_button)
                time.sleep(0.5)
                self.click_center(self.random_button)
                time.sleep(0.5)
                self.click_center(self.confirm_button)
                self.switch_count += 1
                self.log(f"未發現王，執行換頻 {self.switch_count} 次")

            for _ in range(self.interval):
                if not self.running:
                    break
                time.sleep(1)


if __name__ == '__main__':
    _root = tk.Tk()
    _app = DetectBossApp(_root)
    _root.mainloop()

