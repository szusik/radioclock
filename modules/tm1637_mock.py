import tkinter as tk
import threading
from time import sleep

_SEGMENTS = bytearray(
    b'\x3F\x06\x5B\x4F\x66\x6D\x7D\x07\x7F\x6F\x77\x7C\x39\x5E\x79\x71\x3D\x76\x06\x1E\x76\x38\x55\x54\x3F\x73\x67'
    b'\x50\x6D\x78\x3E\x1C\x2A\x76\x6E\x5B\x00\x40\x63')


class TM1637Mock:
    """Mock TM1637 that renders to a Tkinter window. Same API as real driver."""

    _ON  = '#ff6600'
    _OFF = '#2a0c00'
    _BG  = '#0d0d0d'

    def __init__(self, clk=None, dio=None, brightness=7):
        self._brightness = brightness
        self._segments = [0, 0, 0, 0]
        self._lock = threading.Lock()
        self._ready = threading.Event()
        self._root = None

        t = threading.Thread(target=self._run_ui, daemon=True)
        t.start()
        self._ready.wait(timeout=3.0)

    def _run_ui(self):
        self._root = tk.Tk()
        self._root.title('TM1637 Display')
        self._root.configure(bg=self._BG)
        self._root.resizable(False, False)

        W, H = 56, 96      # digit width, height
        gap = 8
        colon_w = 20
        pad = 14
        canvas_w = pad * 2 + 4 * W + 3 * gap + colon_w
        canvas_h = H + pad * 2

        self._canvas = tk.Canvas(self._root, bg=self._BG, width=canvas_w,
                                  height=canvas_h, highlightthickness=0)
        self._canvas.pack()

        # digit x positions: [0] [1] COLON [2] [3]
        xs = [
            pad,
            pad + W + gap,
            pad + 2 * W + 2 * gap + colon_w,
            pad + 3 * W + 3 * gap + colon_w,
        ]
        y0 = pad

        self._digit_items = [self._draw_digit(x, y0, W, H) for x in xs]

        cx = pad + 2 * W + 2 * gap + colon_w // 2
        r = 5
        self._colon = [
            self._canvas.create_oval(cx-r, y0 + H//3 - r, cx+r, y0 + H//3 + r,
                                     fill=self._OFF, outline=''),
            self._canvas.create_oval(cx-r, y0 + 2*H//3 - r, cx+r, y0 + 2*H//3 + r,
                                     fill=self._OFF, outline=''),
        ]

        self._ready.set()
        self._poll()
        self._root.mainloop()

    def _draw_digit(self, x, y, W, H):
        c = self._canvas
        p = 4       # gap between segment ends
        t = 7       # segment thickness
        H2 = H // 2
        off = self._OFF
        # items ordered to match segment bits 0-6: a b c d e f g
        return [
            c.create_rectangle(x+p,   y,        x+W-p, y+t,          fill=off, outline=''),  # a top
            c.create_rectangle(x+W-t, y+p,      x+W,   y+H2-p,       fill=off, outline=''),  # b top-right
            c.create_rectangle(x+W-t, y+H2+p,   x+W,   y+H-p,        fill=off, outline=''),  # c bottom-right
            c.create_rectangle(x+p,   y+H-t,    x+W-p, y+H,          fill=off, outline=''),  # d bottom
            c.create_rectangle(x,     y+H2+p,   x+t,   y+H-p,        fill=off, outline=''),  # e bottom-left
            c.create_rectangle(x,     y+p,      x+t,   y+H2-p,       fill=off, outline=''),  # f top-left
            c.create_rectangle(x+p,   y+H2-t//2, x+W-p, y+H2+t//2,  fill=off, outline=''),  # g middle
        ]

    def _poll(self):
        with self._lock:
            segs = list(self._segments)

        for d, items in enumerate(self._digit_items):
            for bit, item in enumerate(items):
                on = bool(segs[d] & (1 << bit))
                self._canvas.itemconfig(item, fill=self._ON if on else self._OFF)

        colon_on = bool(segs[1] & 0x80)
        colon_color = self._ON if colon_on else self._OFF
        for dot in self._colon:
            self._canvas.itemconfig(dot, fill=colon_color)

        if self._root:
            self._root.after(100, self._poll)

    def brightness(self, val=None):
        if val is None:
            return self._brightness
        if not 0 <= val <= 7:
            raise ValueError("Brightness out of range")
        self._brightness = val

    def write(self, segments, pos=0):
        with self._lock:
            for i, seg in enumerate(segments):
                if pos + i < 4:
                    self._segments[pos + i] = seg

    @staticmethod
    def encode_digit(digit):
        return _SEGMENTS[digit & 0x0f]

    @staticmethod
    def encode_char(char):
        o = ord(char)
        if o == 32: return _SEGMENTS[36]
        if o == 42: return _SEGMENTS[38]
        if o == 45: return _SEGMENTS[37]
        if 65 <= o <= 90:  return _SEGMENTS[o - 55]
        if 97 <= o <= 122: return _SEGMENTS[o - 87]
        if 48 <= o <= 57:  return _SEGMENTS[o - 48]
        raise ValueError("Character out of range: {:d} '{:s}'".format(o, chr(o)))

    def encode_string(self, string):
        segments = bytearray(len(string))
        for i in range(len(string)):
            segments[i] = self.encode_char(string[i])
        return segments

    def hex(self, val):
        self.write(self.encode_string('{:04x}'.format(val & 0xffff)))

    def number(self, num):
        num = max(-999, min(num, 9999))
        self.write(self.encode_string('{0: >4d}'.format(num)))

    def numbers(self, num1, num2, colon=True):
        num1 = max(-9, min(num1, 99))
        num2 = max(-9, min(num2, 99))
        segments = self.encode_string('{0:0>2d}{1:0>2d}'.format(num1, num2))
        if colon:
            segments[1] |= 0x80
        self.write(segments)

    def temperature(self, num):
        if num < -9:
            self.show('lo')
        elif num > 99:
            self.show('hi')
        else:
            self.write(self.encode_string('{0: >2d}'.format(num)))
        self.write([_SEGMENTS[38], _SEGMENTS[12]], 2)

    def dec_temperature(self, num):
        if num < -9.9:
            self.write([0, 0, 0, 0])
            self.show('lo')
        elif num > 99.9:
            self.write([0, 0, 0, 0])
            self.show('hi')
        else:
            intval = abs(int(num / 1))
            if num == 0:
                seg1, seg2, seg3 = 0, self.encode_digit(0), self.encode_digit(0)
            elif num < 0:
                seg1 = 0x40
                seg2 = self.encode_digit(intval)
                try:
                    seg3 = self.encode_digit(int(str(num).split('.')[1][0]))
                except Exception:
                    seg3 = self.encode_digit(0)
            elif intval < 10:
                seg1 = 0
                seg2 = self.encode_digit(intval)
                try:
                    seg3 = self.encode_digit(int(str(num).split('.')[1][0]))
                except Exception:
                    seg3 = self.encode_digit(0)
            else:
                seg1 = self.encode_digit(int(intval / 10))
                seg2 = self.encode_digit(int(num - (int(intval / 10) * 10)))
                try:
                    seg3 = self.encode_digit(int(str(num).split('.')[1][0]))
                except Exception:
                    seg3 = self.encode_digit(0)
            segments = [seg1, seg2, seg3, _SEGMENTS[38]]
            segments[1] |= 0x80
            self.write(segments)

    def show(self, string, colon=False):
        segments = self.encode_string(string)
        if len(segments) > 1 and colon:
            segments[1] |= 128
        self.write(segments[:4])

    def scroll(self, string, delay=250):
        segments = string if isinstance(string, list) else self.encode_string(string)
        data = [0] * 8
        data[4:0] = list(segments)
        for i in range(len(segments) + 5):
            self.write(data[0 + i:4 + i])
            sleep(delay / 1000)


class TM1637DecimalMock(TM1637Mock):
    """Decimal-point variant — mirrors TM1637Decimal API."""

    def encode_string(self, string):
        segments = bytearray(len(string.replace('.', '')))
        j = 0
        for i in range(len(string)):
            if string[i] == '.' and j > 0:
                segments[j - 1] |= 0x80
                continue
            segments[j] = self.encode_char(string[i])
            j += 1
        return segments
