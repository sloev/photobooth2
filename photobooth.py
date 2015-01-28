import sys
import select

from PIL import Image

from modules.printer import PrinterWorker
from modules.social import SocialWorker

from modules.camera import Camera

def main():
    strip = Image.open("strip.jpg")
    printer_queue = multiprocessing.Queue()
    social_queue = multiprocessing.Queue()
    camera = Camera()
    printer_worker = PrinterWorker(printer_queue)
    social_worker = SocialWorker(social_queue)

    def shoot():
        for _ in range(2):
            image = camera.shoot()
            printer_queue.put(image)
            social_queue.put(image)
        printer_queue.put(strip)

        for _ in range(2):
            social_queue.put(camera.shoot())
    try:
        sys.stderr.write("press \"s\" to shoot!")
        while True:
            while sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
                c = sys.stdin.readline()
                c = c[0:1]
                if(c =='s'):
                    shoot()
    except KeyboardInterrupt:
        sys.stderr.write("quiting")
        pass
    #give poison pill to workers!

    #first the printer
    printer_queue.put(None)
    sys.stderr.write("printer_worker joining")
    printer_worker.join()
    sys.stderr.write("printer_worker joined")

    #then the social
    social_queue.put(None)
    sys.stderr.write("social_worker joining")
    social_worker.join()
    sys.stderr.write("social_worker joined")

if __name__ is "__main__":
    main()
