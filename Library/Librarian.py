import os

from Error.BookDoesNotExistException import BookDoesNotExistException
from Error.CustomException import CustomException
from Error.NegativeCopiesException import NegativeCopiesException
from Error.NoBorrowedCopiesException import NoBorrowedCopiesException
from Error.NoCopyAvailableException import NoCopyAvailableException
from Error.NonIntegerValueException import NonIntegerValueException
from Error.RemovingBorrowedBookException import RemovingBorrowedBookException
from Library.Observer import LibraryNotificationSubject
from Library.Book import Book
from system.CSVHandler import CSVHandler
from Library.Customer import Customer
from Library.LibrarianNotificationObserver import LibrarianNotificationObserver
from system.Logger import Logger


class Librarian:
    def __init__(self, file_path=None) -> None:
        if file_path is None:
            base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            file_path = os.path.join(base_path, 'files', 'books.csv')

        # טוען ספרים מקובץ CSV
        self.books = CSVHandler.load_books_from_csv(file_path)
        self.waiting_list = CSVHandler.load_waiting_list_from_csv()
        self.books_borrowed = {}
        for title, book in self.books.items():
            if book.is_loaned == "Yes":
                book.available_copies = 0
                self.books_borrowed[title] = book.total_copies

        self.logger = Logger()
        self.waiting_list = {}  # Book, customer
        self.notification_subject = LibraryNotificationSubject()
        self.notification_observer = LibrarianNotificationObserver(self.logger)
        self.notification_subject.attach(self.notification_observer)

    def get_waiting_list(self):
        return self.waiting_list

    def added(self, book: Book):
        try:
            self.logger.log_debug(
                f"Attempting to add book: title={book.title}, total_copies={book.total_copies}, year={book.year}")

            if not isinstance(book.total_copies, int) or not isinstance(book.year, int):
                raise NonIntegerValueException()

            if book.total_copies <= 0:
                raise NegativeCopiesException()

            customers_to_notify = []
            if book.title in self.books:
                existing_book = self.books[book.title]
                borrowed_copies = self.books_borrowed.get(book.title, 0)

                # עדכון מספר העותקים הכולל
                existing_book.total_copies += book.total_copies
                added_copies = book.total_copies

                # העותקים הזמינים הם: סך כל העותקים פחות העותקים המושאלים
                existing_book.available_copies = existing_book.total_copies - borrowed_copies

                # טיפול ברשימת המתנה אם קיימת
                if book.title in self.waiting_list and self.waiting_list[book.title]:
                    # מעבר על כמות העותקים שנוספו
                    for _ in range(min(added_copies, len(self.waiting_list[book.title]))):
                        next_customer = self.waiting_list[book.title].pop(0)
                        customers_to_notify.append(next_customer)
                        self.loaned(book)  # משאיל את הספר ללקוח הבא ברשימה

                    self.save_waiting_list()
                    if customers_to_notify:
                        self.notification_subject.notify(book, customers_to_notify, "addition")

                # עדכון סטטוס ההשאלה
                if existing_book.available_copies == 0:
                    existing_book.is_loaned = "Yes"
                else:
                    existing_book.is_loaned = "No"
            else:
                self.books[book.title] = book

            self.logger.log_info("Book added successfully")
            self.save_books()

        except CustomException as e:
            self.logger.log_error("Book added fail")
            raise e

        except Exception as e:
            self.logger.log_error("Book added fail")
            raise e

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

    def loaned(self, book: Book) -> bool:
        try:
            if book.title in self.books:
                current_book = self.books[book.title]

                if current_book.available_copies > 0:
                    current_book.available_copies -= 1
                    self.books_borrowed[book.title] = self.books_borrowed.get(book.title, 0) + 1

                    if current_book.available_copies == 0:
                        current_book.is_loaned = "Yes"

                    self.logger.log_info("book loaned successfully")
                    self.save_books()
                    return True
                else:
                    raise NoCopyAvailableException()
            else:
                raise BookDoesNotExistException()

        except CustomException as e:
            self.logger.log_error(f"Book loaned fail")
            raise e

        except Exception as e:
            self.logger.log_error("Book loaned fail")
            raise e

    def returned(self, book: Book) -> bool:
        try:
            if book.title not in self.books:
                raise BookDoesNotExistException("Book does not exist in the system.")

            if book.title not in self.books_borrowed:
                raise NoBorrowedCopiesException("There are no borrowed copies of this book.")

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

            self.logger.log_info("Book returned successfully")
            self.save_books()
            return True

        except CustomException as e:
            self.logger.log_error("Book returned fail")
            raise e

        except Exception as e:
            self.logger.log_error("Book returned fail")
            raise e

    def waiting_for_book(self, book, customer=None):
        """הוספת לקוח לרשימת ההמתנה."""
        if customer is None:
            customer = self.create_customer()

        # בדיקה אם הלקוח כבר רשום לספר זה
        if book.title in self.waiting_list:
            # בדיקה לפי שם וטלפון (או כל זיהוי אחר שאתה רוצה)
            for existing_customer in self.waiting_list[book.title]:
                if existing_customer.name == customer.name and existing_customer.phone == customer.phone:
                    raise ValueError(f"Customer {customer.name} is already in waiting list for book '{book.title}'")
        else:
            self.waiting_list[book.title] = []

        self.waiting_list[book.title].append(customer)
        self.logger.log_info(f" {customer} added to waiting list for book '{book.title}'")
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
