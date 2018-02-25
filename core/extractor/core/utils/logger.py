import logging
import sys

def create_logger(module_name, log_level=logging.INFO):
    """ Configure base logger for each of our classes. """
    
    logging.basicConfig(
        format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
        level=log_level,
        stream=sys.stderr)
    logger = logging.getLogger(module_name)

    return logger