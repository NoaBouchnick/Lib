import unittest
import os
import csv
import logging

from search.Search import Search
from search.SearchStrategy import TitleSearchStrategy, AuthorSearchStrategy, GenreSearchStrategy, YearSearchStrategy, \
    CopiesSearchStrategy
from system.Logger import Logger
from Library.Book import Book


class TestSearch(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """הכנת סביבת טסט"""
        # השבתת לוגים
        logging.disable(logging.CRITICAL)

        # נתיב הבסיס
        cls.base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        cls.files_dir = os.path.join(cls.base_path, 'files')

    def setUp(self):
        """הכנת ספרים לכל טסט"""
        # טעינת ספרים מקובץ CSV
        books_path = os.path.join(self.base_path, 'files', 'books.csv')
        self.books = {}

        with open(books_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                book = Book(
                    title=row['title'],
                    author=row['author'],
                    copies=int(row['copies']),
                    genre=row['genre'],
                    year=int(row['year'])
                )
                book.is_loaned = row['is_loaned']
                book.available_copies = int(row['copies']) if row['is_loaned'] == "No" else 0
                self.books[book.title] = book

        # יצירת אובייקט חיפוש
        self.search = Search(self.books)

    def test_search_strategies(self):
        """בדיקת כל אסטרטגיות החיפוש"""
        test_cases = [
            (TitleSearchStrategy(), "1984", ["1984"]),
            (AuthorSearchStrategy(), "orwell", ["1984"]),
            (GenreSearchStrategy(), "dystopian", ["1984", "Brave New World", "The Handmaid's Tale"]),
            (YearSearchStrategy(), "1952", ["Invisible Man", "The Old Man and the Sea"]),
            (CopiesSearchStrategy(), "7", ["Harry Potter and the Philosopher's Stone"])
        ]

        for strategy, query, expected_titles in test_cases:
            # הגדרת אסטרטגיה
            self.search.set_strategy(strategy)

            # ביצוע החיפוש
            results = self.search.search(query)

            # בדיקת תוצאות
            self.assertEqual(
                len(results),
                len(expected_titles),
                f"Failed for {strategy.__class__.__name__} with query '{query}'"
            )

            # בדיקת כותרות הספרים שנמצאו
            result_titles = [book.title for book in results]
            for title in expected_titles:
                self.assertIn(
                    title,
                    result_titles,
                    f"Failed to find {title} for {strategy.__class__.__name__}"
                )

    def test_display_methods(self):
        """בדיקת שיטות התצוגה"""
        # בדיקת הצגת כל הספרים
        all_books = self.search.display_all_books()
        self.assertEqual(len(all_books), len(self.books))

        # בדיקת הצגת ספרים זמינים
        available_books = self.search.display_available_books()
        self.assertTrue(all(book.available_copies > 0 for book in available_books))

        # בדיקת הצגת ספרים מושאלים
        borrowed_books = self.search.display_borrowed_books()
        self.assertTrue(all(book.total_copies > book.available_copies for book in borrowed_books))

    def test_no_strategy_set(self):
        """בדיקת מצב שבו לא הוגדרה אסטרטגיית חיפוש"""
        search = Search(self.books)
        results = search.search("test")
        self.assertEqual(results, [])

    def test_no_results_found(self):
        """בדיקת חיפוש שאינו מחזיר תוצאות"""
        strategies = [
            TitleSearchStrategy(),
            AuthorSearchStrategy(),
            GenreSearchStrategy(),
            YearSearchStrategy(),
            CopiesSearchStrategy()
        ]

        for strategy in strategies:
            self.search.set_strategy(strategy)
            results = self.search.search("NonexistentQuery")
            self.assertEqual(results, [], f"Failed for {strategy.__class__.__name__}")

    def test_case_insensitive_search(self):
        """בדיקת חיפוש רגיש לגודל אותיות"""
        test_cases = [
            (TitleSearchStrategy(), "the hobbit"),
            (TitleSearchStrategy(), "THE HOBBIT"),
            (TitleSearchStrategy(), "ThE hObBiT"),
            (AuthorSearchStrategy(), "tolkien"),
            (AuthorSearchStrategy(), "TOLKIEN"),
            (AuthorSearchStrategy(), "ToLkIeN")
        ]

        for strategy, query in test_cases:
            self.search.set_strategy(strategy)
            results = self.search.search(query)
            self.assertTrue(
                any(book.title in ["The Hobbit", "The Lord of the Rings"] for book in results),
                f"Failed for query '{query}'"
            )


if __name__ == '__main__':
    unittest.main()