import os

from .Book import Book
from .CSVHandler import CSVHandler
from Log import Log
from Notifications import Notifications
from .Customer import Customer


################# בדוק מימוש ###############
# def log_action(func):
#     def wrapper(self, *args, **kwargs):
#         try:
#             result = func(self, *args, **kwargs)
#             self.logger.log_info(f"book {func.__name__} successfully")
#             return result
#         except Exception as e:
#             self.logger.log_error(f"book {func.__name__} fail")
#             raise
#     return wrapper
## דקורטור??

class Librarian:

    def __init__(self, file_path=None) -> None:
        # אם לא נמסר path לקובץ, ברירת המחדל היא מיקום הקובץ בספריית הספרייה
        if file_path is None:
            base_path = os.path.dirname(os.path.abspath(__file__))
            file_path = os.path.join(base_path, 'books.csv')

        # טוען ספרים מקובץ CSV
        self.books = CSVHandler.load_books_from_csv(file_path)

        self.books_borrowed = {}
        self.logger = Log()
        self.waiting_list = {}  # Book, customer
        self.notifications = Notifications()

    def added(self, book: Book):
        if book.title in self.books:
            self.books[book.title].total_copies += book.total_copies
            self.books[book.title].available_copies += book.available_copies
            self.logger.log_info("book added successfully")
        else:
            self.books[book.title] = book
            self.logger.log_info("book added successfully")

        self.save_books()

    def removed(self, book: Book):
        if book.title not in self.books:
            self.logger.log_error("book removed fail")
        else:
            if book.total_copies < self.books[book.title].total_copies:
                self.books[book.title].total_copies -= book.total_copies
                self.books[book.title].available_copies -= book.total_copies
                self.logger.log_info("book removed successfully")
            else:
                del self.books[book.title]
                self.logger.log_info("book removed successfully")
        self.save_books()

    def loaned(self, book: Book, customer: Customer):
        if book.title in self.books:
            current_book = self.books[book.title]

            if current_book.available_copies > 0:
                current_book.available_copies -= 1
                self.books_borrowed[book.title] = self.books_borrowed.get(book.title, 0) + 1

                self.logger.log_info("book loaned successfully")
            else:
                self.logger.log_error("book loaned fail")
                # כאן ניתן להוסיף אפשרות להכניס לרשימת המתנה
                self.waiting_for_book(book, customer)
                self.logger.log_info(f"{customer} added to waiting list")
        else:
            self.logger.log_error("book loaned fail")
        self.save_books()

    def returned(self, book: Book):
        if book.title not in self.books or book.title not in self.books_borrowed:
            self.logger.log_error("book returned fail")
            ## רשימת המתנה
            if book.title in self.waiting_list:
                self.notifications.notify_waiting_list(book)
                self.logger.log_info("send message")

        else:
            current_book = self.books[book.title]
            current_book.available_copies += 1
            self.books_borrowed[book.title] -= 1
            if self.books_borrowed[book.title] == 0:
                del self.books_borrowed[book.title]
            self.logger.log_info("book return successfully")
        self.save_books()

    def waiting_for_book(self, book: Book, customer: Customer):
        if book.title in self.books and self.books[book.title].available_copies == 0:
            if book.title not in self.waiting_list:
                self.waiting_list[book.title] = []
            self.waiting_list[book.title].append(customer)
            self.logger.log_info("Customer added to the waiting list successfully")
        else:
            self.logger.log_error("Customer added to the waiting list fail")

    def save_books(self):
        CSVHandler.save_books_to_csv(self.books)
