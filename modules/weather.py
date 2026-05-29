import requests
import json
from requests.exceptions import HTTPError
import base64
import urllib.parse
import urllib3
import time
from time import sleep
from modules.stoppableThread import StoppableThread

from PIL import Image
import os.path
from os import path
import math
try:
    from modules.tm1637 import TM1637
except (ImportError, RuntimeError):
    from modules.tm1637_mock import TM1637Mock as TM1637

import logging
import threading
import sys
import schedule
import traceback
try:
    import rrdtool
except ImportError:
    class rrdtool:
        @staticmethod
        def create(*a, **kw): pass
        @staticmethod
        def update(*a, **kw): pass

try:
    import Adafruit_DHT
except ImportError:
    class Adafruit_DHT:
        DHT11 = 11
        @staticmethod
        def read_retry(sensor, pin):
            return (50.0, 22.0)
import csv
from flask import jsonify
import modules.config as cfg
from modules.oled_display import OledDisplay

DHT_SENSOR = Adafruit_DHT.DHT11

#Temperature 4-digit LED
tmTemp = TM1637(clk=cfg.tempCLK, dio=cfg.tempDIO)
tmTemp.brightness(0)

workerThread = None

def displayClear():
    global workerThread
    if workerThread is not None:
        logging.info("Requested stop of worker thread 1")
        workerThread.stop()
        workerThread.join()
    OledDisplay.get_instance().clear()
    tmTemp.write([0, 0, 0, 0])
    tmTemp.brightness(0)

def getWeatherAsync():
    global workerThread
    logger = logging.getLogger(threading.current_thread().name)
    try:
        logger.info("Working on weather thread")
        if workerThread is not None:
            logger.info("Requested stop of old worker thread")
            workerThread.stop()
            workerThread.join()
        workerThread = StoppableThread(target=getWeather)
        workerThread.start()
        logger.info("Working on weather thread " + workerThread.name + " done")
    except:
        logger.error("Other error - Async")
        exc_type, exc_value, exc_traceback = sys.exc_info()
        err = traceback.format_tb(exc_traceback)
        logger.error("Error known as " + str(err))
        tmTemp.show("UPS")
        OledDisplay.get_instance().show_message(str(err)[:30], duration=5)

def getWeatherSched():
    logger = logging.getLogger(threading.current_thread().name)
    try:
        logger.info("Calling scheduler for weather")
        getWeatherAsync()
        schedule.every(10).minutes.do(getWeatherAsync)
        while True:
            schedule.run_pending()
            sleep(1)
    except:
        logger.error("Other error Sched")
        exc_type, exc_value, exc_traceback = sys.exc_info()
        err = traceback.format_tb(exc_traceback)
        logger.error("Error known as " + str(err))
        tmTemp.show("UPS")
        OledDisplay.get_instance().show_message(str(err)[:30], duration=5)

def getWeather():
    oled = OledDisplay.get_instance()
    logger = logging.getLogger(threading.current_thread().name)
    logger.info("Got schedule for weather")
    try:
        if cfg.apikey == "PUT_YOUR_OWN_API_TOKEN":
            logger.info("Missing api weather token")
            tmTemp.show("TOKE")
            return
        # Show question-mark icon while loading
        iconpath = path.join(cfg.basePath, "static", "icons", "0.png")
        if path.exists(iconpath):
            oled.set_icon(Image.open(iconpath).convert('1'))
        tmTemp.show("1***")
        sleep(1)
        response = requests.get(
            "https://api.openweathermap.org/data/2.5/weather"
            "?lat=" + cfg.lat + "&lon=" + cfg.lon +
            "&appid=" + cfg.apikey + "&units=metric&exclude=daily,minutely,hourly")
        tmTemp.show("*1**")
        sleep(1)
        logger.info("Request for weather done")
        response.raise_for_status()
        tmTemp.show("**1*")
        sleep(1)
        weather = json.loads(response.text)
        temp = round(float(weather['main']['temp']))
        performRRDUpdateAsync(temp)
        tmTemp.show("***1")
        if temp < -9:
            tmTemp.show(str(temp) + "*")
        else:
            tmTemp.temperature(temp)
        # Set actual weather icon — OledDisplay takes over scrolling from here
        kind = weather['weather'][0]['icon']
        iconpath = path.join(cfg.basePath, "static", "icons", kind + ".png")
        if not path.exists(iconpath):
            iconpath = path.join(cfg.basePath, "static", "icons", "0.png")
        if path.exists(iconpath):
            oled.set_icon(Image.open(iconpath).convert('1'))
    except:
        tmTemp.show("UPS")
        logger.error("Other error - main weather")
        exc_type, exc_value, exc_traceback = sys.exc_info()
        err = traceback.format_tb(exc_traceback)
        logger.error("Error known as " + str(err))
        oled.show_message(str(err)[:30], duration=5)

def createRRDDB():
    rrdtool.create(
        cfg.rrdFile,
        "--start", "now",
        "--step", "600",
        "RRA:AVERAGE:0.5:1:1200",
        "RRA:AVERAGE:0.5:3:96",
        "RRA:AVERAGE:0.5:144:740",
        "DS:temp_in:GAUGE:1200:0:50",
        "DS:temp_out:GAUGE:1200:-30:50",
        "DS:humid:GAUGE:1200:0:100")

def performRRDUpdateAsync(temp_out):
    logger = logging.getLogger(threading.current_thread().name)
    try:
        logger.info("Working RRD thread")
        rrdThread = StoppableThread(target=performRRDUpdate, args=(temp_out,))
        rrdThread.start()
        logger.info("Working on RRD thread " + rrdThread.name + " done")
    except:
        logger.error("Other error - Async")
        exc_type, exc_value, exc_traceback = sys.exc_info()
        err = traceback.format_tb(exc_traceback)
        logger.error("Error known as " + str(err))

def performRRDUpdate(temp_out):
    humid, temp = getDHTReading()
    logging.debug("Temp={0:0.1f}*C Humidity={1:0.1f}%".format(temp, humid))
    if not path.isfile(cfg.rrdFile):
        createRRDDB()
    rrdtool.update(cfg.rrdFile, "N:%s:%s:%s" % (temp, temp_out, humid))
    writeTempHumidStats(temp, temp_out, humid)

def getDHTReading():
    global DHT_SENSOR
    return Adafruit_DHT.read_retry(DHT_SENSOR, cfg.dhtPIN)

def writeTempHumidStats(temp_in, temp_out, humid):
    try:
        with open(cfg.basePath + '/temp.csv', 'w', newline='') as csvfile:
            tempwriter = csv.writer(csvfile, delimiter=' ',
                            quotechar='|', quoting=csv.QUOTE_MINIMAL)
            tempwriter.writerow([temp_in, temp_out, humid])
    except:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        err = traceback.format_tb(exc_traceback)
        logging.error("Unable to write temp stats file " + str(err))

def getTempHumid():
    try:
        with open(cfg.basePath + '/temp.csv', newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=' ', quotechar='|')
            for row in reader:
                temp_in  = row[0]
                temp_out = row[1]
                humid    = row[2]
            return jsonify({'temp_in': str(temp_in), 'temp_out': str(temp_out), 'humid': str(humid)})
    except:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        err = traceback.format_tb(exc_traceback)
        logging.error("Unable to read temp stats file " + str(err))
        return jsonify({'temp_in': 0, 'temp_out': 0, 'humid': 0})
