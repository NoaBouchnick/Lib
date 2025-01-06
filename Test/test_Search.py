from unittest import TestCase

from Library.Book import Book
from Library.Librarian import Librarian
from Library.Search import Search


class TestSearch(TestCase):

    def setUp(self):
        self.librarian = Librarian()
        self.librarian.logger.disable_console_logs()

        """
        אתחול הספרים לבדיקות.
        """
        self.book1 = Book("Harry Potter", "J.K. Rowling", 3, "Fantasy", 1997)
        self.book2 = Book("The Hobbit", "J.R.R. Tolkien", 5, "Fantasy", 1937)
        self.book3 = Book("Clean Code", "Robert C. Martin", 2, "Programming", 2008)

        self.books = {
            self.book1.title: self.book1,
            self.book2.title: self.book2,
            self.book3.title: self.book3,
        }

        self.search = Search(self.books)

    def test_set_strategy(self):
        """
        בדיקת הגדרת אסטרטגיית חיפוש.
        """
        self.search.set_strategy(Search.TitleSearchStrategy())
        self.assertIsInstance(self.search.strategy, Search.TitleSearchStrategy)

    def test_search_by_partial_title(self):
        """
        בדיקת חיפוש חלקי לפי כותרת.
        """
        self.search.set_strategy(Search.TitleSearchStrategy())
        results = self.search.search("Har")
        self.assertEqual(len(results), 1)
        self.assertIn(self.book1, results)

        results = self.search.search("Potter")
        self.assertEqual(len(results), 1)
        self.assertIn(self.book1, results)

    def test_search_by_partial_author(self):
        """
        בדיקת חיפוש חלקי לפי מחבר.
        """
        self.search.set_strategy(Search.AuthorSearchStrategy())
        results = self.search.search("Row")
        self.assertEqual(len(results), 1)
        self.assertIn(self.book1, results)

        results = self.search.search("Mart")
        self.assertEqual(len(results), 1)
        self.assertIn(self.book3, results)

    def test_search_by_partial_year(self):
        """
        בדיקת חיפוש חלקי לפי שנה.
        """
        self.search.set_strategy(Search.YearSearchStrategy())
        results = self.search.search("19")
        self.assertEqual(len(results), 2)  # אמור להחזיר את הספרים עם 1937 ו-1997
        self.assertIn(self.book1, results)
        self.assertIn(self.book2, results)

    def test_search_by_partial_genre(self):
        """
        בדיקת חיפוש חלקי לפי ז'אנר.
        """
        self.search.set_strategy(Search.GenreSearchStrategy())
        results = self.search.search("Fan")
        self.assertEqual(len(results), 2)
        self.assertIn(self.book1, results)
        self.assertIn(self.book2, results)

        results = self.search.search("Pro")
        self.assertEqual(len(results), 1)
        self.assertIn(self.book3, results)

    def test_search_by_partial_copies(self):
        """
        בדיקת חיפוש חלקי לפי עותקים.
        """
        self.search.set_strategy(Search.CopiesSearchStrategy())
        results = self.search.search("2")
        self.assertEqual(len(results), 1)
        self.assertIn(self.book3, results)

    def test_search_no_results(self):
        """
        בדיקת חיפוש ללא תוצאות.
        """
        self.search.set_strategy(Search.TitleSearchStrategy())
        results = self.search.search("Nonexistent")
        self.assertEqual(len(results), 0)

    def test_display_all_books(self):
        """
        בדיקת הצגת כל הספרים.
        """
        results = self.search.display_all_books()
        self.assertEqual(len(results), 3)
        self.assertIn(self.book1, results)
        self.assertIn(self.book2, results)
        self.assertIn(self.book3, results)

    def test_display_available_books(self):
        """
        בדיקת הצגת ספרים זמינים.
        """
        # הפחתת עותק מהספר "Harry Potter"
        self.book1.available_copies -= 1

        results = self.search.display_available_books()
        self.assertEqual(len(results), 3)
        self.assertIn(self.book1, results)
        self.assertIn(self.book2, results)
        self.assertIn(self.book3, results)

    def test_display_borrowed_books(self):
        """
        בדיקת הצגת ספרים מושאלים.
        """
        # סימון עותק מושאל עבור "Harry Potter"
        self.book1.available_copies -= 1

        results = self.search.display_borrowed_books()
        self.assertEqual(len(results), 1)
        self.assertIn(self.book1, results)
