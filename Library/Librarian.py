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
    #decorator for logging library operations using the class logger
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            try:
                # log debug message before executing the operation
                if args and hasattr(args[0], 'title'):
                    self.logger.log_debug(f"Attempting {operation_name}: title={args[0].title}")

                # run original function
                result = func(self, *args, **kwargs)

                # log success message
                self.logger.log_info(f"{operation_name} successfully")
                return result

            except Exception as e:
                # log error message
                self.logger.log_error(f"{operation_name} fail")
                raise e

        return wrapper
    return decorator


#represents a librarian managing the book collection and costumer interactions
class Librarian:
    #initializes the librarian, including loading books and waiting list
    def __init__(self, books_path=None, waiting_list_path=None) -> None:
        # sets default paths to files if none was specified
        if books_path is None or waiting_list_path is None:
            base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            files_dir = os.path.join(base_path, 'files')

            if books_path is None:
                books_path = os.path.join(files_dir, 'books.csv')
            if waiting_list_path is None:
                waiting_list_path = os.path.join(files_dir, 'waiting_list.csv')

        # basic start
        self.logger = Logger()
        self.books_borrowed = {}
        self.notification_subject = LibraryNotificationSubject()
        self.notification_observer = LibrarianNotificationObserver(self.logger)
        self.notification_subject.attach(self.notification_observer)

        # load books and waiting list from files
        self.books = CSVHandler.load_books_from_csv(books_path)
        self.waiting_list = CSVHandler.load_waiting_list_from_csv(waiting_list_path)

        # update loaned books status
        for title, book in self.books.items():
            if book.is_loaned == "Yes":
                book.available_copies = 0
                self.books_borrowed[title] = book.total_copies

    #retrieves the waiting list
    def get_waiting_list(self):
        return self.waiting_list

    #adds a book to library or updates number of copies
    @log_operation("book added")
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

    #removes book from library
    @log_operation("book removed")
    def removed(self, book: Book) -> bool:
        if book.title not in self.books:
            raise BookDoesNotExistException()

        if book.title in self.books_borrowed:
            raise RemovingBorrowedBookException()

        del self.books[book.title]
        self.save_books()
        return True

    #loans a book to costumer if there is an available copy
    @log_operation("book borrowed")
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

    #returns borrowed book to library.
    # if there is a waiting list for the book it loans it to the first costumer on the list
    @log_operation("book returned")
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

    #adds costumer to waiting list if no copies are available
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

    #creates a costumer object
    def create_customer(self):
        # requests costumer details
        name = input("Enter customer name: ")
        phone = input("Enter customer phone: ")
        email = input("Enter customer email: ")

        #create and return new costumer object
        customer = Customer(name, phone, email)

        return customer
    """
    returns most demanded books based on:
    1. the number of borrowed copies
    2. the size of the waiting list
    final demand score=number of borrowed copies+size of waiting list"""
    def get_most_demanded_books(self, limit=10):

        book_demand = []

        for title, book in self.books.items():
            # number of borrowed copies
            borrowed_copies = self.books_borrowed.get(title, 0)

            # number of people on waiting list
            waiting_list_count = len(self.waiting_list.get(title, []))

            # final demand score
            total_demand = borrowed_copies + waiting_list_count

            book_demand.append((
                title,
                total_demand,
                borrowed_copies,
                waiting_list_count
            ))

        # order from highest score to lowest
        sorted_books = sorted(book_demand, key=lambda x: x[1], reverse=True)

        # returns a list of the requested length
        return sorted_books[:limit]

    #saves the current state of the library's books to books.cvs
    def save_books(self):
        CSVHandler.save_books_to_csv(self.books)

    #saves the current state of the waiting list to waiting_list.cvs
    def save_waiting_list(self):
        CSVHandler.save_waiting_list_to_csv(self.waiting_list)
