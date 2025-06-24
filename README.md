# DetectBoss GUI

This repository provides a small tkinter GUI that repeatedly performs OCR on a screen region to detect messages about the appearance of a boss.

## Requirements

- Python 3.8+
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) installed at `C:\Program Files\Tesseract-OCR\tesseract.exe`
- The packages listed in `requirements.txt`

```bash
pip install -r requirements.txt
```

## Usage

Run the script and configure the following options before clicking **開始偵測**:

- **偵測區域** – Enter four numbers (x1, y1, x2, y2) or use the **拖曳設定** button to draw the region to capture.
- **按鈕區域** – Enter the coordinates of the button to click when the text is not found. You can also drag to select a region; the script will click the center.
- **偵測間隔(秒)** – How many seconds to wait between each OCR scan.
- **偵測文字** – Space separated keywords that must all appear for the boss to be detected.

The current mouse position is displayed at the top of the window to help determine coordinates.

During detection the program captures the specified region every interval and performs OCR using Traditional Chinese (`chi_tra`). When all keywords are found, a notification window appears and a system sound plays. Otherwise, the script clicks the configured button region to change channels.

Log messages display the OCR results and current status, including how many channel switches have occurred. Use **停止偵測** to end detection.
