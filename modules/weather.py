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
import traceback 
import rrdtool
import Adafruit_DHT
import csv
from flask import jsonify
import modules.config as cfg

DHT_SENSOR = Adafruit_DHT.DHT11

#Temperature 4-digit LED
tmTemp = TM1637(clk=cfg.tempCLK, dio=cfg.tempDIO)
tmTemp.brightness(0)

# 128x32 display with hardware I2C:
dOled = Adafruit_SSD1306.SSD1306_128_32(rst=cfg.oledRST)
dOled.begin()
scrollspeed = 1
# Get display width and height.
width = dOled.width
height = dOled.height
workerThread = None

def displayClear():
    global tmTemp
    global dOled
    global workerThread
    if workerThread is not None:
        logging.info("Requested stop of worker thread 1")
        workerThread.stop()
        workerThread.join()
    # Clear display.
    dOled.clear()
    dOled.display()
    tmTemp.write([0, 0, 0, 0])
    tmTemp.brightness(0)    

#displayClear()
def getWeatherAsync():
    global workerThread
    global tmTemp
    try:
        logging.info("Working on weather")
        if workerThread is not None:
            logging.info("Requested stop of worker thread 1")
            workerThread.stop()
            workerThread.join()
        workerThread = StoppableThread(target=getWeather)
        workerThread.start()
    except:
        logging.error("Other error - Async")
        exc_type, exc_value, exc_traceback = sys.exc_info()
        err = traceback.format_tb(exc_traceback)
        logging.error("Error known as "+str(err))
        tmTemp.show("UPS")
        sleep(1)
        displayText(str(err))

def getWeatherSched():
    global tmTemp
    try:
        logging.info("Calling scheduler for weather")
        getWeatherAsync()
        schedule.every(10).minutes.do(getWeatherAsync)
        while True:
            schedule.run_pending()
            sleep(1)
        logging.info("Calling scheduler for weather done")
    except:
        logging.error("Other error Sched")
        exc_type, exc_value, exc_traceback = sys.exc_info()
        err = traceback.format_tb(exc_traceback)
        logging.error("Error known as "+str(err))
        tmTemp.show("UPS")
        sleep(1)
        displayText(str(err))
        print("Other error occurred:",str(err))

def getWeather():
    global tmTemp
    while not threading.current_thread().stopped():
        try:
            logging.info("Preparing request for weather")
            if threading.current_thread().stopped():
                logging.info("Weather thread marked as stopped 1")
                break
            if cfg.apikey == "PUT_YOUR_OWN_API_TOKEN":
                logging.info("Missing api weahter token")
                tmTemp.show("TOKE")
                break
            logging.info("TOKEN "+cfg.apikey)          
            #display question mark
            iconpath = cfg.basePath+"/static/icons/0.png"
            icon = Image.open(iconpath)
            displayIconAtPos(60,icon,False)
            sleep(1)
            tmTemp.show("1***")
            sleep(1)
            #make a request for weather
            response = requests.get("https://api.openweathermap.org/data/2.5/onecall?lat="+cfg.lat+"&lon="+cfg.lon+"&appid="+cfg.apikey+"&units=metric&exclude=daily,minutely,hourly")
            # If the response was successful, no Exception will be raised
            tmTemp.show("*1**")
            sleep(1)
            logging.info("Request for weather done")
            response.raise_for_status()
            tmTemp.show("**1*")
            sleep(1)
            weather = json.loads(response.text)
            temp = round(float(weather['current']['temp']))
            performRRDUpdate(temp)
            tmTemp.show("***1")
            if(temp<-9):
                tmTemp.show(str(temp)+"*")
            else:
                tmTemp.temperature(temp)
            displayIcon(weather['current']['weather'][0]['icon'])
        except:
            tmTemp.show("UPS")
            logging.error("Other error - main weather")
            exc_type, exc_value, exc_traceback = sys.exc_info()
            err = traceback.format_tb(exc_traceback)
            logging.error("Error known as "+str(err))            
            sleep(1)
            displayText(str(err))
            print("Other error occurred:",str(err))  # Python 3.6           
            

def displayIcon(kind):
    # Create image buffer.
    # Make sure to create image with mode '1' for 1-bit color.
    iconpath = cfg.basePath+"/static/icons/"+kind+".png"

    if not path.exists(iconpath):
        iconpath = cfg.basePath+"/static/icons/0.png"
    icon = Image.open(iconpath).convert('1')
    inTimestamp = dt.now()
    while not threading.current_thread().stopped():
        for x in range(width-32,0,-10):        
            displayIconAtPos(x,icon)
        now = dt.now()
        lastCall = now - inTimestamp
        minute = now.minute
        #print("Total seconds "+str(lastCall.total_seconds()))
        #if minute % 10 == 0 and lastCall.total_seconds() > 60:
        #    break
        for x in range(0,width-32,10):        
            displayIconAtPos(x,icon)
        now = dt.now()
        lastCall = now - inTimestamp
        minute = now.minute
        #print("Total seconds "+str(lastCall.total_seconds()))
        #if minute % 10 == 0 and lastCall.total_seconds() > 60:
        #    break
        if threading.current_thread().stopped():
            logging.info("Weather thread marked as stopped 2")
            break

def displayIconAtPos(x,icon,doSleep = True):
    if threading.current_thread().stopped():
        logging.info("Weather thread marked as stopped 3")
    else:
        global dOled
        image = Image.new('1', (width, height))
        # Create drawing object.
        draw = ImageDraw.Draw(image)
        draw.rectangle((0,0,width,height), outline=0, fill=0)        
        image.paste(icon, [x,0])
        # display image.
        dOled.image(image)
        dOled.display()
        #print("display at "+str(x))
        if doSleep: 
            sleep(scrollspeed)

def displayText(text,doScroll=True):
    global dOled
    # Create image buffer.
    # Make sure to create image with mode '1' for 1-bit color.
    image = Image.new('1', (width, height))

    # Load default font.
    font = ImageFont.truetype(cfg.basePath+"/modules/VCR_OSD_MONO_1.001.ttf", 20)
    # Create drawing object.
    draw = ImageDraw.Draw(image)
    
    maxwidth, unused = draw.textsize(text, font=font)
    velocity = -2
    startpos = width
    pos = startpos
    while True:
        # check if we are allowed
        if threading.current_thread().stopped():
            logging.info("Weather thread marked as stopped 4")
            break
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
        dOled.image(image)
        dOled.display()
        # Move position for next frame.
        pos += velocity
        # Start over if text has scrolled completely off left side of screen.
        if pos < -maxwidth:
            pos = startpos
        # Pause briefly before drawing next frame.
        sleep(0.03)
        minute = dt.now().minute
        if minute % 5 == 0: #no more than 5 minutes - before next try
            break
        if not doScroll:
            break 

#getWeather()
#displayIcon("01")
def createRRDDB():
    rrdtool.create(
        cfg.rrdFile,
        "--start", "now",
        "--step", "600",
        "RRA:AVERAGE:0.5:1:1200", #co 10 (1xstep) min 4 dni
        "RRA:AVERAGE:0.5:3:96", # co 30 min 2 dni
        "RRA:AVERAGE:0.5:144:740", # co 1 dzien , 740 dni
        "DS:temp_in:GAUGE:1200:0:50",
        "DS:temp_out:GAUGE:1200:-30:50",
        "DS:humid:GAUGE:1200:0:100")

def performRRDUpdate(temp_out):
    humid, temp = getDHTReading()
    logging.debug("Temp={0:0.1f}*C Humidity={1:0.1f}%".format(temp, humid))
    if not path.isfile(cfg.rrdFile):
        createRRDDB()
    rrdtool.update(cfg.rrdFile,"N:%s:%s:%s" %(temp,temp_out,humid))
    writeTempHumidStats(temp,temp_out, humid)

def getDHTReading():
    global DHT_SENSOR
    return Adafruit_DHT.read_retry(DHT_SENSOR, cfg.dhtPIN)

def writeTempHumidStats(temp_in,temp_out, humid):
    try:
        with open(cfg.basePath+'/temp.csv', 'w',newline='') as csvfile:
            tempwriter = csv.writer(csvfile, delimiter=' ',
                            quotechar='|', quoting=csv.QUOTE_MINIMAL)
            tempwriter.writerow([temp_in,temp_out,humid])
    except:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        err = traceback.format_tb(exc_traceback)
        logging.error("Unable to write temp stats file "+str(err))

def getTempHumid():
    try:
        with open(cfg.basePath+'/temp.csv', newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=' ', quotechar='|')
            for row in reader:
                temp_in=row[0]
                temp_out=row[1]
                humid=row[2]
            return  jsonify({ 'temp_in': str(temp_in), 'temp_out': str(temp_out),'humid': str(humid) })
    except:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        err = traceback.format_tb(exc_traceback)
        logging.error("Unable to read temp stats file "+str(err))
        return jsonify({ 'temp_in': 0, 'temp_out': 0,'humid': 0 })
