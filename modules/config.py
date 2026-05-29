import logging
import json
import os
import traceback 
import sys
from logging import Logger
# CONFIGURATION MODULE

#PINs FOR CLOCK DISPLAY
clockDIO = 26
clockCLK = 19
#PINs FOR TEMP DISPLAY
tempDIO = 17
tempCLK = 27
#PINs for TEMP SENSOR
dhtPIN = 23

logfile="/var/log/radioclock.log"

#Weather API details
apikey = "PUT_YOUR_OWN_API_TOKEN"
lat = "0"
lon = "0"

#files
basePath = "/opt/radioclock/radioclock"
rrdFile = basePath+"/temp-out.rrd"

#Settings for OLED display
oledRST = 24

#Radio stations streams URL
radio_1 = "http://stream.rcs.revma.com/ypqt40u0x1zuv" # Radio Nowy Swiat
radio_2 = "http://stream.rcs.revma.com/an1ugyygzk8uv" # Radion 357
radio_1_vol = "60%"
radio_2_vol = "70%"

#Songs
song_1 = "/opt/music/song1.webm"
song_2 = "/opt/music/song2.webm"
song_1_vol = "90%"
song_2_vol = "80%"

def init():
    #define keys read from config file
    global apikey
    global lat
    global lon
    global basePath
    global rrdFile
    global logfile
    print("Config init")
    confFileName="config.json"
    try:
        if os.path.isfile(confFileName):
            confPath = os.path.abspath(confFileName)
            logging.info("Reading config at "+confPath)
            f = open(confPath)
            confdata = json.load(f)
            apikey = str(confdata['apikey'])
            logging.info("Got APIKEY "+apikey)
            lat = str(confdata['lat'])
            lon = str(confdata['lon'])
            if 'basePath' in confdata:
                basePath = str(confdata['basePath'])
                rrdFile = basePath + "/temp-out.rrd"
            if 'logfile' in confdata:
                logfile = str(confdata['logfile'])
        print("Log path "+str(logfile))
    except:
        logging.error("Reading config error")
        exc_type, exc_value, exc_traceback = sys.exc_info()
        err = traceback.format_tb(exc_traceback)
        logging.error("Error known as "+str(err))

    logging.info("Config initialized")


def logError(exc: Exception, logger: Logger, extras: str):
    try:
        if extras:
            logger.info(extras);
        exc_traceback = sys.exc_info()
        logger.error("Error: "+str(exc)+" file: "+str(exc.__traceback__.tb_frame)+":"+str(exc.__traceback__.tb_lineno))
    except:
        logger.error("Fallback error log: "+str(exc_traceback))