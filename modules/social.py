#!/usr/bin/python
# esc-pos-image.py - print image files given as command line arguments
#                    to simple ESC-POS image on stdout
# scruss - 2014-07-26 - WTFPL (srsly)

import multiprocessing
import sys
import os

import json,time
from facepy import GraphAPI
from PIL import Image


class SocialWorker(multiprocessing.Process):
    def __init__(self, _queue):
        super(SocialWorker, self).__init__()
        self._queue = _queue
        with open("photonumber.txt", 'r') as f:
            self._photonumber = int(f.readline())
        with open('apiconfigs.txt', 'rb') as fp:
            config = json.load(fp)
            self._facebook = Facebook(config["facebook"])

    def run(self):
        counter = 0
        for image in iter(self._queue.get, None):
            if image:
                counter += 1
                if counter > 3:
                    counter = 0

                    sys.stderr.write("socializing image\n")
                    message = "Photo #%d" % self._photonumber
                    image.save("tmp.jpg", "JPEG")
                    self._facebook.upload_image("tmp.jpg", message)
                    self._photonumber += 1
                    f = open("photonumber.tmp", 'w')
                    f.write(str(self._photonumber))
                    f.flush()
                    os.fsync(f.fileno()) 
                    f.close()
                    os.rename("photonumber.tmp", "photonumber.txt")
        sys.stderr.write("social worker joined\n")

    def compose_image(self, images):
        y = 0
        x = 0
        strip = self._strip

        for image in images:
            strip = image

        return strip


class Facebook(object):
    '''
    classdocs
    '''
    def __init__(self,config):
        self.facebook = GraphAPI(config["token"])
        try:
            me=self.facebook.get('me')
            sys.stderr.write(json.dumps(me, indent=4))

        except:
            pass#self.facebook=None

    def upload_image(self,image, messageStr="sdfsafdsdfafgsdghdef"):
        tries=0
        while(tries<5):
            try:
                s = self.facebook.post(
                                   path = 'me/photos',
                                   source = open(image),
                                   message=messageStr
                                   )
                break
            except:
                sys.stderr.write("facebook error, try #%d\n" % tries)
                time.sleep(0.1)
                tries=tries+1

        sys.stderr.write("finnished uploading to facebook\n")
