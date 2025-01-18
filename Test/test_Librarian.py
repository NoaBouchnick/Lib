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
from Library.Book import Book
from Library.Customer import Customer


class TestLibrarian(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """הכנת סביבת טסט"""
        # השבתת לוגים
        logging.disable(logging.CRITICAL)

        # נתיב הבסיס
        cls.base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        cls.files_dir = os.path.join(cls.base_path, 'files')

        # יצירת גיבוי מלא של הקבצים
        cls.books_backup = os.path.join(cls.files_dir, 'books_backup.csv')
        cls.waiting_list_backup = os.path.join(cls.files_dir, 'waiting_list_backup.csv')

        # יצירת גיבוי מהקבצים המקוריים
        shutil.copy2(
            os.path.join(cls.files_dir, 'books.csv'),
            cls.books_backup
        )
        shutil.copy2(
            os.path.join(cls.files_dir, 'waiting_list.csv'),
            cls.waiting_list_backup
        )

    @classmethod
    def tearDownClass(cls):
        """החזרה למצב מקורי"""
        # החזרת הקבצים המקוריים מהגיבוי
        shutil.copy2(cls.books_backup, os.path.join(cls.files_dir, 'books.csv'))
        shutil.copy2(cls.waiting_list_backup, os.path.join(cls.files_dir, 'waiting_list.csv'))

        # מחיקת קבצי הגיבוי
        os.remove(cls.books_backup)
        os.remove(cls.waiting_list_backup)

    def setUp(self):
        """הכנת אובייקט Librarian לכל טסט"""
        self.librarian = Librarian(
            books_path=os.path.join(self.base_path, 'files', 'books.csv'),
            waiting_list_path=os.path.join(self.base_path, 'files', 'waiting_list.csv')
        )
        # השבתת לוגים של הספרייה
        self.librarian.logger.disable_console_logs()

    def test_add_book_negative_copies(self):
        """בדיקת הוספת ספר עם עותקים שליליים"""
        book = Book("Negative Test", "Author Name", -5, "Genre", 2021)
        with self.assertRaises(NegativeCopiesException):
            self.librarian.added(book)

    def test_add_book_non_integer_copies(self):
        """בדיקת הוספת ספר עם עותקים שאינם מספר שלם"""
        book = Book("Non-integer Test", "Author Name", 3.5, "Genre", 2021)
        with self.assertRaises(NonIntegerValueException):
            self.librarian.added(book)

    def test_remove_nonexistent_book(self):
        """בדיקת הסרת ספר שאינו קיים"""
        book = Book("Nonexistent Book", "Author Name", 1, "Genre", 2021)
        with self.assertRaises(BookDoesNotExistException):
            self.librarian.removed(book)

    def test_remove_borrowed_book(self):
        """בדיקת הסרת ספר מושאל"""
        book = self.librarian.books["1984"]  # ספר מושאל בספרייה
        with self.assertRaises(RemovingBorrowedBookException):
            self.librarian.removed(book)

    def test_loan_nonexistent_book(self):
        """בדיקת השאלת ספר שאינו קיים"""
        book = Book("Nonexistent Book", "Author Name", 1, "Genre", 2021)
        with self.assertRaises(BookDoesNotExistException):
            self.librarian.loaned(book)

    def test_loan_no_available_copies(self):
        """בדיקת השאלת ספר ללא עותקים זמינים"""
        book = self.librarian.books["The Divine Comedy"]  # ספר ללא עותקים זמינים
        with self.assertRaises(NoCopyAvailableException):
            self.librarian.loaned(book)

    def test_return_nonexistent_book(self):
        """בדיקת החזרת ספר שאינו קיים"""
        book = Book("Nonexistent Book", "Author Name", 1, "Genre", 2021)
        with self.assertRaises(BookDoesNotExistException):
            self.librarian.returned(book)

    def test_return_no_borrowed_copies(self):
        """בדיקת החזרת ספר שאינו מושאל"""
        book = self.librarian.books["The Great Gatsby"]  # ספר שאינו מושאל
        with self.assertRaises(NoBorrowedCopiesException):
            self.librarian.returned(book)

    def test_waiting_for_book(self):
        """בדיקת הוספת לקוח לרשימת המתנה"""
        borrowed_book = self.librarian.books["1984"]  # ספר מושאל
        customer = Customer("John Doe", "0501234567", "john@example.com")

        self.librarian.waiting_for_book(borrowed_book, customer)

        self.assertIn(borrowed_book.title, self.librarian.waiting_list)
        self.assertIn(customer, self.librarian.waiting_list[borrowed_book.title])

        # בדיקת כפילות לקוחות
        with self.assertRaises(ValueError):
            self.librarian.waiting_for_book(borrowed_book, customer)


if __name__ == '__main__':
    unittest.main()