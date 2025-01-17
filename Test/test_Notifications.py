import unittest
import os
import csv
import shutil
from pathlib import Path
from unittest.mock import patch
from io import StringIO
from Library.Book import Book
from Library.Customer import Customer
from Library.LibrarianNotificationObserver import LibrarianNotificationObserver
from system.Logger import Logger


class TestLibrarianNotificationObserver(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """
        הגדרת סביבת הטסט - יצירת קובץ משתמשים זמני וקובץ גיבוי
        """
        cls.base_path = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        cls.files_dir = cls.base_path / 'files'
        os.makedirs(cls.files_dir, exist_ok=True)

        cls.users_file = cls.files_dir / 'users.csv'
        cls.users_backup = cls.files_dir / 'users_backup.csv'

        # יצירת קובץ משתמשים לטסטים
        test_users_data = [
            ['librarian1', 'password1'],
            ['librarian2', 'password2'],
            ['librarian3', 'password3']
        ]

        # גיבוי קובץ המשתמשים המקורי אם קיים
        if cls.users_file.exists():
            shutil.copy2(cls.users_file, cls.users_backup)

        # יצירת קובץ משתמשים לטסט
        with open(cls.users_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerows(test_users_data)

    def setUp(self):
        """
        הגדרת אובייקטים לשימוש בטסטים
        """
        self.logger = Logger()
        self.logger.disable_console_logs()  # השתקת לוגים לקונסול
        self.observer = LibrarianNotificationObserver(self.logger)

        # נתונים לדוגמה לשימוש בטסטים
        self.test_book = Book("Test Book", "Test Author", 3, "Fiction", 2023)
        self.test_customers = [
            Customer("Customer 1", "0501234567", "test1@test.com"),
            Customer("Customer 2", "0521234567", "test2@test.com")
        ]

    @classmethod
    def tearDownClass(cls):
        """
        ניקוי - שחזור קובץ המשתמשים המקורי
        """
        try:
            # שחזור קובץ המשתמשים המקורי אם היה קיים
            if cls.users_backup.exists():
                shutil.copy2(cls.users_backup, cls.users_file)
                os.remove(cls.users_backup)
            else:
                # אם לא היה קובץ מקורי, מוחקים את קובץ הטסט
                if cls.users_file.exists():
                    os.remove(cls.users_file)
        except Exception as e:
            print(f"Error during cleanup: {str(e)}")

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
        # יצירת observer חדש עם נתיב לקובץ לא קיים
        test_observer = LibrarianNotificationObserver(self.logger)
        test_observer.users_file = Path('nonexistent_file.csv')
        librarians = test_observer.get_librarians()
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

    @patch('sys.stdout', new_callable=StringIO)
    def test_notification_on_addition(self, mock_stdout):
        """בדיקת שליחת הודעה בעת הוספת עותקים"""
        self.observer.update(self.test_book, self.test_customers, "addition")
        output = mock_stdout.getvalue()

        # בדיקת תוכן ההודעה
        self.assertIn(f"Were added {self.test_book.total_copies} copies", output)
        self.assertIn("Customer 1", output)
        self.assertIn("Customer 2", output)

    @patch('sys.stdout', new_callable=StringIO)
    def test_notification_invalid_event(self, mock_stdout):
        """בדיקת התנהגות עם סוג אירוע לא חוקי"""
        self.observer.update(self.test_book, self.test_customers, "invalid_event")
        output = mock_stdout.getvalue()
        self.assertEqual(output, "")  # לא אמורה להישלח הודעה

    def test_notification_no_customers(self):
        """בדיקת התנהגות כשאין לקוחות"""
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