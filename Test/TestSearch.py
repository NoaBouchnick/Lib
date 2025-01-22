import unittest
import os
import csv
import logging

from search.Search import Search
from search.SearchStrategy import TitleSearchStrategy, AuthorSearchStrategy, GenreSearchStrategy, YearSearchStrategy, \
    CopiesSearchStrategy
from Books.Book import Book

#test suite for the search module
class TestSearch(unittest.TestCase):
    #prepare the test environment for the search test suite
    @classmethod
    def setUpClass(cls):
        logging.disable(logging.CRITICAL)

        # set up the base directory and file path
        cls.base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        cls.files_dir = os.path.join(cls.base_path, 'files')

    #prepare the test environment for each test case
    def setUp(self):
        books_path = os.path.join(self.base_path, 'files', 'books.csv')
        self.books = {}

        #load books from CVS file
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

        # create the search object
        self.search = Search(self.books)

    #test all search strategies
    #verifies the correct results are returned for each strategy
    def test_search_strategies(self):
        test_cases = [
            (TitleSearchStrategy(), "1984", ["1984"]),
            (AuthorSearchStrategy(), "orwell", ["1984"]),
            (GenreSearchStrategy(), "dystopian", ["1984", "Brave New World", "The Handmaid's Tale"])
        ]

        for strategy, query, expected_titles in test_cases:
            self.search.set_strategy(strategy)
            results = self.search.search(query)
            self.assertEqual(
                len(results),
                len(expected_titles),
                f"Failed for {strategy.__class__.__name__} with query '{query}'"
            )

    #test various book display methods
    def test_display_methods(self):
        all_books = self.search.display_all_books()
        self.assertEqual(len(all_books), len(self.books))

        # display available books
        available_books = self.search.display_available_books()
        self.assertTrue(all(book.available_copies > 0 for book in available_books))

        # display borrowed books
        borrowed_books = self.search.display_borrowed_books()
        self.assertTrue(all(book.total_copies > book.available_copies for book in borrowed_books))

        #display books by genre
        genre_books = self.search.display_books_by_genre("Fiction")
        self.assertTrue(all(book.genre == "Fiction" for book in genre_books))

    #test the behavior when no search strategy is set
    def test_no_strategy_set(self):
        with self.assertRaises(ValueError):
            self.search.search("test")

    #verifies the behavior when no results are found
    def test_no_results_found(self):
        strategies = [
            TitleSearchStrategy(),
            AuthorSearchStrategy(),
            GenreSearchStrategy()
        ]

        for strategy in strategies:
            self.search.set_strategy(strategy)
            results = self.search.search("NonexistentQuery")
            self.assertEqual(results, [], f"Failed for {strategy.__class__.__name__}")

    #test case-insensitive functionality
    def test_case_insensitive_search(self):
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

    """test the display_popular_books method
    verifies:
    only books with demand (borrowed or in the waiting list) are displayed
    no more than 10 books a re returned
    books are sorted by popularity (borrowed count + waiting list count)
    """

    def test_display_popular_books(self):
        # mock data for borrowed books and waiting lists
        self.search.books_borrowed = {
            "1984": 5,
            "The Hobbit": 3,
            "Brave New World": 2
        }

        self.search.waiting_list = {
            "1984": ["User1", "User2"],
            "The Hobbit": ["User3"],
            "Brave New World": []
        }

        # display popular books
        popular_books = self.search.display_popular_books()

        # verify that only books with demand are returned
        self.assertTrue(len(popular_books) > 0)

        # verify that no more than 10 books are returned
        self.assertTrue(len(popular_books) <= 10)

        # verify that books are sorted by popularity
        popularities = [
            self.search.books_borrowed.get(book.title, 0) +
            len(self.search.waiting_list.get(book.title, []))
            for book in popular_books
        ]
        self.assertEqual(popularities, sorted(popularities, reverse=True))

        # verify the most popular book is at the top of the list
        self.assertEqual(popular_books[0].title, "1984")


if __name__ == '__main__':
    unittest.main()