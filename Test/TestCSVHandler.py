import os
import unittest

from system.CSVHandler import CSVHandler
from Library.Book import Book


class TestCSVHandler(unittest.TestCase):

    def test_add_book(self):
        # הגדרת נתיב הקובץ
        base_path = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(base_path, '..', 'Library', 'books.csv')

        # טוען את רשימת הספרים
        books = CSVHandler.load_books_from_csv(file_path)

        # יצירת ספר חדש
        new_book = Book(
            title="The Silent Patient",
            author="Alex Michaelides",
            copies=3,
            genre="Thriller",
            year=2019
        )
        # הוספת הספר לרשימה
        books[new_book.title] = new_book
        CSVHandler.save_books_to_csv(books, file_path)

        # טוען שוב את קובץ ה-CSV
        updated_books = CSVHandler.load_books_from_csv(file_path)

        # בדוק אם הספר החדש נמצא
        self.assertIn(new_book.title, updated_books)
        self.assertEqual(updated_books[new_book.title].author, new_book.author)

    def test_remove_book(self):
        # הגדרת נתיב הקובץ
        base_path = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(base_path, '..', 'Library', 'books.csv')

        # טוען את רשימת הספרים
        books = CSVHandler.load_books_from_csv(file_path)

        # בודק אם הספר שהוספת כבר קיים
        book_to_remove = books.get("The Silent Patient")
        if book_to_remove:
            # הסרת הספר מהרשימה
            del books[book_to_remove.title]
            CSVHandler.save_books_to_csv(books, file_path)

            # טוען שוב את קובץ ה-CSV
            updated_books = CSVHandler.load_books_from_csv(file_path)

            # בדוק אם הספר הוסר
            self.assertNotIn("The Silent Patient", updated_books)
        else:
            # במקרה שהספר לא נמצא (אם הוא הוסר בטסט קודם)
            self.skipTest("Book not found for removal.")
