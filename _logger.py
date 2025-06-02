import logging
import traceback
import inspect

class CatchErrors:
    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger(__name__)
        logging.basicConfig(level=logging.ERROR)

    def __call__(self, func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # Get calling frame info
                frame = inspect.trace()[1]
                filename = frame.filename
                lineno = frame.lineno
                func_name = func.__name__

                # Format and log the error
                self.logger.error(
                    f"[{func_name}] Error: {e}\n"
                    f"Location: {filename}, line {lineno}\n"
                    f"Traceback:\n{traceback.format_exc()}"
                )
        return wrapper


import logging

class PrintLog:
    def __init__(self, logger=None):
        logging.basicConfig(level=logging.INFO)
        self.logger = logger or logging.getLogger(__name__)
    
    def __call__(self, msg, *args, **kwargs):
        self.logger.info(msg, *args, **kwargs)

# create a single instance that you import as "log"
log = PrintLog()