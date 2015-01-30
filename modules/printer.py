#!/usr/bin/python
# esc-pos-image.py - print image files given as command line arguments
#                    to simple ESC-POS image on stdout
# scruss - 2014-07-26 - WTFPL (srsly)

import multiprocessing
import sys
from PIL import Image, ImageOps
import struct

class PrinterWorker(multiprocessing.Process):
    def __init__(self, _queue):
        super(PrinterWorker, self).__init__()
        self._queue = _queue
        self._printer = Printer()
        self._strip = Image.open("strip.jpg")

    def run(self):
        counter = 0
        for image in iter(self._queue.get, None):
            if image:
                image = self._compose_image(image)
                self._printer.print_image(image)
                counter += 1
                if counter > 1:
                    counter = 0
                    self._printer.print_image(self._strip)
                    self._printer.print_image(image)
                    sys.stderr.write("send two images, and strip to the printer!\n")
        sys.stderr.write("printer joined\n")

    def _compose_image(self, img):
        bbox = img.getbbox()
        image = img.crop(((bbox[2]/2)-(bbox[3]/2),0,(bbox[2]/2)+(bbox[3]/2),bbox[3]))
        image = image.resize((382,382))
        image = ImageOps.expand(image, 1,(255,255,255))
        return image

class Printer():
    """Thermal printer
    """
    def __init__(self):
        pass

    # print all of the images!
    def print_image(self, image):
        # if image is not 1-bit, convert it
                # if image width is not a multiple of 8 pixels, fix that
        #if image.size[0] % 8:
        #    image2 = Image.new('1', (image.size[0] + 8 - image.size[0] % 8,
        #                    image.size[1]), 'white')
        #    image2.paste(image, (0, 0))
        #    image = image2
        if image.mode != '1':
            image = image.convert('1')

        # Invert image, via greyscale for compatibility
        #  (no, I don't know why I need to do this)
        image = ImageOps.invert(image.convert('L'))
        # ... and now convert back to single bit
        image = image.convert('1')

        # output header (GS v 0 \000), width, height, image data
        sys.stdout.write(''.join(('\x1d\x76\x30\x00',
                                  struct.pack('2B', image.size[0] / 8 % 256,
                                              image.size[0] / 8 / 256),
                                              struct.pack('2B', image.size[1] % 256,
                                                          image.size[1] / 256),
                                                          image.tobytes())))
    sys.stdout.flush()
def main():
    # give usage and exit if no arguments
    if len(sys.argv) == 1:
        print 'Usage:', sys.argv[0], \
               'image1 image2 ... [ > printer_device ]'
        exit(1)

    image = Image.open(sys.argv[1])
    printer = Printer()
    printer.print_image(image)

if __name__ == "__main__":
    main()
