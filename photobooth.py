from subprocess import call
from PIL import Image, ImageEnhance, ImageOps
import io
import sys
import time
import shutil
import sys
import os
from PIL import Image, ImageEnhance, ImageOps
import struct
import wiringpi2 as wiringpi
import multiprocessing

from log import setup_logging



logging = setup_logging()
logger = logging.getLogger(__name__)


strip = Image.open("end_strip.jpg")

def fade_led(wiringpi):
    for i in range(0,301,1):
        wiringpi.pwmWrite(18,i)
        time.sleep(0.004)
    time.sleep(4)
    for i in range(301,-1,-1):
        wiringpi.pwmWrite(18,i)
        time.sleep(0.003)
    logging.info("led fading done")

def shoot():
    logger.info("shooting a pic")

    timestr = time.strftime("%Y%m%d-%H%M%S")

    filename = "./images/{}.jpg".format(timestr)
    call(["raspistill", "-o", filename])
    logger.info("shot a pic: {}".format(filename))
    return filename


def print_filename(filename):
    image = Image.open(filename)
    image = compose_image(image)
    logger.info("printing image {}".format(filename))
    print_image(image)

    logger.info("printing strip")
    print_image(strip)
    timestr = time.strftime("%Y%m%d-%H%M%S")

    new_filename = "./social/{}.jpg".format(timestr)
    logger.info("moving file to social upload")
    new_image = image.convert(mode='P',
        colors=256,
        dither=1,
        palette=Image.ADAPTIVE)
    new_image = new_image.convert("RGB")
    new_image.save(new_filename)
    logger.info("done sending to printer")


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
    with open('/dev/usb/lp0', 'w') as f:
        f.write(s)
        f.flush()
    logger.info("done printing")


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
    logger.info("photobooth running!")
    wiringpi.wiringPiSetupGpio()
    wiringpi.pinMode(4, 0)
    wiringpi.pinMode(18, 2)
    t1 = multiprocessing.Process(target=fade_led, args= (wiringpi, ))
    t1.start()
    t1.join()
    logger.info("faded down")
    try:
        while True:
            time.sleep(0.2)
            if(wiringpi.digitalRead(4) == 0):
                time.sleep(0.2)
                if(wiringpi.digitalRead(4) == 0):
                    logger.info("button pressed")
                    try:
                        t1.join()
                    except:
                        pass
                    t1 = multiprocessing.Process(target=fade_led, args= (wiringpi, ))
                    t1.start()

                    filename = shoot()
                    print_filename(filename)

    except:
        logger.exception("error")
    t1.join()

    wiringpi.digitalWrite(18, 0)
    wiringpi.pinMode(18, 0)
    logger.info("exiting")

if __name__ == "__main__":
    main()
