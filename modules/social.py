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
import flickr_api as flickr
import io
from websocket import create_connection

class SocialWorker(multiprocessing.Process):
    def __init__(self, _queue):
        super(SocialWorker, self).__init__()
        self._queue = _queue
        with open("photonumber.txt", 'r') as f:
            self._photonumber = int(f.readline())
        with open('apiconfigs.txt', 'rb') as fp:
            config = json.load(fp)
            self._facebook = Facebook(config["facebook"])
            fc = config['flickr']
            fc = {'api_key':str(fc['api_key']), 'api_secret':str(fc['api_secret'])}
            flickr.set_keys(**fc)
            flickr.set_auth_handler("flickr.auth")
            user = flickr.test.login()
            sys.stderr.write("flickr\n%s"%str(user))
            photos = []
            for i in user.getPhotos():
                photos += [
                        {'instruction':'post_photo',
                            'args': {
                                'title':i.title,
                                'url':i.getSizes()['Original']['source'],
                                'date':i.getInfo()['taken']
                                },
                            'callback_id':''}]
            sys.stderr.write("connecting to ws")
            self.ws = create_connection("ws://127.0.0.1:8888")
            for args in photos:
                self.ws.send(json.dumps(args))
    def run(self):
        counter = 0
        for image_file in iter(self._queue.get, None):
            if image_file:
                #image.save("socialout%d.jpg"%counter, "JPEG")
                counter += 1
                if counter > 3:
                    filename = "images/social_out.jpg"
                    stream = io.BytesIO()
                    image_file.save(stream, format='JPEG')
                    image_file.save(filename, format='JPEG')
                    stream.seek(0)
                    #image_file.save(filename)
                    counter = 0
                    sys.stderr.write("socializing image\n")
                    file_str = bin(self._photonumber)[2:].replace('1','|').replace('0','-')
                    message = "[ %s ]" %file_str
                    self._facebook.upload_image(stream, message)
                    flickr_image = flickr.upload(photo_file=filename,title=message)
                    sys.stderr.write("flickr_image\n%s\n"%str(flickr_image))
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
            #sys.stderr.write(json.dumps(me, indent=4))

        except:
            pass#self.facebook=None

    def upload_image(self,imagefile, messageStr="sdfsafdsdfafgsdghdef"):
        tries=0
        while(tries<5):
            try:
                s = self.facebook.post(
                                   path = 'me/photos',
                                   source = imagefile,
                                   message=messageStr
                                   )
                break
            except:
                sys.stderr.write("facebook error, try #%d\n" % tries)
                time.sleep(0.1)
                tries=tries+1

        sys.stderr.write("finnished uploading to facebook\n")
if __name__ == "__main__":
    sw = SocialWorker(None)
