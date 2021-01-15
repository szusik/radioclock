from modules.stoppableThread import StoppableThread,ExeContext
import subprocess

def playRadio():
    command = "/opt/radioclock/radio.sh" #command to be executed
    try:
        res = subprocess.call(command, shell = True,stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError as e:
        print("Unable to play radio")
    return

def killMusic():
    command = "killall -9 mplayer" #command to be executed
    try:
        res = subprocess.call(command, shell = True,stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError as e:
        print("Unable to stop playing")
    return
def playLulaby():
    command = "amixer -c 1 set Speaker 70%; mplayer /opt/music/ajde-jano.webm"
    try:
        res = subprocess.call(command, shell = True,stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError as e:
        print("Unable to play lulaby")
    return