import sys
import select
import multiprocessing

from PIL import Image

from modules.printer import PrinterWorker
from modules.social import SocialWorker

from modules.camera import Camera

from PIL import ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True

def main():
    queues = []
    printer_queue = multiprocessing.Queue()
    queues.append(printer_queue)
    social_queue = multiprocessing.Queue()
    queues.append(social_queue)
    camera = Camera()
    procs = []
    printer_worker = PrinterWorker(printer_queue)
    procs.append(printer_worker)
    social_worker = SocialWorker(social_queue)

    procs.append(social_worker)

    for i in procs:
        i.start()

    def shoot():
        for i in range(4):
            image = camera.shoot()
            social_queue.put(image)
            if not i % 2: #first and third image gets printed
                printer_queue.put(image)
    try:
        sys.stderr.write("press \"s\" to shoot!")
        while True:
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

if __name__ == "__main__":
    main()
