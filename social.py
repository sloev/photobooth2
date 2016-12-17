
import sys
import os

import json,time
from facepy import GraphAPI
from PIL import Image
import io
import uuid
from log import setup_logging



logging = setup_logging()
logger = logging.getLogger(__name__)


class session:
    facebook = None
session = session()

def create_session(config_filename='apiconfigs.txt'):
    with open(config_filename, 'r') as config_file:
        config = json.load(config_file)

        facebook_config = config["facebook"]
        session.facebook = GraphAPI(facebook_config["token"])

        print(session.facebook.get('me'))

def social_upload(filename):
    image_file = open(filename, "rb")

    message = "Loppen photo {}".format(uuid.uuid4())
    logger.info("uploading image, filename: {} message: {}".format(
        filename, message
    ))

    tries=5
    while(tries >= 0):
        try:
            logger.info("uploading to facebook, try # {}".format(tries))
            s = session.facebook.post(
                       path = 'me/photos',
                       source = image_file,
                       message = message
            )
            logger.info("uploaded to facebook,{}".format(s))
            os.remove(filename)
            logger.info("removed {}".format(filename))
            break
        except:
            logger.exception("facebook error, try # {}".format(tries))
            time.sleep(5)
            tries -= 1

    if not tries:
        logger.info("upload to facebook failed")


def main():
    create_session()
    try:
        logger.info("social uploader running")
        while True:
            for dirpath, dnames, fnames in os.walk("./social/"):
                for filename in fnames:
                    if not filename.endswith(".py"):
                        filename = os.path.join(dirpath, filename)
                        logger.info("found file!!! : {}".format(filename))
                        social_upload(filename)
                        time.sleep(5)
            logger.info("no files, sleeping 5 seconds")
            time.sleep(5)
            logger.info("woke up!")
    except:
        logger.exception("exited")

if __name__ == "__main__":
    main()
