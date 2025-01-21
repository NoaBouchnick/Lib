import os
from functools import wraps

from Error.BookDoesNotExistException import BookDoesNotExistException
from Error.CustomException import CustomException
from Error.NegativeCopiesException import NegativeCopiesException
from Error.NoBorrowedCopiesException import NoBorrowedCopiesException
from Error.NoCopyAvailableException import NoCopyAvailableException
from Error.NonIntegerValueException import NonIntegerValueException
from Error.RemovingBorrowedBookException import RemovingBorrowedBookException
from Books.Book import Book
from Library.Observer import LibraryNotificationSubject
from system.CSVHandler import CSVHandler
from Library.Customer import Customer
from Library.LibrarianNotificationObserver import LibrarianNotificationObserver
from system.Logger import Logger


def log_operation(operation_name):
    """
    דקורטור לתיעוד פעולות בספרייה - משתמש בלוגר של המחלקה
    """
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            try:
                # רישום הודעת דיבוג לפני ביצוע הפעולה
                if args and hasattr(args[0], 'title'):
                    self.logger.log_debug(f"Attempting {operation_name}: title={args[0].title}")

                # הרצת הפונקציה המקורית
                result = func(self, *args, **kwargs)

                # רישום הודעת הצלחה
                self.logger.log_info(f"{operation_name} completed successfully")
                return result

            except Exception as e:
                # רישום הודעת שגיאה
                self.logger.log_error(f"{operation_name} failed")
                raise e

        return wrapper
    return decorator


class Librarian:
    def __init__(self, books_path=None, waiting_list_path=None) -> None:
        # קביעת נתיבים ברירת מחדל אם לא התקבלו
        if books_path is None or waiting_list_path is None:
            base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            files_dir = os.path.join(base_path, 'files')

            if books_path is None:
                books_path = os.path.join(files_dir, 'books.csv')
            if waiting_list_path is None:
                waiting_list_path = os.path.join(files_dir, 'waiting_list.csv')

        # אתחול בסיסי
        self.logger = Logger()
        self.books_borrowed = {}
        self.notification_subject = LibraryNotificationSubject()
        self.notification_observer = LibrarianNotificationObserver(self.logger)
        self.notification_subject.attach(self.notification_observer)

        # טעינת ספרים ורשימת המתנה מהקבצים
        self.books = CSVHandler.load_books_from_csv(books_path)
        self.waiting_list = CSVHandler.load_waiting_list_from_csv(waiting_list_path)

        # עדכון מצב הספרים המושאלים
        for title, book in self.books.items():
            if book.is_loaned == "Yes":
                book.available_copies = 0
                self.books_borrowed[title] = book.total_copies

    def get_waiting_list(self):
        return self.waiting_list

    @log_operation("add book")
    def added(self, book: Book):
        if not isinstance(book.total_copies, int) or not isinstance(book.year, int):
            raise NonIntegerValueException()

        if book.total_copies <= 0:
            raise NegativeCopiesException()

        customers_to_notify = []
        if book.title in self.books:
            existing_book = self.books[book.title]
            borrowed_copies = self.books_borrowed.get(book.title, 0)

            existing_book.total_copies += book.total_copies
            added_copies = book.total_copies
            existing_book.available_copies = existing_book.total_copies - borrowed_copies

            if book.title in self.waiting_list and self.waiting_list[book.title]:
                for _ in range(min(added_copies, len(self.waiting_list[book.title]))):
                    next_customer = self.waiting_list[book.title].pop(0)
                    customers_to_notify.append(next_customer)
                    self.loaned(book)

                self.save_waiting_list()
                if customers_to_notify:
                    self.notification_subject.notify(book, customers_to_notify, "addition")

            if existing_book.available_copies == 0:
                existing_book.is_loaned = "Yes"
            else:
                existing_book.is_loaned = "No"
        else:
            self.books[book.title] = book

        self.save_books()

    @log_operation("remove book")
    def removed(self, book: Book) -> bool:
        if book.title not in self.books:
            raise BookDoesNotExistException()

        if book.title in self.books_borrowed:
            raise RemovingBorrowedBookException()

        del self.books[book.title]
        self.save_books()
        return True

    @log_operation("loan book")
    def loaned(self, book: Book) -> bool:
        if book.title in self.books:
            current_book = self.books[book.title]

            if current_book.available_copies > 0:
                current_book.available_copies -= 1
                self.books_borrowed[book.title] = self.books_borrowed.get(book.title, 0) + 1

                if current_book.available_copies == 0:
                    current_book.is_loaned = "Yes"

                self.save_books()
                return True
            else:
                raise NoCopyAvailableException()
        else:
            raise BookDoesNotExistException()

    @log_operation("return book")
    def returned(self, book: Book) -> bool:
        if book.title not in self.books:
            raise BookDoesNotExistException()

        if book.title not in self.books_borrowed:
            raise NoBorrowedCopiesException()

        current_book = self.books[book.title]
        current_book.available_copies += 1

        self.books_borrowed[book.title] -= 1
        if self.books_borrowed[book.title] == 0:
            del self.books_borrowed[book.title]
            current_book.is_loaned = "No"
        else:
            current_book.is_loaned = "Yes"

        if book.title in self.waiting_list and self.waiting_list[book.title]:
            next_customer = self.waiting_list[book.title].pop(0)
            self.save_waiting_list()
            self.notification_subject.notify(book, [next_customer], "return")
            self.loaned(book)

        self.save_books()
        return True

    @log_operation("add to waiting list")
    def waiting_for_book(self, book, customer=None):
        if customer is None:
            customer = self.create_customer()

        if book.title in self.waiting_list:
            for existing_customer in self.waiting_list[book.title]:
                if existing_customer.name == customer.name and existing_customer.phone == customer.phone:
                    raise ValueError(f"Customer {customer.name} is already in waiting list for book '{book.title}'")
        else:
            self.waiting_list[book.title] = []

        self.waiting_list[book.title].append(customer)
        self.save_waiting_list()

    def create_customer(self):
        # בקשת פרטי הלקוח מהמשתמש
        name = input("Enter customer name: ")
        phone = input("Enter customer phone: ")
        email = input("Enter customer email: ")

        # יצירת אובייקט לקוח חדש
        customer = Customer(name, phone, email)

        return customer

    def get_most_demanded_books(self, limit=10):
        """
        מחזיר את הספרים המבוקשים ביותר על פי:
        1. כמות העותקים המושאלים
        2. גודל רשימת ההמתנה

        Args:
            limit (int): כמות הספרים להחזרה (ברירת מחדל: 10)

        Returns:
            list: רשימה של טאפלים (שם הספר, ציון ביקוש כולל, עותקים מושאלים, אנשים בהמתנה)
        """
        book_demand = []

        for title, book in self.books.items():
            # מספר העותקים המושאלים
            borrowed_copies = self.books_borrowed.get(title, 0)

            # מספר האנשים ברשימת ההמתנה
            waiting_list_count = len(self.waiting_list.get(title, []))

            # הציון הכולל הוא סכום של העותקים המושאלים ואורך רשימת ההמתנה
            total_demand = borrowed_copies + waiting_list_count

            book_demand.append((
                title,
                total_demand,
                borrowed_copies,
                waiting_list_count
            ))

        # מיון לפי הציון הכולל בסדר יורד
        sorted_books = sorted(book_demand, key=lambda x: x[1], reverse=True)

        # החזרת הכמות המבוקשת של ספרים
        return sorted_books[:limit]

    def save_books(self):
        CSVHandler.save_books_to_csv(self.books)

    def save_waiting_list(self):
        """שומר את רשימת ההמתנה."""
        CSVHandler.save_waiting_list_to_csv(self.waiting_list)
