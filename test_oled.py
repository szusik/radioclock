"""Quick visual test for the SSD1306 mock — run directly with python3 test_oled.py"""
from modules.ssd1306_mock import SSD1306_128_32
from PIL import Image, ImageDraw
from time import sleep

oled = SSD1306_128_32()

# Frame 1: border + text
img = Image.new('1', (128, 32), 0)
draw = ImageDraw.Draw(img)
draw.rectangle([0, 0, 127, 31], outline=1)
draw.text((8, 10), "OLED MOCK OK", fill=1)
oled.image(img)
oled.display()
sleep(2)

# Frame 2: scrolling bar
for x in range(0, 128, 4):
    img = Image.new('1', (128, 32), 0)
    draw = ImageDraw.Draw(img)
    draw.rectangle([x, 12, x + 16, 20], fill=1)
    oled.image(img)
    oled.display()
    sleep(0.05)

# Frame 3: weather icon
from os import path
iconpath = path.join(path.dirname(__file__), "static/icons/01d.png")
icon = Image.open(iconpath).convert('1')
img = Image.new('1', (128, 32), 0)
img.paste(icon, [48, 0])
oled.image(img)
oled.display()
sleep(3)
