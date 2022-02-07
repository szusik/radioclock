#!/usr/bin/env python

import time
import threading
import logging

from time import sleep, localtime

from modules.tm1637 import TM1637

DIO = 26
CLK = 19

tm = TM1637(CLK, DIO)
tm.brightness(1)

class Clock:
    def __init__(self, tm_instance):
        self.tm = tm_instance
        self.show_colon = False

    def run(self):
        while True:
            t = localtime()
            self.show_colon = not self.show_colon
            tm.numbers(t.tm_hour, t.tm_min, self.show_colon)
            sleep(1)
            if threading.current_thread().stopped():
                logging.info("Clock thread marked as stopped")
                break

def runClock(BRIGHTNESS):
    clock = Clock(tm)
    clock.run()

def clearScreen():
    tm.write([0, 0, 0, 0])
    tm.brightness(0)

