from modules.stoppableThread import StoppableThread
import subprocess

def playRadio(id):
    command = "amixer -c 1 set Speaker"
    if id == 'ns':
        command += " 60% && mplayer -cache 1024 -nolirc http://stream.rcs.revma.com/ypqt40u0x1zuv"
    elif id == '357':
        command += " 70% && mplayer -cache 1024 -nolirc http://stream.rcs.revma.com/an1ugyygzk8uv"
    print("Trying to run"+command)
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
    command = "killall -9 mpv" #command to be executed
    try:
        res = subprocess.call(command, shell = True,stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError as e:
        print("Unable to stop playing")
    return
def playLulaby(id):
    command = "amixer -c 1 set Speaker"
    if id == '1':
        command += " 90% && mplayer /opt/music/ajde-jano.webm"
    elif id == '2':
        command += " 80% && mplayer /opt/music/ta-dorotka.webm"
    try:
        res = subprocess.call(command, shell = True,stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError as e:
        print("Unable to play lulaby")
    return