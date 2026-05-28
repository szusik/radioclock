import tkinter as tk
import threading
from PIL import Image

_SCALE = 4
_ON    = '#00cfff'   # cyan-blue, like a real OLED
_OFF   = '#000000'


class SSD1306_128_32:
    """Mock SSD1306 OLED that renders to a Tkinter window. Same API as real driver."""

    width  = 128
    height = 32

    def __init__(self, rst=None):
        self._image = Image.new('1', (self.width, self.height))
        self._dirty = False
        self._lock  = threading.Lock()
        self._ready = threading.Event()
        self._root  = None
        self._rects = []
        self._prev  = [None] * (self.width * self.height)

        t = threading.Thread(target=self._run_ui, daemon=True)
        t.start()
        self._ready.wait(timeout=3.0)

    def _run_ui(self):
        self._root = tk.Tk()
        self._root.title('SSD1306 OLED')
        self._root.configure(bg='#000000')
        self._root.resizable(False, False)

        W = self.width  * _SCALE
        H = self.height * _SCALE

        self._canvas = tk.Canvas(self._root, bg='#000000', width=W, height=H,
                                  highlightthickness=0)
        self._canvas.pack(padx=4, pady=4)

        # Pre-create one rectangle per OLED pixel — no PhotoImage involved
        for y in range(self.height):
            for x in range(self.width):
                r = self._canvas.create_rectangle(
                    x * _SCALE,       y * _SCALE,
                    (x + 1) * _SCALE, (y + 1) * _SCALE,
                    fill=_OFF, outline='')
                self._rects.append(r)

        self._ready.set()
        self._root.after(100, self._poll)
        self._root.mainloop()

    def _poll(self):
        with self._lock:
            dirty = self._dirty
            if dirty:
                img = self._image.copy()
                self._dirty = False

        if dirty:
            pixels = list(img.convert('L').getdata())  # 0 or 255 per pixel
            for i, p in enumerate(pixels):
                color = _ON if p else _OFF
                if color != self._prev[i]:
                    self._canvas.itemconfig(self._rects[i], fill=color)
                    self._prev[i] = color

        if self._root:
            self._root.after(100, self._poll)  # 10 fps

    def begin(self):
        pass

    def clear(self):
        with self._lock:
            self._image = Image.new('1', (self.width, self.height))
            self._dirty = True

    def image(self, img):
        with self._lock:
            self._image = img.copy()

    def display(self):
        with self._lock:
            self._dirty = True
