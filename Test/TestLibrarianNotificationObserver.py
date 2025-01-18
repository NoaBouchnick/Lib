import unittest
import os
import csv
import tempfile
import logging
from pathlib import Path
from Library.Book import Book
from Library.Customer import Customer
from system.Logger import Logger
from Library.LibrarianNotificationObserver import LibrarianNotificationObserver


class TestLibrarianNotificationObserver(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """הכנת סביבת טסט"""
        # השבתת לוגים
        logging.disable(logging.CRITICAL)

    def setUp(self):
        """הכנת סביבת טסט לכל מבחן"""
        # יצירת לוגר זמני
        self.logger = Logger()
        self.logger.disable_console_logs()

        # יצירת קובץ משתמשים זמני
        self.temp_dir = tempfile.mkdtemp()
        self.temp_users_file = os.path.join(self.temp_dir, 'users.csv')

        # כתיבת נתוני משתמשים לקובץ הזמני
        with open(self.temp_users_file, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerows([
                ['נועה'],
                ['אביב'],
                ['דני']
            ])

        # יצירת אובייקט LibrarianNotificationObserver עם הקובץ הזמני
        self.notification_observer = LibrarianNotificationObserver(self.logger)
        self.notification_observer.users_file = Path(self.temp_users_file)

    def tearDown(self):
        """ניקוי סביבת הטסט"""
        # מחיקת הקובץ הזמני
        os.unlink(self.temp_users_file)
        os.rmdir(self.temp_dir)

    def test_get_librarians(self):
        """בדיקת שליפת ספרנים מקובץ המשתמשים"""
        librarians = self.notification_observer.get_librarians()

        # בדיקה שנשלפו כל הספרנים
        expected_librarians = ['נועה', 'אביב', 'דני']
        self.assertEqual(len(librarians), 3)
        self.assertEqual(set(librarians), set(expected_librarians))

    def test_update_with_return_event(self):
        """בדיקת עדכון עבור אירוע החזרת ספר"""
        book = Book("1984", "George Orwell", 5, "Dystopian", 1949)
        customers = [
            Customer("לקוח 1", "0501234567", "customer1@example.com"),
            Customer("לקוח 2", "0521234567", "customer2@example.com")
        ]

        # שמירת הודעות שנשלחו (במקום הדפסה)
        sent_messages = []

        # החלפת השיטה המקורית במתודה שתשמור את ההודעות
        original_send_notification = self.notification_observer._send_notification

        def mock_send_notification(librarian, message):
            sent_messages.append((librarian, message))

        self.notification_observer._send_notification = mock_send_notification

        try:
            # הפעלת העדכון
            self.notification_observer.update(book, customers, "return")

            # בדיקה שנשלחו הודעות לכל הספרנים
            self.assertEqual(len(sent_messages), 3)

            # בדיקת תוכן ההודעות
            for librarian, message in sent_messages:
                self.assertIn("The book '1984' returned and loaned to:", message)
                for customer in customers:
                    self.assertIn(customer.name, message)
                    self.assertIn(customer.phone, message)
                    self.assertIn(customer.email, message)

        finally:
            # החזרת המתודה המקורית
            self.notification_observer._send_notification = original_send_notification

    def test_update_with_addition_event(self):
        """בדיקת עדכון עבור אירוע הוספת ספרים"""
        book = Book("The Hobbit", "J.R.R. Tolkien", 3, "Fantasy", 1937)
        customers = [
            Customer("לקוח 3", "0531234567", "customer3@example.com"),
            Customer("לקוח 4", "0541234567", "customer4@example.com")
        ]

        # שמירת הודעות שנשלחו (במקום הדפסה)
        sent_messages = []

        # החלפת השיטה המקורית במתודה שתשמור את ההודעות
        original_send_notification = self.notification_observer._send_notification

        def mock_send_notification(librarian, message):
            sent_messages.append((librarian, message))

        self.notification_observer._send_notification = mock_send_notification

        try:
            # הפעלת העדכון
            self.notification_observer.update(book, customers, "addition")

            # בדיקה שנשלחו הודעות לכל הספרנים
            self.assertEqual(len(sent_messages), 3)

            # בדיקת תוכן ההודעות
            for librarian, message in sent_messages:
                self.assertIn("Were added 3 copies of the book 'The Hobbit' and were loaned to:", message)
                for customer in customers:
                    self.assertIn(customer.name, message)
                    self.assertIn(customer.phone, message)
                    self.assertIn(customer.email, message)

        finally:
            # החזרת המתודה המקורית
            self.notification_observer._send_notification = original_send_notification

    def test_update_with_invalid_event_type(self):
        """בדיקת עדכון עם סוג אירוע לא חוקי"""
        book = Book("Test Book", "Test Author", 1, "Test Genre", 2023)
        customers = [
            Customer("לקוח 5", "0551234567", "customer5@example.com")
        ]

        # שמירת הודעות שנשלחו (במקום הדפסה)
        sent_messages = []

        # החלפת השיטה המקורית במתודה שתשמור את ההודעות
        original_send_notification = self.notification_observer._send_notification

        def mock_send_notification(librarian, message):
            sent_messages.append((librarian, message))

        self.notification_observer._send_notification = mock_send_notification

        try:
            # הפעלת העדכון
            self.notification_observer.update(book, customers, "unknown_event")

            # בדיקה שלא נשלחו הודעות
            self.assertEqual(len(sent_messages), 0)

        finally:
            # החזרת המתודה המקורית
            self.notification_observer._send_notification = original_send_notification

    def test_get_librarians_with_empty_file(self):
        """בדיקת שליפת ספרנים מקובץ ריק"""
        # יצירת קובץ ריק
        with open(self.temp_users_file, 'w', newline='', encoding='utf-8') as file:
            pass

        librarians = self.notification_observer.get_librarians()
        self.assertEqual(len(librarians), 0)


if __name__ == '__main__':
    unittest.main()