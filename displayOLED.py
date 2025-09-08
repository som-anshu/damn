# displayOLED.py
# Display translated text from main.py on SSD1306 OLED using Adafruit CircuitPython library

import time
import threading
import queue
from board import SCL, SDA
import busio
from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306

# Import your translation logic from main.py (optional fallback)
try:
    from main import get_translated_text  # This function should return the translated text as a string
except ImportError:
    def get_translated_text():
        return "Hello, World!\nThis is a translated message."

disp = None
_draw = None
_font = None
_oled_queue = queue.Queue()
_oled_thread = None

def _oled_worker():
    global disp, _draw, _font
    while True:
        text = _oled_queue.get()
        if text is None:
            break
        # Draw text
        image = Image.new("1", (disp.width, disp.height))
        draw = ImageDraw.Draw(image)
        font = _font
        # Split text into lines that fit the display width
        lines = []
        max_width = disp.width
        words = text.split()
        line = ""
        for word in words:
            test_line = line + word + " "
            if draw.textlength(test_line, font=font) <= max_width:
                line = test_line
            else:
                lines.append(line)
                line = word + " "
        lines.append(line)
        draw.rectangle((0, 0, disp.width, disp.height), outline=0, fill=0)
        for i, l in enumerate(lines[:5]):
            draw.text((0, i * 12), l.strip(), font=font, fill=255)
        disp.image(image)
        disp.show()
        _oled_queue.task_done()

def init_oled():
    global disp, _draw, _font, _oled_thread
    if disp is None:
        i2c = busio.I2C(SCL, SDA)
        disp = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c, addr=0x3C)
        disp.fill(0)
        disp.show()
        try:
            _font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
        except IOError:
            _font = ImageFont.load_default()
        _oled_thread = threading.Thread(target=_oled_worker, daemon=True)
        _oled_thread.start()

def display_text_on_oled(text):
    init_oled()
    # Put text in the queue for the background thread to display
    _oled_queue.put(text)

if __name__ == "__main__":
    translated_text = get_translated_text()
    display_text_on_oled(translated_text)
    # Wait a bit to see the result
    time.sleep(5)
    # Clean up
    _oled_queue.put(None)
    if _oled_thread:
        _oled_thread.join()
