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

Run the script and use the **開始偵測** button to begin scanning. The program will capture the region `(500, 180, 1400, 280)` every five seconds and perform OCR using Traditional Chinese (`chi_tra`).

When the keywords `野生`, `菇菇王`, and `出現` are all found, a notification window will appear and a system sound will play. If the keywords are not found, the script will automatically click position `(1375, 655)` to change channels.

Log messages display the OCR results and current status, including how many channel switches have occurred.

Use **停止偵測** to end detection.
