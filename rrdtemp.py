#!/usr/bin/python3

import rrdtool
import os.path
import sys
import Adafruit_DHT


DHT_SENSOR = Adafruit_DHT.DHT11

rrd_file = "/opt/radioclock/radioclock/temp.rrd"
DHT_PIN = 23

def createRRDDB():
    global rrd_file
    rrdtool.create(
        rrd_file,
        "--start", "now",
        "--step", "300",
        "RRA:AVERAGE:0.5:1:1200", #co 5 min 4 dni
        "RRA:AVERAGE:0.5:6:96", # co 30 min 2 dni
        "RRA:AVERAGE:0.5:288:740", # co 1 dzien , 740 dni
        "DS:temp:GAUGE:600:0:50",
        "DS:humid:GAUGE:600:0:100")

def testRRDDBExists():
    return os.path.isfile(rrd_file)

def performUpdate():
    humid, temp = getDHTReading()
    print("Temp={0:0.1f}*C Humidity={1:0.1f}%".format(temp, humid))
    if not testRRDDBExists():
        createRRDDB()
    rrdtool.update(rrd_file,"N:%s:%s" %(temp, humid))

def getDHTReading():
    global DHT_PIN
    global DHT_SENSOR
    return  Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)

if __name__ == '__main__':
    try:
        performUpdate()
    except:
        err = str(sys.exc_info())
        print("Got rrd update error known as: "+str(err))
    finally:
        print("Update done")
