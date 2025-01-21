from functools import wraps
from Books.BookIterator import AllBooksIterator, AvailableBooksIterator, BorrowedBooksIterator
from Library.Librarian import log_operation
from system.Logger import Logger

class Search:
    def __init__(self, books: dict, waiting_list=None, books_borrowed=None):
        """
        אתחול מחלקת החיפוש

        Args:
            books (dict): מילון של כל הספרים
            waiting_list (dict, optional): מילון של רשימות המתנה לכל ספר
            books_borrowed (dict, optional): מילון של כמות העותקים המושאלים לכל ספר
        """
        self.books = books
        self.waiting_list = waiting_list if waiting_list is not None else {}
        self.books_borrowed = books_borrowed if books_borrowed is not None else {}
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

    @log_operation("search")  # שימוש בדקורטור המשותף
    def search(self, query: str):
        if not self.strategy:
            raise ValueError("No search strategy set.")
        return self.strategy.search(query, self.books)

    @log_operation("Display all books")
    def display_all_books(self):
        books = []
        iterator = self.__iter__()
        while iterator.has_next():
            books.append(iterator.next())
        return books

    @log_operation("Display available books")
    def display_available_books(self):
        books = []
        iterator = self.get_available_iterator()
        while iterator.has_next():
            books.append(iterator.next())
        return books

    @log_operation("Display borrowed books")
    def display_borrowed_books(self):
        books = []
        iterator = self.get_borrowed_iterator()
        while iterator.has_next():
            books.append(iterator.next())
        return books

    @log_operation("Display books by category")
    def display_books_by_genre(self, genre: str):
        books = []
        for book in self.books.values():
            if book.genre.lower() == genre.lower():
                books.append(book)
        return books

    @log_operation("Display popular books")
    def display_popular_books(self):
        """מציג ספרים פופולריים לפי כמות השאלות ורשימת המתנה"""
        popular_books = []

        for book in self.books.values():
            borrowed_copies = self.books_borrowed.get(book.title, 0)
            waiting_list_count = len(self.waiting_list.get(book.title, []))
            popularity_score = borrowed_copies + waiting_list_count

            if popularity_score > 0:  # רק ספרים שיש להם ביקוש
                popular_books.append((book, popularity_score))

        # מיון לפי ציון הפופולריות
        popular_books.sort(key=lambda x: x[1], reverse=True)

        # החזרת הספרים (ללא ציון הפופולריות)
        return [book for book, _ in popular_books[:10]]