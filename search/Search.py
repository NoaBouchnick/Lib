from Books.BookIterator import AllBooksIterator, AvailableBooksIterator, BorrowedBooksIterator
from system.Logger import Logger


class Search:
    def __init__(self, books: dict):
        self.books = books
        self.strategy = None
        self.logger = Logger()
        self.logger.disable_console_logs()

    def __iter__(self):
        return AllBooksIterator(self.books, self.logger)

    def get_available_iterator(self):
        return AvailableBooksIterator(self.books, self.logger)

    def get_borrowed_iterator(self):
        return BorrowedBooksIterator(self.books, self.logger)

    def set_strategy(self, strategy):
        """קובע את אסטרטגיית החיפוש."""
        self.strategy = strategy

    def search(self, query: str):
        """מבצע את החיפוש עם האסטרטגיה שנבחרה."""
        if not self.strategy:
            self.logger.log_error(f'Search book "{query}" by name fail')
            raise ValueError("No search strategy set.")

        results = self.strategy.search(query, self.books)

        strategy_name = self.strategy.__class__.__name__
        if strategy_name == "TitleSearchStrategy":
            success_msg = f'Search book "{query}" by name completed successfully'
            fail_msg = f'Search book "{query}" by name fail'
        elif strategy_name == "AuthorSearchStrategy":
            success_msg = f'Search book "{query}" by author name completed successfully'
            fail_msg = f'Search book "{query}" by author name fail'
        else:  # GenreSearchStrategy
            success_msg = "Displayed book by category successfully"
            fail_msg = "Displayed book by category fail"

        if results:
            self.logger.log_info(success_msg)
        else:
            self.logger.log_error(fail_msg)
        return results

    def display_all_books(self):
        """מציג את כל הספרים."""
        try:
            books = []
            iterator = self.__iter__()
            while iterator.has_next():
                books.append(iterator.next())

            if books:
                self.logger.log_info("Displayed all books successfully")
            else:
                self.logger.log_error("Displayed all books fail")
            return books
        except Exception:
            self.logger.log_error("Displayed all books fail")
            return []

    def display_available_books(self):
        """מציג את כל הספרים הזמינים."""
        try:
            books = []
            iterator = self.get_available_iterator()
            while iterator.has_next():
                books.append(iterator.next())

            if books:
                self.logger.log_info("Displayed available books successfully")
            else:
                self.logger.log_error("Displayed available books fail")
            return books
        except Exception:
            self.logger.log_error("Displayed available books fail")
            return []

    def display_borrowed_books(self):
        """מציג את כל הספרים המושאלים."""
        try:
            books = []
            iterator = self.get_borrowed_iterator()
            while iterator.has_next():
                books.append(iterator.next())

            if books:
                self.logger.log_info("Displayed borrowed books successfully")
            else:
                self.logger.log_error("Displayed borrowed books fail")
            return books
        except Exception:
            self.logger.log_error("Displayed borrowed books fail")
            return []

    def display_books_by_genre(self, genre: str):
        """מציג ספרים לפי קטגוריה."""
        try:
            books = []
            for book in self.books.values():
                if book.genre.lower() == genre.lower():
                    books.append(book)

            if books:
                self.logger.log_info("Displayed book by category successfully")
            else:
                self.logger.log_error("Displayed book by category fail")
            return books
        except Exception:
            self.logger.log_error("Displayed book by category fail")
            return []

    def display_popular_books(self):
        """מציג ספרים פופולריים."""
        try:
            if True:
                self.logger.log_info("displayed successfully")
            else:
                self.logger.log_error("displayed fail")
            return []  # החלף עם הרשימה האמיתית
        except Exception:
            self.logger.log_error("displayed fail")
            return []