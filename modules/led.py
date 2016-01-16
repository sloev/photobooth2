#!/usr/bin/python
# esc-pos-image.py - print image files given as command line arguments
#                    to simple ESC-POS image on stdout
# scruss - 2014-07-26 - WTFPL (srsly)

import wiringpi2
import multiprocessing
import time

class LedWorker(multiprocessing.Process):
    def __init__(self, _queue):
        super(LedWorker, self).__init__()
        self._queue = _queue

    def run(self):
        for cmd in iter(self._queue.get, None):
            if cmd:
                if cmd == "off":
                    for i in range(1000,-1,-1):
                        wiringpi2.pwmWrite(18,i)
                        time.sleep(0.005)
                else:
                    for i in range(0,1001,1):
                        wiringpi2.pwmWrite(18,1)
                        time.sleep(0.005)

        sys.stderr.write("led joined\n")

