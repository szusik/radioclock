#!/usr/bin/env python

import time
import threading
import logging
import sys

from time import sleep, localtime

from modules.tm1637 import TM1637
import modules.config as cfg

tmClock = TM1637(cfg.clockCLK, cfg.clockDIO)
tmClock.brightness(1)

class Clock:
    def __init__(self,tm_instance):
        self.tm = tm_instance
        self.show_colon = False

    def run(self):
        while True:
            try:
                #logging.info("Clock thread running 1")
                t = localtime()
                self.show_colon = not self.show_colon
                #logging.info("Clock thread running 2")
                self.tm.numbers(t.tm_hour, t.tm_min, self.show_colon)
                sleep(1)
                if threading.current_thread().stopped():
                    logging.info("Clock thread marked as stopped")
                    break
                #else:
                #    logging.info("Clock thread running 3")
            except:
                err = str(sys.exc_info())
                logging.error("Clock error known as "+err)   

def runClock(brightness):
    global tmClock
    tmClock.brightness(int(brightness))
    clock = Clock(tmClock)
    clock.run()

def clearScreen():
    global tmClock
    tmClock.write([0, 0, 0, 0])
    tmClock.brightness(0)

