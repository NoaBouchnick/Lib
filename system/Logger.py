import logging
from pathlib import Path
import os

#a logging utility class for handling log messages in the library system
class Logger:
    #initializes the logger instance with a log file and console logging
    def __init__(self, log_file=None) -> None:
        self.logger = logging.getLogger("LibraryLogger")
        self.logger.setLevel(logging.INFO)

        #find path to log files based on project structure
        if log_file is None:
            base_path = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            log_file = base_path / "files" / "library.log"

            #ensure the file directory exists
            log_file.parent.mkdir(parents=True, exist_ok=True)

        # log formatting
        formatter = logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s')

        # write logs to file
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

        # write logs to console
        self.console_handler = logging.StreamHandler()
        self.console_handler.setFormatter(formatter)
        self.logger.addHandler(self.console_handler)

    #logs an informational message
    def log_info(self, message):
        self.logger.info(message)

    #logs an error message
    def log_error(self, message):
        self.logger.error(message)

    #logs a debug message
    def log_debug(self, message):
        self.logger.debug(message)

    #removes the console log handler to disable logging to the console
    def disable_console_logs(self):
        self.logger.removeHandler(self.console_handler)