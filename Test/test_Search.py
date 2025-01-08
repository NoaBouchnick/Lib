import os
from unittest import TestCase
from Library.Librarian import Librarian
from Library.Search import Search
from Library.CSVHandler import CSVHandler  # הנחה שיש לך את המחלקה הזו

class TestSearch(TestCase):

    def setUp(self):
        self.librarian = Librarian()
        self.librarian.logger.disable_console_logs()

        """
        טוען את הספרים מקובץ CSV.
        """
        path = os.path.join('..', 'Library', 'books.csv')
        self.books = CSVHandler.load_books_from_csv(path)  # העברת הנתיב המלא כארגומנט אחד

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
        results = self.search.search("Harry")
        self.assertEqual(len(results), 1)
        self.assertIn(self.books["Harry Potter and the Philosopher's Stone"], results)

        results = self.search.search("Hobbit")
        self.assertEqual(len(results), 1)
        self.assertIn(self.books["The Hobbit"], results)

    def test_search_by_partial_author(self):
        """
        בדיקת חיפוש חלקי לפי מחבר.
        """
        self.search.set_strategy(Search.AuthorSearchStrategy())
        results = self.search.search("Rowling")
        self.assertEqual(len(results), 1)
        self.assertIn(self.books["Harry Potter and the Philosopher's Stone"], results)

        results = self.search.search("Tolkien")
        self.assertEqual(len(results), 2)
        self.assertIn(self.books["The Hobbit"], results)
        self.assertIn(self.books["The Lord of the Rings"], results)

    def test_search_by_partial_year(self):
        """
        בדיקת חיפוש חלקי לפי שנה.
        """
        self.search.set_strategy(Search.YearSearchStrategy())
        results = self.search.search("1997")
        self.assertEqual(len(results), 1)
        self.assertIn(self.books["Harry Potter and the Philosopher's Stone"], results)

    def test_search_by_partial_genre(self):
        """
        בדיקת חיפוש חלקי לפי ז'אנר.
        """
        self.search.set_strategy(Search.GenreSearchStrategy())
        results = self.search.search("Fantasy")
        self.assertEqual(len(results), 6)
        self.assertIn(self.books["Harry Potter and the Philosopher's Stone"], results)
        self.assertIn(self.books["The Hobbit"], results)
        self.assertIn(self.books["The Lord of the Rings"], results)
        self.assertIn(self.books["A Game of Thrones"], results)

    def test_search_by_partial_copies(self):
        """
        בדיקת חיפוש חלקי לפי עותקים.
        """
        self.search.set_strategy(Search.CopiesSearchStrategy())
        results = self.search.search("3")
        self.assertEqual(len(results), 10)  # ספרים עם 3 עותקים

    def test_search_no_results(self):
        """
        בדיקת חיפוש ללא תוצאות.
        """
        self.search.set_strategy(Search.TitleSearchStrategy())
        results = self.search.search("Nonexistent Book")
        self.assertEqual(len(results), 0)

    def test_display_all_books(self):
        """
        בדיקת הצגת כל הספרים.
        """
        results = self.search.display_all_books()
        self.assertEqual(len(results), 34)  # צריך להיות מספר הספרים הכולל בקובץ
        self.assertIn(self.books["The Hobbit"], results)
        self.assertIn(self.books["Harry Potter and the Philosopher's Stone"], results)

    def test_display_available_books(self):
        """
        בדיקת הצגת ספרים זמינים.
        """
        # הפחתת עותק מהספר "Harry Potter"
        self.books["Harry Potter and the Philosopher's Stone"].available_copies -= 1

        results = self.search.display_available_books()
        self.assertEqual(len(results), 17)  # ספרים זמינים אחרי ההפחתה
        self.assertIn(self.books["Harry Potter and the Philosopher's Stone"], results)

    def test_display_borrowed_books(self):
        """
        בדיקת הצגת ספרים מושאלים.
        """
        # סימון עותק מושאל עבור "Harry Potter"
        self.books["Harry Potter and the Philosopher's Stone"].available_copies -= 1

        results = self.search.display_borrowed_books()
        self.assertEqual(len(results), 18)
        self.assertIn(self.books["Harry Potter and the Philosopher's Stone"], results)
