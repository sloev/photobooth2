#!/usr/bin/python
# esc-pos-image.py - print image files given as command line arguments
#                    to simple ESC-POS image on stdout
# scruss - 2014-07-26 - WTFPL (srsly)

import multiprocessing
import sys

class SocialWorker(multiprocessing.Process):
    def __init__(self, _queue):
        super(SocialWorker, self).__init__()
        self._queue = _queue

    def run(self):
        counter = 0
        for image in iter(self._queue.get, None):
            if image:
                counter += 1
                if counter > 3:
                    sys.stderr.write("socializing image\n")
        sys.stderr.write("social worker joined\n")
