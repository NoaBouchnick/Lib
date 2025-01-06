from abc import ABC, abstractmethod
from Log import Log  # ייבוא מחלקת הלוג

class Search:
    def __init__(self, books: dict):
        self.books = books
        self.strategy = None
        self.logger = Log()  # יצירת אובייקט לוג

        self.logger.disable_console_logs()


    def set_strategy(self, strategy):
        """
        קובע את אסטרטגיית החיפוש.
        """
        self.strategy = strategy

    def search(self, query: str):
        """
        מבצע את החיפוש עם האסטרטגיה שנבחרה.
        """
        if not self.strategy:
            self.logger.log_error("fail")
            # raise ValueError("No search strategy set.")

        results = self.strategy.search(query, self.books)

        # תיעוד הצלחה או כישלון
        if results:
            self.logger.log_info(f'Search book {query.title()} by {query} completed successfully')
        else:
            self.logger.log_error(f'Search for book {query.title()} by {query} fail')

        return results

    def display_all_books(self):
        """
        מציג את כל הספרים.
        """
        try:
            books = list(self.books.values())
            if books:
                self.logger.log_info("Displayed all books successfully")
                return books
            else:
                self.logger.log_error("Displayed all books fail")
                return []
        except Exception as e:
            self.logger.log_error(f"Error displaying all books: {str(e)}")
            return []

    def display_available_books(self):
        """
        מציג את כל הספרים הזמינים.
        """
        try:
            books = [book for book in self.books.values() if book.available_copies > 0]
            if books:
                self.logger.log_info("Displayed available books successfully.")
                return books
            else:
                self.logger.log_error("Displayed available books fail")
                return []
        except Exception as e:
            self.logger.log_error(f"Error displaying available books: {str(e)}")
            return []

    def display_borrowed_books(self):
        """
        מציג את כל הספרים המושאלים.
        """
        try:
            books = [book for book in self.books.values() if book.total_copies > book.available_copies]
            if books:
                self.logger.log_info("Displayed borrowed books successfully.")
                return books
            else:
                self.logger.log_error("Displayed borrowed books fail")
                return []
        except Exception as e:
            self.logger.log_error(f"Error displaying borrowed books: {str(e)}")
            return []

    # מחלקת בסיס לאסטרטגיות
    class SearchStrategy(ABC):
        @abstractmethod
        def search(self, query: str, books: dict):
            pass

    class TitleSearchStrategy(SearchStrategy):
        def search(self, query: str, books: dict):
            query = query.lower()
            return [book for book in books.values() if query in book.title.lower()]

    class AuthorSearchStrategy(SearchStrategy):
        def search(self, query: str, books: dict):
            query = query.lower()
            return [book for book in books.values() if query in book.author.lower()]

    class GenreSearchStrategy(SearchStrategy):
        def search(self, query: str, books: dict):
            query = query.lower()
            return [book for book in books.values() if query in book.genre.lower()]

    class YearSearchStrategy(SearchStrategy):
        def search(self, query: str, books: dict):
            query = query.lower()
            return [book for book in books.values() if query in str(book.year).lower()]

    class CopiesSearchStrategy(SearchStrategy):
        def search(self, query: str, books: dict):
            query = query.lower()
            return [book for book in books.values() if query in str(book.total_copies).lower()]

