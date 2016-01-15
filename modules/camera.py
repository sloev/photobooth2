'''
Created on Apr 22, 2014

@author: johannes
'''

import picamera
from PIL import Image
#import io
import sys

class Camera(object):
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''
        self.camera = picamera.PiCamera()
        self.camera.resolution=(1024,768)
        sys.stderr.write("[!] camera initialized\n")
      #  self.camera.resolution=(800,600)

    def shoot(self, filename):
        #stream = io.BytesIO()
        #self.camera.capture(stream, format='jpeg')
        #stream.seek(0)
        #image = Image.open(stream)
        filename = "images/%s.jpg" % filename
        self.camera.capture(filename)
        sys.stderr.write("[*] camera took one photo\n")

        return filename
