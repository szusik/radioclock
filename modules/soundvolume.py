import subprocess

def getSoundVolume():    
    command = "/opt/radioclock/getSoundVolume.sh" #command to be executed
    res = subprocess.check_output(command, shell = True, stderr=subprocess.DEVNULL)
    return float(res.decode("utf-8"))

def setSoundVolume(volume):
    command = "amixer -c 1 set Speaker "+str(volume)+"%"
    res = subprocess.check_output(command, shell = True, stderr=subprocess.DEVNULL)
    return res.decode("utf-8")