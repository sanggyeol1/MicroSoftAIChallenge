from machine import Pin # Import Pin library
import utime # Import utime library

led = Pin("LED", Pin.OUT)  

while True: # Loop forever
    led.value(1) # Set Pin 25 to high
    utime.sleep(0.5) # Wait 0.5 second
    led.value(0) # Set Pin 25 to low
    utime.sleep(0.5) # Wait 0.5 second

