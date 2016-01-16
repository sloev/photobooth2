#!/usr/bin/python
# esc-pos-image.py - print image files given as command line arguments
#                    to simple ESC-POS image on stdout
# scruss - 2014-07-26 - WTFPL (srsly)

import shutil
import multiprocessing
import sys
from PIL import Image, ImageEnhance, ImageOps
import struct

def compose_image(img):
    #image = ImageOps.fit(img, (img.height, img.height))
    bbox = img.getbbox()
    image = img.crop(((bbox[2]/2)-(bbox[3]/2),0,(bbox[2]/2)+(bbox[3]/2),bbox[3]))
    image = image.resize((384,384))
    #image = ImageOps.expand(image, 1,(255,255,255))
    Image = ImageOps.grayscale(image)
    enh = ImageEnhance.Brightness(image)
    image = enh.enhance(1.3)
    enh = ImageEnhance.Contrast(image)
    image = enh.enhance(1.3)
    return image

class PrinterWorker(multiprocessing.Process):
    def __init__(self, _queue):
        super(PrinterWorker, self).__init__()
        self._queue = _queue
        self._printer = Printer()
        self._strip = Image.open("end_strip.jpg")

    def run(self):
        counter = 0
        for filename in iter(self._queue.get, None):
            if filename:
                image = Image.open(filename)
                image = compose_image(image)
                filename = filename + ".bin"
                self._printer.print_image(image, filename)
                counter += 1
                filename+="strip"
                if counter > 1:
                    counter = 0
                    self._printer.print_image(self._strip, filename)
                    sys.stderr.write("send two images, and strip to the printer!\n")
        sys.stderr.write("printer joined\n")


class Printer():
    """Thermal printer
    """
    def __init__(self):
        pass

    # print all of the images!
    def print_image(self, image, filename):
        if image.mode != '1':
            image = image.convert('1')

        # Invert image, via greyscale for compatibility
        #  (no, I don't know why I need to do this)
        image = ImageOps.invert(image.convert('L'))
        # ... and now convert back to single bit
        image = image.convert('1')

        # output header (GS v 0 \000), width, height, image data
        sys.stderr.write(filename)
        with open(filename, "w") as f:
            f.write(''.join(('\x1d\x76\x30\x00',
                                  struct.pack('2B', image.size[0] / 8 % 256,
                                              image.size[0] / 8 / 256),
                                              struct.pack('2B', image.size[1] % 256,
                                                          image.size[1] / 256),
                                                          image.tobytes())))
        try:
            shutil.copyfile(filename, "/dev/usb/lp0")
        except Exception:
            sys.stderr.write("error in copy file")
def main():
    # give usage and exit if no arguments
    if len(sys.argv) == 1:
        print 'Usage:', sys.argv[0], \
               'image1 image2 ... [ > printer_device ]'
        exit(1)
    filename = sys.argv[1]
    image = Image.open(filename)
    image = compose_image(image)
    printer = Printer()
    filename = filename + ".bin"
    printer.print_image(image, filename)

if __name__ == "__main__":
    main()
