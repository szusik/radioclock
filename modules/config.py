import logging
# CONFIGURATION MODULE

#PINs FOR CLOCK DISPLAY
clockDIO = 26
clockCLK = 19
#PINs FOR TEMP DISPLAY
tempDIO = 17
tempCLK = 27
#PINs for TEMP SENSOR
dhtPIN = 23

#Weather API details
apikey = "c1b7c56b934a179d0eee7603d16ad0a8"
lat = "52.42254135407858"
lon = "13.536243826790663"

#files
basePath = "/opt/radioclock/radioclock"
rrdFile = basePath+"/temp-out.rrd"

#Settings for OLED display
oledRST = 24

def init():
    print("Config init")
    logging.info("Config initialized")
