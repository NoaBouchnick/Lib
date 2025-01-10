import os

from Error.BookDoesNotExistException import BookDoesNotExistException
from Error.CustomException import CustomException
from Error.NegativeCopiesException import NegativeCopiesException
from Error.NoBorrowedCopiesException import NoBorrowedCopiesException
from Error.NoCopyAvailableException import NoCopyAvailableException
from Error.NonIntegerValueException import NonIntegerValueException
from Error.RemovingBorrowedBookException import RemovingBorrowedBookException
from .Book import Book
from .CSVHandler import CSVHandler
from Logger import Logger
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

        self.logger = Logger()
        self.waiting_list = {}  # Book, customer
        self.notifications = Notifications()

    def added(self, book: Book):
        try:
            # דיבוג: בדיקת ערכי הספר לפני בדיקות תנאים
            self.logger.log_debug(
                f"Attempting to add book: title={book.title}, total_copies={book.total_copies}, year={book.year}")

            # בדיקה אם ערכי השנה וכמות העותקים הם מסוג int
            if not isinstance(book.total_copies, int) or not isinstance(book.year, int):
                self.logger.log_debug("Non-integer value detected for total_copies or year.")
                raise NonIntegerValueException()

            # בדיקה אם כמות העותקים שלילית או אפס
            if book.total_copies <= 0:
                self.logger.log_debug("Negative or zero value detected for total_copies.")
                raise NegativeCopiesException()

            # דיבוג: הוספת הספר למערכת
            self.logger.log_debug(f"Adding book to collection: title={book.title}")

            if book.title in self.books:
                self.books[book.title].total_copies += book.total_copies
                self.books[book.title].available_copies += book.available_copies
            else:
                self.books[book.title] = book

            self.logger.log_info("Book added successfully")
            self.save_books()

        except CustomException as e:
            self.logger.log_error("Book added fail")

    def removed(self, book: Book) -> bool:
        try:
            # דיבוג: בדיקה אם הספר קיים במערכת
            self.logger.log_debug(f"Attempting to remove book: title={book.title}")

            # בדיקה אם הספר קיים במערכת או כבר הושאל
            if book.title not in self.books:
                self.logger.log_debug(f"Book {book.title} does not exist.")
                raise BookDoesNotExistException()

            if book.title in self.books_borrowed:
                self.logger.log_debug(f"Book {book.title} is currently borrowed.")
                raise RemovingBorrowedBookException()

            # הסרת הספר אם הוא לא הושאל
            del self.books[book.title]
            self.logger.log_info(f"Book removed successfully.")
            self.save_books()
            return True

        except CustomException as e:
            self.logger.log_error("Book removed fail")
            raise e
        except Exception as e:
            # כל שגיאה לא צפויה
            self.logger.log_error("Book removed fail")
            raise e

    def loaned(self, book: Book)-> bool:
        try:
            if book.title in self.books:
                current_book = self.books[book.title]

                if current_book.available_copies > 0:
                    current_book.available_copies -= 1
                    if current_book.available_copies == 0:
                        current_book.is_loaned = "Yes"
                    self.books_borrowed[book.title] = self.books_borrowed.get(book.title, 0) + 1
                    self.logger.log_info("book loaned successfully")
                    self.save_books()
                    return True
                else:
                    # אם אין עותקים זמינים
                    raise NoCopyAvailableException()

            else:
                # אם הספר לא קיים
                raise BookDoesNotExistException()

        except CustomException as e:
            self.logger.log_error(f"Book loaned fail")

        except Exception as e:
            # טיפול בשגיאות לא צפויות
            self.logger.log_error("Book loaned fail")

    def returned(self, book: Book) -> bool:
        try:
            # אם הספר לא קיים במערכת או לא הושאל
            if book.title not in self.books:
                raise BookDoesNotExistException("Book does not exist in the system.")

            if book.title not in self.books_borrowed:
                raise NoBorrowedCopiesException("There are no borrowed copies of this book.")

            # אם הספר קיים והושאל, נבצע את החזרת הספר
            current_book = self.books[book.title]
            current_book.available_copies += 1
            if current_book.available_copies > 0:
                current_book.is_loaned = "No"

            self.books_borrowed[book.title] -= 1
            if self.books_borrowed[book.title] == 0:
                del self.books_borrowed[book.title]

            self.logger.log_info("Book returned successfully.")
            self.save_books()
            return True

        except CustomException as e:
            self.logger.log_error("Book returned fail")
            raise e  # נזרוק את השגיאה שוב

        except Exception as e:
            self.logger.log_error("Book returned fail")
            raise e  # נזרוק את השגיאה שוב


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

