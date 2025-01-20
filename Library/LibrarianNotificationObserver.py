import csv
import os
from typing import List
from pathlib import Path
from Books.Book import Book
from Library.Customer import Customer
from Library.Observer import Observer


class LibrarianNotificationObserver(Observer):
    def __init__(self, logger):
        base_path = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.users_file = base_path / "files" / "users.csv"
        self.logger = logger

    def get_librarians(self) -> List[str]:
        """מחזיר את רשימת הספרנים מהעמודה הראשונה בקובץ user.csv"""
        librarians = []
        try:
            if self.users_file.exists():
                with open(self.users_file, 'r', encoding='utf-8') as file:
                    reader = csv.reader(file)
                    for row in reader:
                        if row:  # אם השורה לא ריקה
                            librarians.append(row[0])  # לוקח רק את העמודה הראשונה
        except Exception as e:
            self.logger.log_error(f"Error reading users file: {str(e)}")
        return librarians

    def update(self, book: Book, customers: List[Customer], event_type: str):
        try:
            librarians = self.get_librarians()
            if event_type == "return":
                message = f"The book '{book.title}' returned and loaned to:"
            elif event_type == "addition":
                message = f"Were added {book.total_copies} copies of the book '{book.title}' and were loaned to:"
            else:
                return

            for customer in customers:
                message += f"\n- {customer.name} (Phone: {customer.phone}, Email: {customer.email})"

            for librarian in librarians:
                self._send_notification(librarian, message)

            self.logger.log_info(f"Notifications sent to librarians about book '{book.title}'")
        except Exception as e:
            self.logger.log_error(f"Failed to send notifications: {str(e)}")

    def _send_notification(self, librarian: str, message: str):
        """מימוש פנימי של שליחת ההודעה"""
        print(f"Message has been sent to the librarian {librarian}:\n{message}\n")