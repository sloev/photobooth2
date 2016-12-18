

import os
import json
from log import setup_logging

logging = setup_logging()
logger = logging.getLogger(__name__)

logger.info("shutterdownder loading")

from flask import Flask
app = Flask(__name__)


from functools import wraps
from flask import request, Response

credentials = {}

def create_session(config_filename='apiconfigs.txt'):
    with open(config_filename, 'r') as config_file:
        config = json.load(config_file)

        credentials.update(config["shutdown"])


@app.route("/shutdown")
def shutdown():
    logging.info("received shutdown")

    # here we want to get the value of user (i.e. ?user=some-value)
    username = request.args.get('username')
    password = request.args.get('password')
    if credentials["username"] == username and credentials["password"] == password:
        logging.info("shutting down")
        os.system("shutdown now -h")
        return "shutdown"
    return "wrong credentials", 401

if __name__ == "__main__":
    logging.info("shutdown server running")
    create_session()
    app.run(host="0.0.0.0", port=5000)
