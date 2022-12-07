import subprocess
import sys

def getSoundVolume():    
    command = "/opt/radioclock/getSoundVolume.sh" #command to be executed
    volume = -1
    try:
        res = subprocess.check_output(command, shell = True, stderr=subprocess.DEVNULL)
        volume = float(res.decode("utf-8"))
    except:
        err = str(sys.exc_info())
        logging.error("Volume error known as "+err)
    return volume

def setSoundVolume(volume):
    command = "amixer -c 1 set Speaker "+str(volume)+"%"
    rettext = "-1"
    try:
        res = subprocess.check_output(command, shell = True, stderr=subprocess.DEVNULL)
        rettext = res.decode("utf-8")
        logger.info("Set volume level "+ rettext)
        return volume
    except:
        err = str(sys.exc_info())
        logging.error("Volume error known as "+err)
    return "-1"

def volumeDown():
    volume = getSoundVolume()
    volume -= 10
    if volume<0:
      volume = 0
    return setSoundVolume(volume)

def volumeUp():
    volume = getSoundVolume()
    volume += 10
    if volume>100:
      volume = 100
    return setSoundVolume(volume)