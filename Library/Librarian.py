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
        if file_path is None:
            base_path = os.path.dirname(os.path.abspath(__file__))
            file_path = os.path.join(base_path, 'books.csv')

        # טוען ספרים מקובץ CSV
        self.books = CSVHandler.load_books_from_csv(file_path)

        self.books_borrowed = {}
        for title, book in self.books.items():
            if book.is_loaned == "Yes":
                book.available_copies = 0
                self.books_borrowed[title] = book.total_copies

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

    def removed(self, book: Book) -> bool:
        if book.title not in self.books or book.title in self.books_borrowed:
            self.logger.log_error("book removed fail")
            return False
        else:
            del self.books[book.title]
            self.logger.log_info("book removed successfully")
            self.save_books()
            return True

    def loaned(self, book: Book):
        if book.title in self.books:
            current_book = self.books[book.title]

            if current_book.available_copies > 0:
                current_book.available_copies -= 1
                if current_book.available_copies == 0:
                    current_book.is_loaned = "Yes"
                self.books_borrowed[book.title] = self.books_borrowed.get(book.title, 0) + 1
                self.logger.log_info("book loaned successfully")
            else:
                self.logger.log_error("book loaned fail")
                self.waiting_for_book(book)  # אין צורך בפרמטר לקוח פה
                self.logger.log_info(f"Customer added to waiting list for book '{book.title}'")
        else:
            self.logger.log_error("book loaned fail")
        self.save_books()

    def returned(self, book: Book):
        if book.title not in self.books or book.title not in self.books_borrowed:
            self.logger.log_error("book returned fail")
            if book.title in self.waiting_list:
                self.notifications.notify_waiting_list(book)
                self.logger.log_info("send message")
        else:
            current_book = self.books[book.title]
            current_book.available_copies += 1
            if current_book.available_copies > 0:
                current_book.is_loaned = "No"
            self.books_borrowed[book.title] -= 1
            if self.books_borrowed[book.title] == 0:
                del self.books_borrowed[book.title]
            self.logger.log_info("book return successfully")
        self.save_books()

    def waiting_for_book(self, book: Book):
        # יצירת לקוח בעת הצורך להוספה לרשימת ההמתנה
        customer = self.create_customer()  # יצירת לקוח חדש אם צריך
        if book.title not in self.waiting_list:
            self.waiting_list[book.title] = []
        self.waiting_list[book.title].append(customer)
        self.logger.log_info(f"Customer {customer} added to waiting list for book '{book.title}'")

    def create_customer(self):
        def create_customer(self):
            # בקשת פרטי הלקוח מהמשתמש
            name = input("Enter customer name: ")
            phone = input("Enter customer phone: ")
            email = input("Enter customer email: ")

            # יצירת אובייקט לקוח חדש
            customer = Customer(name, phone, email)

            return customer
    def save_books(self):
        CSVHandler.save_books_to_csv(self.books)

