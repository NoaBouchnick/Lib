import unittest
import os
import csv
import shutil
from Library.Book import Book
from Library.Customer import Customer
from Library.Librarian import Librarian
from Error.BookDoesNotExistException import BookDoesNotExistException
from Error.NegativeCopiesException import NegativeCopiesException
from Error.NonIntegerValueException import NonIntegerValueException
from Error.NoCopyAvailableException import NoCopyAvailableException
from Error.NoBorrowedCopiesException import NoBorrowedCopiesException
from Error.RemovingBorrowedBookException import RemovingBorrowedBookException


class TestLibrarian(unittest.TestCase):
    books_file = None
    waiting_list_file = None
    books_backup = None
    waiting_list_backup = None
    base_path = None

    @classmethod
    def setUpClass(cls):
        """
        פעולות שמתבצעות פעם אחת לפני כל הטסטים:
        גיבוי הקבצים המקוריים והשתקת לוגים
        """
        # נתיבים לקבצים המקוריים
        cls.base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        cls.books_file = os.path.join(cls.base_path, 'Library', 'books.csv')
        cls.waiting_list_file = os.path.join(cls.base_path, '../waiting_list.csv')

        # יצירת גיבויים
        cls.books_backup = os.path.join(cls.base_path, 'Library', 'books_backup.csv')
        cls.waiting_list_backup = os.path.join(cls.base_path, '../waiting_list_backup.csv')

        # העתקת הקבצים המקוריים לגיבוי
        shutil.copy2(cls.books_file, cls.books_backup)
        if os.path.exists(cls.waiting_list_file):
            shutil.copy2(cls.waiting_list_file, cls.waiting_list_backup)

        # יצירת ספרייה ראשונית להשתקת הלוגים
        temp_librarian = Librarian(cls.books_file)
        temp_librarian.logger.disable_console_logs()

    def setUp(self):
        """
        פעולות שמתבצעות לפני כל טסט:
        שחזור הקבצים המקוריים מהגיבוי
        """
        # שחזור הקבצים מהגיבוי
        shutil.copy2(self.books_backup, self.books_file)
        if os.path.exists(self.waiting_list_backup):
            shutil.copy2(self.waiting_list_backup, self.waiting_list_file)

        # יצירת מופע Librarian חדש והשתקת הלוגים שלו
        self.librarian = Librarian(self.books_file)
        self.librarian.logger.disable_console_logs()

    @classmethod
    def tearDownClass(cls):
        """
        פעולות שמתבצעות פעם אחת אחרי כל הטסטים:
        שחזור הקבצים המקוריים ומחיקת הגיבויים
        """
        try:
            # שחזור קובץ הספרים המקורי
            if os.path.exists(cls.books_backup):
                shutil.copy2(cls.books_backup, cls.books_file)

            # טיפול בקובץ רשימת ההמתנה
            original_waiting_list_existed = os.path.exists(cls.waiting_list_backup)

            # שחזור או מחיקה של קובץ רשימת ההמתנה
            if original_waiting_list_existed:
                # אם היה קובץ מקורי - משחזרים אותו
                shutil.copy2(cls.waiting_list_backup, cls.waiting_list_file)
            else:
                # אם לא היה קובץ מקורי - מוחקים את הקובץ שנוצר
                if os.path.exists(cls.waiting_list_file):
                    os.remove(cls.waiting_list_file)

        except Exception as e:
            print(f"Error during file restoration: {str(e)}")

        finally:
            # מחיקת קבצי הגיבוי
            for backup_file in [cls.books_backup, cls.waiting_list_backup]:
                if os.path.exists(backup_file):
                    try:
                        os.remove(backup_file)
                    except Exception as e:
                        print(f"Error removing backup file {backup_file}: {str(e)}")

            # וידוא סופי שקובץ רשימת ההמתנה נמחק אם לא היה קובץ מקורי
            if not original_waiting_list_existed and os.path.exists(cls.waiting_list_file):
                try:
                    os.remove(cls.waiting_list_file)
                except Exception as e:
                    print(f"Error during final cleanup: {str(e)}")

    def test_add_book_normal(self):
        """בדיקת הוספת ספר במקרה רגיל"""
        book = Book("New Test Book", "Test Author", 3, "Fiction", 2023)
        self.librarian.added(book)
        self.assertIn("New Test Book", self.librarian.books)
        self.assertEqual(self.librarian.books["New Test Book"].total_copies, 3)

    def test_add_book_negative_copies(self):
        """בדיקת הוספת ספר עם מספר עותקים שלילי"""
        book = Book("Negative Book", "Author", -1, "Fiction", 2023)
        with self.assertRaises(NegativeCopiesException):
            self.librarian.added(book)

    def test_add_book_non_integer_copies(self):
        """בדיקת הוספת ספר עם מספר עותקים לא שלם"""
        book = Book("Float Book", "Author", 3.5, "Fiction", 2023)
        with self.assertRaises(NonIntegerValueException):
            self.librarian.added(book)

    def test_add_existing_book(self):
        """בדיקת הוספת עותקים לספר קיים"""
        # משתמשים בספר קיים - "The Great Gatsby"
        book = Book("The Great Gatsby", "F. Scott Fitzgerald", 2, "Classic", 1925)
        initial_copies = self.librarian.books["The Great Gatsby"].total_copies
        self.librarian.added(book)
        final_copies = self.librarian.books["The Great Gatsby"].total_copies
        self.assertEqual(final_copies, initial_copies + 2)

    def test_remove_book_normal(self):
        """בדיקת הסרת ספר במקרה רגיל"""
        # משתמשים בספר שלא מושאל - "The Great Gatsby"
        book = self.librarian.books["The Great Gatsby"]
        result = self.librarian.removed(book)
        self.assertTrue(result)
        self.assertNotIn("The Great Gatsby", self.librarian.books)

    def test_remove_borrowed_book(self):
        """בדיקת הסרת ספר שמושאל"""
        # משתמשים בספר שמושאל - "1984"
        book = self.librarian.books["1984"]
        with self.assertRaises(RemovingBorrowedBookException):
            self.librarian.removed(book)

    def test_loan_and_return_flow(self):
        """בדיקת תהליך מלא של השאלה והחזרה"""
        # משתמשים בספר עם מספר עותקים זמינים - "The Great Gatsby"
        book = self.librarian.books["The Great Gatsby"]
        initial_copies = book.available_copies

        # השאלת ספר
        self.assertTrue(self.librarian.loaned(book))
        self.assertEqual(book.available_copies, initial_copies - 1)

        # החזרת ספר
        self.assertTrue(self.librarian.returned(book))
        self.assertEqual(book.available_copies, initial_copies)

    def test_loan_unavailable_book(self):
        """בדיקת השאלת ספר כשאין עותקים זמינים"""
        # משתמשים בספר מושאל לחלוטין - "The Divine Comedy"
        book = self.librarian.books["The Divine Comedy"]
        with self.assertRaises(NoCopyAvailableException):
            self.librarian.loaned(book)

    def test_waiting_list_and_notification(self):
        """בדיקת רשימת המתנה והודעות"""
        # משתמשים בספר מושאל - "1984"
        book = self.librarian.books["1984"]

        # הוספת לקוחות לרשימת המתנה
        customer1 = Customer("Customer 1", "0501234567", "test1@test.com")
        customer2 = Customer("Customer 2", "0521234567", "test2@test.com")

        self.librarian.waiting_for_book(book, customer1)
        self.librarian.waiting_for_book(book, customer2)

        # בדיקת גודל רשימת ההמתנה
        self.assertEqual(len(self.librarian.waiting_list[book.title]), 2)

        # החזרת ספר והשאלה אוטומטית ללקוח הראשון
        self.librarian.returned(book)
        self.assertEqual(len(self.librarian.waiting_list[book.title]), 1)

    def test_get_most_demanded_books(self):
        """בדיקת דירוג הספרים המבוקשים ביותר"""
        # הוספת לקוחות לרשימות המתנה של ספרים מבוקשים
        high_demand_books = [
            ("1984", 3),  # 5 עותקים כבר מושאלים
            ("A Game of Thrones", 2),  # 5 עותקים כבר מושאלים
            ("The Hobbit", 1)  # 4 עותקים כבר מושאלים
        ]

        # הוספת אנשים לרשימות המתנה
        for book_title, num_customers in high_demand_books:
            book = self.librarian.books[book_title]
            for i in range(num_customers):
                phone = f"050{str(i + 1).zfill(7)}"
                customer = Customer(f"Customer {i + 1}", phone, f"test{i + 1}@test.com")
                self.librarian.waiting_for_book(book, customer)

        # בדיקת התוצאות
        results = self.librarian.get_most_demanded_books(limit=3)

        # 1984: 5 מושאלים + 3 בהמתנה = 8
        self.assertEqual(results[0][0], "1984")
        self.assertEqual(results[0][1], 8)

        # A Game of Thrones: 5 מושאלים + 2 בהמתנה = 7
        self.assertEqual(results[1][0], "A Game of Thrones")
        self.assertEqual(results[1][1], 7)

        # The Hobbit: 4 מושאלים + 1 בהמתנה = 5
        self.assertEqual(results[2][0], "The Hobbit")
        self.assertEqual(results[2][1], 5)


if __name__ == '__main__':
    unittest.main()