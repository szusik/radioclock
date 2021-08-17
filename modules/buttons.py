import RPi.GPIO as GPIO # Import Raspberry Pi GPIO library
from time import sleep 

def button_callback(channel):
        print("Button was pushed!")

GPIO.setwarnings(False) # Ignore warning for now
GPIO.setmode(GPIO.BOARD) # Use physical pin numbering
GPIO.setup(22, GPIO.IN, pull_up_down=GPIO.PUD_UP)   

# Define a threaded callback function to run in another thread when events are detected  
def my_callback(channel):  
    if GPIO.input(22):     # if port 22 == 1  
        print("Rising edge detected on 22")
    else:                  # if port 22 != 1  
        print("Falling edge detected on 22")  
  
# when a changing edge is detected on port 22, regardless of whatever   
# else is happening in the program, the function my_callback will be run  
GPIO.add_event_detect(22, GPIO.BOTH, callback=my_callback)  
print("Program will finish after 30 seconds or if you press CTRL+C\n") 
print("Make sure you have a button connected, pulled down through 10k resistor" )
print("to GND and wired so that when pressed it connects"  )
print("GPIO port 25 (pin 22) to GND (pin 6) through a ~1k resistor\n")  
  
print("Also put a 100 nF capacitor across your switch for hardware debouncing"  )
print("This is necessary to see the effect we're looking for"  )

  
try:  
    print("When pressed, you'll see: Rising Edge detected on 25")  
    print("When released, you'll see: Falling Edge detected on 25" ) 
    sleep(30)         # wait 30 seconds  
    print("Time's up. Finished!"  )
  
finally:                   # this block will run no matter how the try block exits  
    GPIO.cleanup()         # clean up after yourself  