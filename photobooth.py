import sys
import select
import multiprocessing
import time

import wiringpi2 as wiringpi
from PIL import Image

from modules.printer import PrinterWorker
from modules.social import SocialWorker
from modules.led import LedWorker
from modules.camera import Camera

from PIL import ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True

def main():
    def wiring_setup():
        wiringpi.wiringPiSetupGpio()
        wiringpi.pinMode(4, 0)
        wiringpi.pinMode(18, 2)

    def wiring_cleanup():
        wiringpi.digitalWrite(18, 0)
        wiringpi.pinMode(18, 0)

    def shoot():
        for i in range(0,1025,4):
            wiringpi.pwmWrite(18,i)
            time.sleep(0.002)
        for i in range(4):
            filename = camera.shoot("%d"%i)
            social_queue.put(filename)
            if not i % 2: #first and third image gets printed
                printer_queue.put(filename)
        led_queue.put("off")
        for i in range(1024,-1,-1):
            wiringpi.pwmWrite(18,i)
            time.sleep(0.005)
        sys.stderr.write("press \"s\" to shoot!\n")

    wiring_setup()
    queues = []
    printer_queue = multiprocessing.Queue()
    queues.append(printer_queue)
    social_queue = multiprocessing.Queue()
    queues.append(social_queue)
    camera = Camera()
    led_queue = multiprocessing.Queue()
    queues.append(led_queue)


    procs = []
    led_worker = LedWorker(led_queue)
    procs.append(led_worker)
    printer_worker = PrinterWorker(printer_queue)
    procs.append(printer_worker)
    social_worker = SocialWorker(social_queue)

    procs.append(social_worker)

    for i in procs:
        i.start()

    sys.stderr.write("press \"s\" to shoot!\n")
    try:
        while True:
            time.sleep(0.2)
            if(wiringpi.digitalRead(4) == 0):
                time.sleep(0.2)
                if(wiringpi.digitalRead(4) == 0):
                    shoot()
            while sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
                c = sys.stdin.readline()
                c = c[0:1]
                if(c =='s'):
                    shoot()
                elif(c=='q'):
                    break
    except KeyboardInterrupt:
        sys.stderr.write("quiting")
        pass
    #give poison pill to workers!
    for i in queues:
        i.put(None)
    for i in procs:
        i.join()
    sys.stderr.write("all joined!, cleaning up up gpio now\n")
    wiring_cleanup()
    sys.stderr.write("all clean, goodbye!\n")


if __name__ == "__main__":
    main()
