import os
import shutil
from unittest import TestCase
from Library.CSVHandler import CSVHandler
from Library.Customer import Customer
from Library.Librarian import Librarian
from Library.Book import Book
from Library.Search import Search


class TestLibrarian(TestCase):

    def setUp(self) -> None:
        self.librarian = Librarian()
        self.librarian.logger.disable_console_logs()

        # יצירת גיבוי של קובץ ה-CSV לפני הבדיקות
        self.path = os.path.join('..', 'Library', 'books.csv')
        self.backup_path = self.path + '.backup'
        shutil.copy(self.path, self.backup_path)

        # טוען את הספרים מקובץ CSV
        self.books = CSVHandler.load_books_from_csv(self.path)
        self.search = Search(self.books)
        self.assertTrue(self.books)  # ווידוא שהספרים נטענו כראוי

        # יוצרים לקוח לבדיקה
        self.customer = Customer("John Doe", "1234567890", "johndoe@example.com")
        self.customer_2 = Customer("noa", "9876543210", "johndoe@example.com")

    def tearDown(self) -> None:
        # מחזירים את קובץ ה-CSV למצבו ההתחלתי אחרי כל טסט
        shutil.copy(self.backup_path, self.path)
        os.remove(self.backup_path)

        # איפוס הספרים והלקוחות שהוספו במהלך הבדיקות
        self.librarian.books.clear()
        self.librarian.books_borrowed.clear()
        self.librarian.waiting_list.clear()

    def test_add_book(self):
        # טוען את הספרים מקובץ CSV
        book_1 = self.books.get("The Great Gatsby")  # טוען את הספר אם קיים בקובץ
        if not book_1:
            book_1 = Book("The Great Gatsby", "F. Scott Fitzgerald", 3, 3, "Classic", 1925)
            self.librarian.added(book_1)

        self.assertIn(book_1.title, self.librarian.books)
        self.assertEqual(self.librarian.books[book_1.title].total_copies, book_1.total_copies)

    def test_remove_book(self):
        # טוען את הספרים מקובץ CSV
        book_1 = self.books.get("Moby Dick")  # טוען את הספר אם קיים בקובץ
        if not book_1:
            book_1 = Book("Moby Dick", "Herman Melville", 1, "Adventure", 1851)
            self.librarian.added(book_1)

        self.librarian.removed(book_1)
        self.assertNotIn(book_1.title, self.librarian.books)

    def test_loan_book(self):
        # טוען את הספרים מקובץ CSV
        book_1 = self.books.get("To Kill a Mockingbird")  # טוען את הספר אם קיים בקובץ
        if not book_1:
            book_1 = Book("To Kill a Mockingbird", "Harper Lee", 2, 3, "Fiction", 1960)
            self.librarian.added(book_1)

        self.assertEqual(self.librarian.books[book_1.title].available_copies,0)

        # השאלה אחרי שספרות הזמינות נגמרות
        self.librarian.loaned(book_1, self.customer)
        self.librarian.loaned(book_1, self.customer)
        self.assertEqual(self.librarian.books[book_1.title].available_copies, 0)

    def test_return_book(self):
        # טוען את הספרים מקובץ CSV
        book_1 = self.books.get("Moby Dick")  # טוען את הספר אם קיים בקובץ
        if not book_1:
            book_1 = Book("To Kill a Mockingbird", "Harper Lee", 2, 3, "Fiction", 1960)
            self.librarian.added(book_1)

        # השאלה מוצלחת
        self.librarian.loaned(book_1, self.customer)
        self.assertEqual(self.librarian.books[book_1.title].available_copies, 0)

        # החזרת הספר
        self.librarian.returned(book_1)
        self.assertEqual(self.librarian.books[book_1.title].available_copies, 1)
        self.assertNotIn(book_1.title, self.librarian.books_borrowed)  # וידוא שהספר לא ברשימת ההשאלות

    # def test_add_customer_to_waiting_list(self):
    #     # טוען את הספרים מקובץ CSV
    #     book_1 = self.books.get("Moby Dick")  # טוען את הספר אם קיים בקובץ
    #     if not book_1:
    #         book_1 = Book("Moby Dick", "Herman Melville", 2, "Adventure", 1851)
    #         self.librarian.added(book_1)
    #
    #     # הלקוח יתווסף לרשימת המתנה כאשר אין עותקים זמינים
    #     self.librarian.loaned(book_1, self.customer)
    #     self.librarian.loaned(book_1, self.customer_2)
    #     self.assertIn(self.customer_2, self.librarian.waiting_list[book_1.title])
