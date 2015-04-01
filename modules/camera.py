'''
Created on Apr 22, 2014

@author: johannes
'''

import picamera
from PIL import Image
import io


class Camera(object):
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''
        self.camera = picamera.PiCamera()

        sys.stderr.write("[!] camera initialized\n")
      #  self.camera.resolution=(800,600)

    def shoot(self):
        stream = io.BytesIO()
        self.camera.capture(stream, format='jpeg')
        stream.seek(0)
        image = Image.open(stream)

        sys.stderr.write("[*] camera took one photo\n")
