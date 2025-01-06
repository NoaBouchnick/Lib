from unittest import TestCase

from Library.Customer import Customer
from Library.Librarian import Librarian
from Library.Book import Book


class TestLibrarian(TestCase):

    def setUp(self) -> None:
        self.librarian = Librarian()
        self.customer = Customer
        self.book_1 = Book("Harry Potter", "J.K. Rowling", 3, "Fantasy", 1997)
        self.book_2 = Book("The Hobbit", "J.R.R. Tolkien", 5, "Fantasy", 1937)

        self.librarian.logger.disable_console_logs()

    def test_add_book(self):
        self.librarian.added(self.book_1)
        self.assertIn("Harry Potter", self.librarian.books)
        self.assertEqual(self.librarian.books["Harry Potter"].total_copies, 3)  # בדיקת מספר עותקים

        # בדיקת הוספת עותקים לספר קיים
        self.librarian.added(self.book_1)
        self.assertEqual(self.librarian.books["Harry Potter"].total_copies, 6)  # 3 עותקים נוספו

    def test_remove_book(self):
        self.librarian.added(self.book_1)
        self.librarian.removed(self.book_1)
        self.assertNotIn("Harry Potter", self.librarian.books)  # הספר הוסר

        # בדיקת הסרת חלק מהעותקים
        self.librarian.added(self.book_2)
        self.librarian.removed(Book("The Hobbit", "J.R.R. Tolkien", 2, "Fantasy", 1937))
        self.assertEqual(self.librarian.books["The Hobbit"].total_copies, 3)

    def test_loan_book(self):
        self.librarian.added(self.book_1)
        customer = Customer("John Doe", "1234567890", "johndoe@example.com")
        self.librarian.loaned(self.book_1, customer)

        # בדיקת הפחתת עותקים זמינים
        self.assertEqual(self.librarian.books["Harry Potter"].available_copies, 2)

        # בדיקת ניסיון השאלה ללא עותקים זמינים
        for _ in range(3):  # לשאול את כל הספרים
            self.librarian.loaned(self.book_1, customer)
        self.assertEqual(self.librarian.books["Harry Potter"].available_copies, 0)

    def test_return_book(self):
        self.librarian.added(self.book_1)
        self.librarian.loaned(self.book_1, self.customer)
        self.librarian.returned(self.book_1)

        # בדיקת הגדלת עותקים זמינים לאחר החזרה
        self.assertEqual(self.librarian.books["Harry Potter"].available_copies, 3)

        # בדיקת החזרת ספר שלא קיים בספרייה
        non_existing_book = Book("Unknown", "Author", 1, "Genre", 2000)
        self.librarian.returned(non_existing_book)  # לא אמור להוסיף ספר חדש
        self.assertNotIn("Unknown", self.librarian.books)
