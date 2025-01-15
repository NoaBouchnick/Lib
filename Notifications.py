# notifications.py
import csv
from typing import List

from Library.Book import Book
from Library.Customer import Customer
from Logger import Logger


class Notifications:
    def __init__(self,logger, users_file='users.csv'):
        self.users_file = users_file
        self.logger = logger

    def get_librarians(self) -> List[str]:
        """מחזיר את רשימת הספרנים מהעמודה הראשונה בקובץ user.csv"""
        librarians = []
        try:
            with open(self.users_file, 'r', encoding='utf-8') as file:
                reader = csv.reader(file)
                for row in reader:
                    if row:  # אם השורה לא ריקה
                        librarians.append(row[0])  # לוקח רק את העמודה הראשונה
        except Exception as e:
            self.logger.log_error(f"Error reading users file: {str(e)}")
        return librarians

    def notify_book_return(self, book: Book, customers: List[Customer]):
        """שולח הודעה לספרנים על החזרת ספר והשאלתו ללקוחות הבאים"""
        try:
            librarians = self.get_librarians()

            message = f"The book '{book.title}' returned and loaned to:"
            for customer in customers:
                message += f"\n- {customer.name} phon: {customer.phone}, email: {customer.email})"

            for librarian in librarians:
                self._send_notification(librarian, message)

            self.logger.log_info(f"Notifications sent to librarians about book '{book.title}'")
        except Exception as e:
            self.logger.log_error(f"Failed to send notifications: {str(e)}")

    def notify_book_addition(self, book: Book, customers: List[Customer]):
        """שולח הודעה לספרנים על הוספת עותקים והשאלתם"""
        try:
            librarians = self.get_librarians()

            message = f"were added {book.total_copies} Copies of the book '{book.title}' and were asked to:"
            for customer in customers:
                message += f"\n- {customer.name} (phon: {customer.phone}, email: {customer.email})"

            for librarian in librarians:
                self._send_notification(librarian, message)

            self.logger.log_info(f"Notifications sent about new copies of book '{book.title}'")
        except Exception as e:
            self.logger.log_error(f"Failed to send notifications: {str(e)}")

    def _send_notification(self, librarian: str, message: str):
        """מימוש פנימי של שליחת ההודעה"""
        print(f"Message has been sent to the librarian {librarian}:\n{message}\n")
        # כאן יהיה המימוש האמיתי של שליחת ההודעה בהמשך
