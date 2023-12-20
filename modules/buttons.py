import RPi.GPIO as GPIO # Import Raspberry Pi GPIO library
from modules.radio import playRadio, killMusic,playLulaby
from modules.soundvolume import volumeUp, volumeDown
import logging
import sys
import threading

GPIO.setwarnings(False) # Ignore warning for now
GPIO.setmode(GPIO.BCM) # Use BCM pin numbering
SLEEP=16
RESET=13
REPEAT=20
HR=5
MIN=6
TIM_SET=22
ALM_SET=21
def button_callback(channel):
    try:
        bName='UNKN'
        if (channel==SLEEP):
            bName='SLEEP'
            killMusic()
            action = threading.Thread(target=playRadio, args=('ns',))
            action.start()
        elif (channel==RESET):
            bName='RESET'
            killMusic()
            action = threading.Thread(target=playRadio, args=('357',))
            action.start()
        elif (channel==REPEAT):
            bName='REPEAT'
            killMusic()
        elif (channel==HR):
            bName='HR'
            killMusic()
            action = threading.Thread(target=playLulaby, args=('1',))
            action.start()
        elif (channel==MIN):
            bName='MIN'
            killMusic()
            action = threading.Thread(target=playLulaby, args=('2',))
            action.start()
        elif (channel==TIM_SET):
            bName='TIM_SET'
            volumeDown()
        elif (channel==ALM_SET):
            bName='ALM_SET'
            volumeUp()

        logging.info("Button "+bName+" was pushed for channel: " +str(channel))
        #print("Button "+bName+" was pushed for channel: " +str(channel))
    except:
        logging.error("Other error")
        err = str(sys.exc_info())
        logging.error("Error known as:",str(err))

def setupButtons():
    logging.debug("Starting init for buttons")
    logging.debug("Current mode "+str(GPIO.getmode()))
    logging.debug("Loop for buttons")
    buttons=[SLEEP,RESET,REPEAT,HR,MIN,TIM_SET,ALM_SET]
    #buttons=[SLEEP,RESET,REPEAT,HR,MIN,TIM_SET]
    for but in buttons:
        logging.info("Setup for button "+str(but))
        #print("Setup for button "+str(but))
        GPIO.setup(but, GPIO.IN, pull_up_down=GPIO.PUD_UP) 
        GPIO.add_event_detect(but,GPIO.FALLING,callback=button_callback, bouncetime=200) 
    logging.info("Loop for buttons DONE")
if __name__ == '__main__':
    setupButtons()
    message = input("Press enter to quit\n\n") # Run until someone presses enter
    GPIO.cleanup() # Clean up
