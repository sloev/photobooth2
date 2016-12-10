from subprocess import call
from PIL import Image, ImageEnhance, ImageOps
import io
import sys
import time
import logging
import shutil
import multiprocessing
import sys
from PIL import Image, ImageEnhance, ImageOps
import struct
import wiringpi2 as wiringpi


strip = Image.open("end_strip.jpg")


def shoot():

    timestr = time.strftime("%Y%m%d-%H%M%S")

    filename = "images/{}.jpg".format(timestr)
    call(["raspistill", "-o", filename])
    return filename


def print_filename(filename):
    image = Image.open(filename)
    image = compose_image(image)
    print_image(image)

    print_image(strip)
    timestr = time.strftime("%Y%m%d-%H%M%S")

    new_filename = "social/{}.jpg".format(timestr)
    shutil.move(filename, new_filename)


def print_image(image):
    if image.mode != '1':
        image = image.convert('1')

    # Invert image, via greyscale for compatibility
    #  (no, I don't know why I need to do this)
    image = ImageOps.invert(image.convert('L'))
    # ... and now convert back to single bit
    image = image.convert('1')

    # output header (GS v 0 \000), width, height, image data

    s = ''.join(('\x1d\x76\x30\x00',
                              struct.pack('2B', image.size[0] / 8 % 256,
                                          image.size[0] / 8 / 256),
                                          struct.pack('2B', image.size[1] % 256,
                                                      image.size[1] / 256),
                                                      image.tobytes()))
    sys.stdout.write(s)
    sys.stdout.flush()


def compose_image(image):
    #image = ImageOps.fit(img, (img.height, img.height))
    bbox = image.getbbox()
    image = image.crop(((bbox[2]/2)-(bbox[3]/2),0,(bbox[2]/2)+(bbox[3]/2),bbox[3]))
    image = image.resize((384,384))
    #image = ImageOps.expand(image, 1,(255,255,255))
    Image = ImageOps.grayscale(image)
    enh = ImageEnhance.Brightness(image)
    image = enh.enhance(1.3)
    enh = ImageEnhance.Contrast(image)
    image = enh.enhance(1.3)
    return image

def main():
    wiringpi.wiringPiSetupGpio()
    wiringpi.pinMode(4, 0)
    wiringpi.pinMode(18, 2)

    try:
        while True:
            time.sleep(0.2)
            if(wiringpi.digitalRead(4) == 0):
                time.sleep(0.2)
                if(wiringpi.digitalRead(4) == 0):
                    filename = shoot()
                    print_filename(filename)
    except KeyboardInterrupt:
        sys.stderr.write("quiting")
        pass
    wiringpi.digitalWrite(18, 0)
    wiringpi.pinMode(18, 0)

if __name__ == "__main__":
    main()
