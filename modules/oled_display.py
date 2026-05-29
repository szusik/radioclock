import threading
import logging
import os.path
from time import sleep, time

from PIL import Image, ImageDraw, ImageFont

try:
    import Adafruit_SSD1306
except ImportError:
    import modules.ssd1306_mock as Adafruit_SSD1306

import modules.config as cfg

_SCROLL_STEP  = 10
_SCROLL_PAUSE = 1.0   # seconds between icon scroll positions


class OledDisplay:
    """Singleton OLED display manager.

    Default content: weather icon scrolling back and forth.
    Call show_message(text, duration) to temporarily overlay text;
    the display reverts to the icon automatically after duration seconds.
    """

    _instance = None
    _instance_lock = threading.Lock()

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            with cls._instance_lock:
                if cls._instance is None:
                    cls._instance = OledDisplay()
        return cls._instance

    def __init__(self):
        self._hw = Adafruit_SSD1306.SSD1306_128_32(rst=cfg.oledRST)
        self._hw.begin()
        self.width  = self._hw.width
        self.height = self._hw.height

        self._lock      = threading.Lock()
        self._icon      = None    # PIL Image mode '1', default content
        self._message   = None    # temporary text overlay
        self._msg_until = 0.0     # epoch time when message expires
        self._interrupt = threading.Event()

        t = threading.Thread(target=self._run, daemon=True)
        t.start()

    # ------------------------------------------------------------------ public

    def set_icon(self, icon):
        """Update the weather icon shown as default content."""
        with self._lock:
            self._icon = icon.copy() if icon is not None else None
        self._interrupt.set()

    def show_message(self, text, duration=3):
        """Overlay scrolling text for `duration` seconds, then revert to icon."""
        with self._lock:
            self._message   = text
            self._msg_until = time() + duration
        self._interrupt.set()

    def clear(self):
        """Blank the display and stop all content."""
        with self._lock:
            self._icon    = None
            self._message = None
        self._interrupt.set()
        self._render(Image.new('1', (self.width, self.height)))

    # ----------------------------------------------------------------- private

    def _in_message(self):
        with self._lock:
            return bool(self._message) and time() < self._msg_until

    def _run(self):
        while True:
            try:
                self._interrupt.clear()
                if self._in_message():
                    with self._lock:
                        text = self._message
                    self._scroll_text(text)
                else:
                    with self._lock:
                        icon = self._icon
                    if icon is not None:
                        self._scroll_icon(icon)
                    else:
                        self._interrupt.wait(timeout=1.0)
            except Exception:
                logging.exception("OledDisplay error")
                sleep(1)

    def _interruptible_sleep(self, seconds):
        """Sleep up to `seconds`; return True if interrupted early."""
        end = time() + seconds
        while time() < end:
            if self._interrupt.is_set() or self._in_message():
                return True
            sleep(0.05)
        return False

    def _render(self, img):
        self._hw.image(img)
        self._hw.display()

    def _scroll_icon(self, icon):
        for x_range in (range(self.width - 32, 0, -_SCROLL_STEP),
                        range(0, self.width - 32, _SCROLL_STEP)):
            for x in x_range:
                if self._interrupt.is_set() or self._in_message():
                    return
                img = Image.new('1', (self.width, self.height))
                img.paste(icon, [x, 0])
                self._render(img)
                if self._interruptible_sleep(_SCROLL_PAUSE):
                    return

    def _scroll_text(self, text):
        fontpath = os.path.join(cfg.basePath, 'modules', 'VCR_OSD_MONO_1.001.ttf')
        try:
            font = ImageFont.truetype(fontpath, 20)
        except Exception:
            font = ImageFont.load_default()

        img  = Image.new('1', (self.width, self.height))
        draw = ImageDraw.Draw(img)

        try:
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
        except AttributeError:
            text_width, _ = draw.textsize(text, font=font)  # Pillow < 9.2

        pos = self.width
        while self._in_message():
            draw.rectangle((0, 0, self.width, self.height), fill=0)
            draw.text((pos, 0), text, font=font, fill=255)
            self._render(img)
            pos -= 2
            if pos < -text_width:
                pos = self.width
            sleep(0.03)
