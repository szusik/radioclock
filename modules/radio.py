from modules.stoppableThread import StoppableThread,ExeContext
import subprocess

def playRadio():
    command = "/opt/radioclock/radio.sh" #command to be executed
    res = subprocess.call(command, shell = True,stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return

def killMusic():
    command = "killall -9 mplayer" #command to be executed
    res = subprocess.call(command, shell = True,stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return
def playLulaby():
    command = "mplayer /opt/music/ajde-jano.webm"
    res = subprocess.call(command, shell = True,stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return