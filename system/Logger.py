import logging
from pathlib import Path
import os


class Logger:
    def __init__(self, log_file=None) -> None:
        self.logger = logging.getLogger("LibraryLogger")
        self.logger.setLevel(logging.INFO)

        if log_file is None:
            # מציאת הנתיב לתיקיית files בהתבסס על המבנה החדש
            base_path = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            log_file = base_path / "files" / "library.log"

            # וידוא שהתיקייה קיימת
            log_file.parent.mkdir(parents=True, exist_ok=True)

        # פורמט של הלוגים
        formatter = logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s')

        # כתיבה לקובץ
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

        # כתיבה לקונסול
        self.console_handler = logging.StreamHandler()
        self.console_handler.setFormatter(formatter)
        self.logger.addHandler(self.console_handler)

    def log_info(self, message):
        self.logger.info(message)

    def log_error(self, message):
        self.logger.error(message)

    def log_debug(self, message):
        self.logger.debug(message)

    def disable_console_logs(self):
        """מסיר את הלוגים לקונסול."""
        self.logger.removeHandler(self.console_handler)