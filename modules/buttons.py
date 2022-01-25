import RPi.GPIO as GPIO # Import Raspberry Pi GPIO library
from modules.radio import playRadio, killMusic,playLulaby
from modules.soundvolume import volumeUp, volumeDown
import logging
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
    bName='UNKN'
    if (channel==SLEEP):
        bName='SLEEP'
        playRadio('ns')
    elif (channel==RESET):
        bName='RESET'
        playRadio('357')
    elif (channel==REPEAT):
        bName='REPEAT'
        killMusic()
    elif (channel==HR):
        bName='HR'
        playLulaby('1')
    elif (channel==MIN):
        bName='MIN'
        playLulaby('2')
    elif (channel==TIM_SET):
        bName='TIM_SET'
        volumeDown()
    elif (channel==ALM_SET):
        bName='ALM_SET'
        volumeUp()

    logging.info("Button "+bName+" was pushed for channel: " +str(channel))
    #print("Button "+bName+" was pushed for channel: " +str(channel))

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
