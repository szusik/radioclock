import requests
import json
from requests.exceptions import HTTPError
import base64
import urllib.parse
import urllib3
import time
from time import sleep
import Adafruit_GPIO.SPI as SPI
import Adafruit_SSD1306
from modules.stoppableThread import StoppableThread

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import os.path
from os import path
import math
from modules.tm1637 import TM1637
from datetime import datetime as dt
import logging
import threading
import sys
import schedule

#Temperature 4-digit LED
tm = TM1637(clk=27, dio=17)

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
workerThread = None

def displayClear():
    global tm
    global disp
    # Clear display.
    disp.clear()
    disp.display()
    tm.write([0, 0, 0, 0])
    tm.brightness(0)

displayClear()
def getWeatherAsync():
    global workerThread
    try:
        logging.info("Working on weather")
        if workerThread is not None:
            workerThread.stop()
        workerThread = StoppableThread(target=getWeather)
        workerThread.start()
    except:
        logging.error("Other error - Async")
        err = str(sys.exc_info())
        logging.error("Error known as "+err)
        tm.show("UPS")
        sleep(1)
        displayText(str(err))
        print("Other error occurred:",str(err))

def getWeatherSched():
    try:
        logging.info("Calling scheduler for weather")
        getWeatherAsync()
        schedule.every(1).minutes.do(getWeatherAsync)
        while True:
            schedule.run_pending()
            sleep(1)
        logging.info("Calling scheduler for weather done")
    except:
        logging.error("Other error Sched")
        err = str(sys.exc_info())
        logging.error("Error known as "+err)
        tm.show("UPS")
        sleep(1)
        displayText(str(err))
        print("Other error occurred:",str(err))

def getWeather():
    global apikey
    global lat
    global lon
    global tm
    while True:
        try:
            logging.info("Preparing request for weather")
            if threading.current_thread().stopped():
                logging.info("Weather thread marked as stopped")
                break            
            #display question mark
            iconpath = "/opt/radioclock/radioclock/static/icons/0.png"
            icon = Image.open(iconpath)
            displayIconAtPos(60,icon,False)
            sleep(1)
            displayText("1...",False)
            sleep(1)
            #make a request for weather
            response = requests.get("https://api.openweathermap.org/data/2.5/onecall?lat="+lat+"&lon="+lon+"&appid="+apikey+"&units=metric&exclude=daily,minutely,hourly")
            # If the response was successful, no Exception will be raised
            displayText("2...",False)
            sleep(1)
            logging.info("Request for weather done")
            response.raise_for_status()
            displayText("3...",False)
            sleep(1)
            weather = json.loads(response.text)        
            temp = round(float(weather['current']['temp']))
            if(temp<-9):
                tm.show(str(temp)+"*")
            else:
                tm.temperature(temp)
            displayText("4...",False)
            displayIcon(weather['current']['weather'][0]['icon'])
        except:
            logging.error("Other error - main weather")
            err = str(sys.exc_info())
            logging.error("Error known as "+err)
            tm.show("UPS")
            sleep(1)
            displayText(str(err))
            print("Other error occurred:",str(err))  # Python 3.6           
            

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
        lastCall = now - inTimestamp
        minute = now.minute
        #print("Total seconds "+str(lastCall.total_seconds()))
        if minute % 10 == 0 and lastCall.total_seconds() > 60:
            break
        for x in range(0,width-32,10):        
            displayIconAtPos(x,icon)
        now = dt.now()
        lastCall = now - inTimestamp
        minute = now.minute
        #print("Total seconds "+str(lastCall.total_seconds()))
        if minute % 10 == 0 and lastCall.total_seconds() > 60:
            break
        if threading.current_thread().stopped():
            logging.info("Weather thread marked as stopped")
            break

def displayIconAtPos(x,icon,doSleep = True):
    global disp
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

def displayText(text,doScroll=True):
    global disp
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
        if doScroll != True:
            break 

#getWeather()
#displayIcon("01")
