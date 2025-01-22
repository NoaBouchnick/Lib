import unittest
import os
import shutil
import logging
from Error.BookDoesNotExistException import BookDoesNotExistException
from Error.NegativeCopiesException import NegativeCopiesException
from Error.NoBorrowedCopiesException import NoBorrowedCopiesException
from Error.NoCopyAvailableException import NoCopyAvailableException
from Error.NonIntegerValueException import NonIntegerValueException
from Error.RemovingBorrowedBookException import RemovingBorrowedBookException
from Library.Librarian import Librarian
from Books.Book import Book
from Library.Customer import Customer

#unit tests for the librarian class
class TestLibrarian(unittest.TestCase):
    #sets up the test environment before running tests
    @classmethod
    def setUpClass(cls):
        #disables logging
        logging.disable(logging.CRITICAL)

        cls.base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        cls.files_dir = os.path.join(cls.base_path, 'files')

        # backup original files
        cls.books_backup = os.path.join(cls.files_dir, 'books_backup.csv')
        cls.waiting_list_backup = os.path.join(cls.files_dir, 'waiting_list_backup.csv')

        shutil.copy2(
            os.path.join(cls.files_dir, 'books.csv'),
            cls.books_backup
        )
        shutil.copy2(
            os.path.join(cls.files_dir, 'waiting_list.csv'),
            cls.waiting_list_backup
        )

    #restores the original state after running the tests
    @classmethod
    def tearDownClass(cls):
        shutil.copy2(cls.books_backup, os.path.join(cls.files_dir, 'books.csv'))
        shutil.copy2(cls.waiting_list_backup, os.path.join(cls.files_dir, 'waiting_list.csv'))

        # deletes backup files
        os.remove(cls.books_backup)
        os.remove(cls.waiting_list_backup)

    #prepares a fresh librarian instance before each test
    def setUp(self):
        self.librarian = Librarian(
            books_path=os.path.join(self.base_path, 'files', 'books.csv'),
            waiting_list_path=os.path.join(self.base_path, 'files', 'waiting_list.csv')
        )
        # disables console logging for cleaner output
        self.librarian.logger.disable_console_logs()

    #tests adding book with negative copies
    def test_add_book_negative_copies(self):
        book = Book("Negative Test", "Author Name", -5, "Genre", 2021)
        with self.assertRaises(NegativeCopiesException):
            self.librarian.added(book)

    #tests adding book with a non integer number of copies
    def test_add_book_non_integer_copies(self):
        book = Book("Non-integer Test", "Author Name", 3.5, "Genre", 2021)
        with self.assertRaises(NonIntegerValueException):
            self.librarian.added(book)

    #tests removing non existant book
    def test_remove_nonexistent_book(self):
        book = Book("Nonexistent Book", "Author Name", 1, "Genre", 2021)
        with self.assertRaises(BookDoesNotExistException):
            self.librarian.removed(book)

    #tests removing borrowed book
    def test_remove_borrowed_book(self):
        book = self.librarian.books["1984"]
        with self.assertRaises(RemovingBorrowedBookException):
            self.librarian.removed(book)

    #tests loaning nom existant book
    def test_loan_nonexistent_book(self):
        book = Book("Nonexistent Book", "Author Name", 1, "Genre", 2021)
        with self.assertRaises(BookDoesNotExistException):
            self.librarian.loaned(book)

    #tests loaning book with no available copies
    def test_loan_no_available_copies(self):
        book = self.librarian.books["The Divine Comedy"]
        with self.assertRaises(NoCopyAvailableException):
            self.librarian.loaned(book)

    #tests returning non existant book
    def test_return_nonexistent_book(self):
        book = Book("Nonexistent Book", "Author Name", 1, "Genre", 2021)
        with self.assertRaises(BookDoesNotExistException):
            self.librarian.returned(book)

    #tests returning book with no loaned copies
    def test_return_no_borrowed_copies(self):
        book = self.librarian.books["The Great Gatsby"]
        with self.assertRaises(NoBorrowedCopiesException):
            self.librarian.returned(book)

    #tests adding costumer to the waiting list for a book
    def test_waiting_for_book(self):
        borrowed_book = self.librarian.books["1984"]
        customer = Customer("John Doe", "0501234567", "john@example.com")

        self.librarian.waiting_for_book(borrowed_book, customer)

        self.assertIn(borrowed_book.title, self.librarian.waiting_list)
        self.assertIn(customer, self.librarian.waiting_list[borrowed_book.title])

        # checks for duplicate costumers
        with self.assertRaises(ValueError):
            self.librarian.waiting_for_book(borrowed_book, customer)


if __name__ == '__main__':
    unittest.main()