import logging
import logging.handlers

def setup_logging():
    logging.basicConfig(level=logging.INFO)

    handler = logging.handlers.SysLogHandler(address = '/dev/log')
    formatter = logging.Formatter('%(asctime)s - %(filename)s:%(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logging.getLogger().handlers = [handler]

    return logging
