import subprocess

def getSoundVolume():    
    command = "/opt/radioclock/getSoundVolume.sh" #command to be executed
    volume = -1
    try:
        res = subprocess.check_output(command, shell = True, stderr=subprocess.DEVNULL)
        volume = float(res.decode("utf-8"))
    except subprocess.CalledProcessError as e:
        print("Unable to check sound volume")
    return volume

def setSoundVolume(volume):
    command = "amixer -c 1 set Speaker "+str(volume)+"%"
    rettext = "-1"
    try:
        res = subprocess.check_output(command, shell = True, stderr=subprocess.DEVNULL)
        rettext = res.decode("utf-8")
    except subprocess.CalledProcessError as e:
        print("Unable to set sound volume")
    return rettext