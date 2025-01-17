import unittest
import os
import csv
import shutil
from unittest.mock import patch
from io import StringIO
from Library.Book import Book
from Library.Customer import Customer
from LibrarianNotificationObserver import LibrarianNotificationObserver
from Logger import Logger


class TestLibrarianNotificationObserver(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """
        הגדרת סביבת הטסט - יצירת קובץ משתמשים זמני וקובץ גיבוי
        """
        cls.base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        cls.test_users_file = os.path.join(cls.base_path, 'Test', 'test_users.csv')
        cls.original_users_file = os.path.join(cls.base_path, 'users.csv')

        # יצירת קובץ משתמשים לטסטים
        test_users_data = [
            ['librarian1', 'password1'],
            ['librarian2', 'password2'],
            ['librarian3', 'password3']
        ]

        with open(cls.test_users_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerows(test_users_data)

        # גיבוי קובץ המשתמשים המקורי אם קיים
        if os.path.exists(cls.original_users_file):
            cls.users_backup = os.path.join(cls.base_path, 'users_backup.csv')
            shutil.copy2(cls.original_users_file, cls.users_backup)

    def setUp(self):
        """
        הגדרת אובייקטים לשימוש בטסטים
        """
        self.logger = Logger()
        self.logger.disable_console_logs()  # השתקת לוגים לקונסול
        self.observer = LibrarianNotificationObserver(self.logger, self.test_users_file)

        # נתונים לדוגמה לשימוש בטסטים
        self.test_book = Book("Test Book", "Test Author", 3, "Fiction", 2023)
        self.test_customers = [
            Customer("Customer 1", "0501234567", "test1@test.com"),
            Customer("Customer 2", "0521234567", "test2@test.com")
        ]

    @classmethod
    def tearDownClass(cls):
        """
        ניקוי - מחיקת קובץ המשתמשים הזמני ושחזור המקורי
        """
        if os.path.exists(cls.test_users_file):
            os.remove(cls.test_users_file)

        # שחזור קובץ המשתמשים המקורי אם היה קיים
        if hasattr(cls, 'users_backup'):
            shutil.copy2(cls.users_backup, cls.original_users_file)
            os.remove(cls.users_backup)

    def test_get_librarians(self):
        """בדיקת קבלת רשימת הספרנים"""
        librarians = self.observer.get_librarians()

        # בדיקת מספר הספרנים
        self.assertEqual(len(librarians), 3)

        # בדיקת שמות הספרנים
        self.assertIn('librarian1', librarians)
        self.assertIn('librarian2', librarians)
        self.assertIn('librarian3', librarians)

    def test_get_librarians_no_file(self):
        """בדיקת התנהגות כשקובץ המשתמשים לא קיים"""
        observer = LibrarianNotificationObserver(self.logger, "nonexistent_file.csv")
        librarians = observer.get_librarians()
        self.assertEqual(len(librarians), 0)

    @patch('sys.stdout', new_callable=StringIO)
    def test_notification_on_return(self, mock_stdout):
        """בדיקת שליחת הודעה בעת החזרת ספר"""
        self.observer.update(self.test_book, [self.test_customers[0]], "return")
        output = mock_stdout.getvalue()

        # בדיקת תוכן ההודעה
        self.assertIn("The book 'Test Book' returned", output)
        self.assertIn("Customer 1", output)
        self.assertIn("0501234567", output)

        # בדיקה שההודעה נשלחה לכל הספרנים
        self.assertIn("librarian1", output)
        self.assertIn("librarian2", output)
        self.assertIn("librarian3", output)

    @patch('sys.stdout', new_callable=StringIO)
    def test_notification_on_addition(self, mock_stdout):
        """בדיקת שליחת הודעה בעת הוספת עותקים"""
        self.observer.update(self.test_book, self.test_customers, "addition")
        output = mock_stdout.getvalue()

        # בדיקת תוכן ההודעה
        self.assertIn(f"Were added {self.test_book.total_copies} copies", output)
        self.assertIn("Customer 1", output)
        self.assertIn("Customer 2", output)

        # בדיקה שההודעה נשלחה לכל הספרנים
        for librarian in ['librarian1', 'librarian2', 'librarian3']:
            self.assertIn(librarian, output)

    @patch('sys.stdout', new_callable=StringIO)
    def test_notification_invalid_event(self, mock_stdout):
        """בדיקת התנהגות עם סוג אירוע לא חוקי"""
        self.observer.update(self.test_book, self.test_customers, "invalid_event")
        output = mock_stdout.getvalue()
        self.assertEqual(output, "")  # לא אמורה להישלח הודעה

    def test_notification_no_customers(self):
        """בדיקת התנהגות כשאין לקוחות"""
        # שימוש ב-patch כדי לוודא שלא נשלחות הודעות
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            self.observer.update(self.test_book, [], "return")
            output = mock_stdout.getvalue()
            self.assertNotIn("were loaned to", output)

    def test_notification_with_special_characters(self):
        """בדיקת טיפול בתווים מיוחדים"""
        book = Book("Test's Book!", "Author & Co.", 1, "Sci-Fi/Fantasy", 2023)
        customer = Customer("O'Connor", "0501234567", "test@test.com")

        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            self.observer.update(book, [customer], "return")
            output = mock_stdout.getvalue()

            # בדיקה שהתווים המיוחדים נשמרו
            self.assertIn("Test's Book!", output)
            self.assertIn("O'Connor", output)


if __name__ == '__main__':
    unittest.main()