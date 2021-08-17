import requests
import json
from requests.exceptions import HTTPError
import base64
import urllib.parse
import urllib3
import tm1637
import time
from time import sleep
import Adafruit_GPIO.SPI as SPI
import Adafruit_SSD1306

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import os.path
from os import path
import math

from datetime import datetime as dt

#Temperature 4-digit LED
tm = tm1637.TM1637(clk=27, dio=17)

apikey = "c1b7c56b934a179d0eee7603d16ad0a8"
lat = "52.42254135407858"
lon = "13.536243826790663"

#Settings for OLED display
# Raspberry Pi pin configuration:
RST = 24
DC = 23
SPI_PORT = 0
SPI_DEVICE = 0
# 128x32 display with hardware I2C:
disp = Adafruit_SSD1306.SSD1306_128_32(rst=RST)
disp.begin()
scrollspeed = 1
# Get display width and height.
width = disp.width
height = disp.height

# Clear display.
disp.clear()
disp.display()
tm.write([0, 0, 0, 0])
tm.brightness(0)
def getWeather():
    while True:
        try:
            iconpath = "/opt/radioclock/radioclock/static/icons/0.png"
            icon = Image.open(iconpath)
            displayIconAtPos(60,icon,False)
            response = requests.get("https://api.openweathermap.org/data/2.5/onecall?lat="+lat+"&lon="+lon+"&appid="+apikey+"&units=metric&exclude=daily,minutely,hourly")
            

            # If the response was successful, no Exception will be raised
            response.raise_for_status()
        except HTTPError as http_err:
            tm.show("UPS1")
            displayText(str(http_err))
            print("HTTP error occurred:",str(http_err))  # Python 3.6
        except Exception as err:
            tm.show("UPS2")
            displayText(str(err))
            print("Other error occurred:",str(err))  # Python 3.6
        else:
            weather = json.loads(response.text)        
            temp = round(float(weather['current']['temp']))
            if(temp<0):
                tm.show(str(temp)+"*")
            else:
                tm.temperature(temp)
            #print(weather)
            #print(temp)
            #print(weather['current']['weather'][0]['icon'])
            displayIcon(weather['current']['weather'][0]['icon'])

def displayIcon(kind):
    # Create image buffer.
    # Make sure to create image with mode '1' for 1-bit color.
    iconpath = "/opt/radioclock/radioclock/static/icons/"+kind+".png"

    if not path.exists(iconpath):
        iconpath = "/opt/radioclock/radioclock/static/icons/0.png"
    icon = Image.open(iconpath).convert('1')
    inTimestamp = dt.now()
    while True:
        for x in range(width-32,0,-10):        
            displayIconAtPos(x,icon)
        now = dt.now()
        lastCall = inTimestamp - now
        minute = now.minute
        if minute % 10 == 0 and lastCall.total_seconds > 60:
            break
        for x in range(0,width-32,10):        
            displayIconAtPos(x,icon)
        now = dt.now()
        lastCall = inTimestamp - now
        minute = now.minute
        if minute % 10 == 0 and lastCall.total_seconds > 60:
            break

def displayIconAtPos(x,icon,doSleep = True):
    image = Image.new('1', (width, height))
    # Create drawing object.
    draw = ImageDraw.Draw(image)
    draw.rectangle((0,0,width,height), outline=0, fill=0)        
    image.paste(icon, [x,0])
    # Display image.
    disp.image(image)
    disp.display()
    #print("Display at "+str(x))
    if doSleep: 
        sleep(scrollspeed)

def displayText(text):
    # Create image buffer.
    # Make sure to create image with mode '1' for 1-bit color.
    image = Image.new('1', (width, height))

    # Load default font.
    font = ImageFont.truetype("/opt/radioclock/radioclock/modules/VCR_OSD_MONO_1.001.ttf", 20)
    # Create drawing object.
    draw = ImageDraw.Draw(image)
    
    maxwidth, unused = draw.textsize(text, font=font)
    velocity = -2
    startpos = width
    pos = startpos
    while True:
        # Clear image buffer by drawing a black filled box.
        draw.rectangle((0,0,width,height), outline=0, fill=0)
        # Enumerate characters and draw them offset vertically based on a sine wave.
        x = pos
        for i, c in enumerate(text):
            # Stop drawing if off the right side of screen.
            if x > width:
                break
            # Calculate width but skip drawing if off the left side of screen.
            if x < -10:
                char_width, char_height = draw.textsize(c, font=font)
                x += char_width
                continue
            # Draw text.
            draw.text((x, 0), c, font=font, fill=255)
            # Increment x position based on chacacter width.
            char_width, char_height = draw.textsize(c, font=font)
            x += char_width
        # Draw the image buffer.
        disp.image(image)
        disp.display()
        # Move position for next frame.
        pos += velocity
        # Start over if text has scrolled completely off left side of screen.
        if pos < -maxwidth:
            pos = startpos
        # Pause briefly before drawing next frame.
        sleep(0.05)
        minute = dt.now().minute
        if minute % 5 == 0: #no more than 5 minutes - before next try
            break

getWeather()
#displayIcon("01")