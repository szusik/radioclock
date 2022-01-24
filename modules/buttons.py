import RPi.GPIO as GPIO # Import Raspberry Pi GPIO library
from radio import playRadio, killMusic,playLulaby
from soundvolume import getSoundVolume, setSoundVolume

def button_callback(channel):
    bName='UNKN'
    if (channel==SLEEP):
        bName='SLEEP'
    elif (channel==RESET):
        bName='RESET'
    elif (channel==REPEAT):
        bName='REPEAT'
    elif (channel==HR):
        bName='HR'
    elif (channel==MIN):
        bName='MIN'
    elif (channel==TIM_SET):
        bName='TIM_SET'
    elif (channel==ALM_SET):
        bName='ALM_SET'

    print("Button "+bName+" was pushed for channel: " +str(channel))
GPIO.setwarnings(False) # Ignore warning for now
GPIO.setmode(GPIO.BOARD) # Use physical pin numbering
SLEEP=36
RESET=33
REPEAT=38
HR=29
MIN=31
TIM_SET=15
ALM_SET=40
buttons=[SLEEP,RESET,REPEAT,HR,MIN,TIM_SET,ALM_SET]
for but in buttons:
    print("Setup for button "+str(but))
    GPIO.setup(but, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Set pin 10 to be an input pin and set initial value to be high
    GPIO.add_event_detect(but,GPIO.FALLING,callback=button_callback, bouncetime=200) # Setup event on pin 10 rising edge
message = input("Press enter to quit\n\n") # Run until someone presses enter
GPIO.cleanup() # Clean up
