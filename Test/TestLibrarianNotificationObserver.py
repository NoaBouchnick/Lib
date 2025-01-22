import unittest
import os
import csv
import tempfile
import logging
from pathlib import Path
from Books.Book import Book
from Library.Customer import Customer
from system.Logger import Logger
from Library.LibrarianNotificationObserver import LibrarianNotificationObserver

#test environment for the librarianNotificationObserver class
class TestLibrarianNotificationObserver(unittest.TestCase):
    #sets up the test environment for the entire suite
    @classmethod
    def setUpClass(cls):
        logging.disable(logging.CRITICAL)

    #sets up test environment for each test
    def setUp(self):
        #creates temporary logger and disables logs
        self.logger = Logger()
        self.logger.disable_console_logs()

        # creates temporary directory and users file
        self.temp_dir = tempfile.mkdtemp()
        self.temp_users_file = os.path.join(self.temp_dir, 'users.csv')

        # write sample librarian data to the temporary file
        with open(self.temp_users_file, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerows([
                ['נועה'],
                ['אביב'],
                ['דני']
            ])

        #initializes librarianNotificationObserver with the temporary file
        self.notification_observer = LibrarianNotificationObserver(self.logger)
        self.notification_observer.users_file = Path(self.temp_users_file)

    #cleans up the test environment after each test case
    # removes the temporary users file and directory
    def tearDown(self):
        os.unlink(self.temp_users_file)
        os.rmdir(self.temp_dir)

    #tests the librarians method
    def test_get_librarians(self):
        librarians = self.notification_observer.get_librarians()

        # checks that all librarians are correctly read from file
        expected_librarians = ['נועה', 'אביב', 'דני']
        self.assertEqual(len(librarians), 3)
        self.assertEqual(set(librarians), set(expected_librarians))

    #tests the update method for a book return event
    def test_update_with_return_event(self):
        book = Book("1984", "George Orwell", 5, "Dystopian", 1949)
        customers = [
            Customer("לקוח 1", "0501234567", "customer1@example.com"),
            Customer("לקוח 2", "0521234567", "customer2@example.com")
        ]

        # mock notifications
        sent_messages = []

        # replace _send_notification with a mock method
        original_send_notification = self.notification_observer._send_notification

        def mock_send_notification(librarian, message):
            sent_messages.append((librarian, message))

        self.notification_observer._send_notification = mock_send_notification

        try:
            #trigger update
            self.notification_observer.update(book, customers, "return")

            #verify notifications were sent to all librarians
            self.assertEqual(len(sent_messages), 3)

            # verify the content of the message
            for librarian, message in sent_messages:
                self.assertIn("The book '1984' returned and loaned to:", message)
                for customer in customers:
                    self.assertIn(customer.name, message)
                    self.assertIn(customer.phone, message)
                    self.assertIn(customer.email, message)

        finally:
            # restore the original method
            self.notification_observer._send_notification = original_send_notification

    #tests the update method for an addition event
    #verifies notifications are sent to all librarians with book and costumer details
    def test_update_with_addition_event(self):
        book = Book("The Hobbit", "J.R.R. Tolkien", 3, "Fantasy", 1937)
        customers = [
            Customer("לקוח 3", "0531234567", "customer3@example.com"),
            Customer("לקוח 4", "0541234567", "customer4@example.com")
        ]

        # mock notifications
        sent_messages = []

        # replace _send_notification with mock method
        original_send_notification = self.notification_observer._send_notification

        def mock_send_notification(librarian, message):
            sent_messages.append((librarian, message))

        self.notification_observer._send_notification = mock_send_notification

        try:
            # trigger update
            self.notification_observer.update(book, customers, "addition")

            # verify notifications were sent to all librarians
            self.assertEqual(len(sent_messages), 3)

            # verify the content of each message
            for librarian, message in sent_messages:
                self.assertIn("Were added 3 copies of the book 'The Hobbit' and were loaned to:", message)
                for customer in customers:
                    self.assertIn(customer.name, message)
                    self.assertIn(customer.phone, message)
                    self.assertIn(customer.email, message)

        finally:
            # restore the original method
            self.notification_observer._send_notification = original_send_notification

    #tests the update method with an invalid event type
    #verifies no notifications are sent for unknown event types
    def test_update_with_invalid_event_type(self):
        book = Book("Test Book", "Test Author", 1, "Test Genre", 2023)
        customers = [
            Customer("לקוח 5", "0551234567", "customer5@example.com")
        ]

        # mock notifications
        sent_messages = []

        # replace _send_notification with a mock method
        original_send_notification = self.notification_observer._send_notification

        def mock_send_notification(librarian, message):
            sent_messages.append((librarian, message))

        self.notification_observer._send_notification = mock_send_notification

        try:
            # trigger update with an unknown event type
            self.notification_observer.update(book, customers, "unknown_event")

            # verify no notifications were sent
            self.assertEqual(len(sent_messages), 0)

        finally:
            # restore the original method
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