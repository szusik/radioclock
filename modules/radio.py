import subprocess
import modules.config as cfg

def playRadio(id):
    command = "amixer -c 1 set Speaker"
    if id == 'ns':
        command += " "+cfg.radio_1_vol+" && mplayer -cache 1024 -nolirc "+cfg.radio_1
    elif id == '357':
        command += " "+cfg.radio_2_vol+" && mplayer -cache 1024 -nolirc "+cfg.radio_2
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
        print("Unable to stop playing mplayer")
    command = "killall -9 mpv" #command to be executed
    try:
        res = subprocess.call(command, shell = True,stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError as e:
        print("Unable to stop playing mpv")
    return
def playLulaby(id):
    command = "amixer -c 1 set Speaker"
    if id == '1':
        command += " "+cfg.song_1_vol+" && mplayer "+cfg.song_1
    elif id == '2':
        command += " "+cfg.song_2_vol+" && mplayer "+cfg.song_2
    try:
        res = subprocess.call(command, shell = True,stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError as e:
        print("Unable to play lulaby")
    return
