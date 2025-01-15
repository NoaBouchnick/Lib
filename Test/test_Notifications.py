import unittest
from unittest.mock import MagicMock, patch
from Library.Book import Book
from Library.Librarian import Librarian

class TestLibrarian(unittest.TestCase):

    @patch('Library.Librarian.CSVHandler')  # Correct path
    @patch('Library.Librarian.Logger')  # Correct path
    @patch('Library.Librarian.Notifications')  # Correct path
    def setUp(self, MockNotifications, MockLogger, MockCSVHandler):
        self.mock_csv_handler = MockCSVHandler
        self.mock_logger = MockLogger
        self.mock_notifications = MockNotifications

        # Creating a Mock Book object from the CSV file
        self.book = MagicMock(spec=Book)
        self.book.title = "Test Book"
        self.book.total_copies = 5
        self.book.available_copies = 3  # 3 copies available
        self.book.year = 2023
        self.book.is_loaned = "Yes"

        # Creating Librarian object
        self.librarian = Librarian(file_path="books.csv")

        # Mocking a waiting list of customers
        self.librarian.waiting_list = ['Customer 1', 'Customer 2', 'Customer 3', 'Customer 4']

    def test_notify_customer_when_book_is_returned(self):
        # Simulating a return of a book, which makes 3 copies available
        self.book.available_copies = 3  # After return, 3 copies are available

        # Notify the first 3 customers in the waiting list
        customers_to_notify = self.librarian.waiting_list[:3]
        self.librarian.notify_all_users_for_book_availability(self.book)

        # Verify the notification was sent to the first 3 customers
        for customer in customers_to_notify:
            self.librarian.notifications.send_notification.assert_any_call(
                f"Book 'Test Book' is now available to {customer}.")
            self.librarian.logger.log_info.assert_any_call(f"Message was sent to {customer}.")

if __name__ == '__main__':
    unittest.main()
