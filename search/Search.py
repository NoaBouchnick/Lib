from functools import wraps
from Books.BookIterator import AllBooksIterator, AvailableBooksIterator, BorrowedBooksIterator
from Library.Librarian import log_operation
from system.Logger import Logger
#provides search functionality for books in the library
class Search:
    #initializes search class
    def __init__(self, books: dict, waiting_list=None, books_borrowed=None):
        self.books = books
        self.waiting_list = waiting_list if waiting_list is not None else {}
        self.books_borrowed = books_borrowed if books_borrowed is not None else {}
        self.strategy = None
        self.logger = Logger()
        self.logger.disable_console_logs()

    #returns an iterator for all books in the library
    def __iter__(self):
        return AllBooksIterator(self.books, self.logger)

    #returns an iterator for available books in the library
    def get_available_iterator(self):
        return AvailableBooksIterator(self.books, self.logger)

    #returns iterator for borrower books in the library
    def get_borrowed_iterator(self):
        return BorrowedBooksIterator(self.books, self.logger)

    #sets the search strategy to be used
    def set_strategy(self, strategy):
        self.strategy = strategy

    #preforms a search using set strategy
    @log_operation("search")
    def search(self, query: str):
        if not self.strategy:
            raise ValueError("No search strategy set.")
        return self.strategy.search(query, self.books)

    #displays all books in the library
    @log_operation("Display all books")
    def display_all_books(self):
        books = []
        iterator = self.__iter__()
        while iterator.has_next():
            books.append(iterator.next())
        return books

    #displays all available books in the library
    @log_operation("Display available books")
    def display_available_books(self):
        books = []
        iterator = self.get_available_iterator()
        while iterator.has_next():
            books.append(iterator.next())
        return books

    #displays all borrowed books in the library
    @log_operation("Display borrowed books")
    def display_borrowed_books(self):
        books = []
        iterator = self.get_borrowed_iterator()
        while iterator.has_next():
            books.append(iterator.next())
        return books

    #displays books filtered by genre
    @log_operation("Display books by category")
    def display_books_by_genre(self, genre: str):
        books = []
        for book in self.books.values():
            if book.genre.lower() == genre.lower():
                books.append(book)
        return books

    #displays the most popular books based on borrow count and waiting list
    @log_operation("Display popular books")
    def display_popular_books(self):
        popular_books = []

        for book in self.books.values():
            borrowed_copies = self.books_borrowed.get(book.title, 0)
            waiting_list_count = len(self.waiting_list.get(book.title, []))
            popularity_score = borrowed_copies + waiting_list_count

            if popularity_score > 0:
                popular_books.append((book, popularity_score))

        #sort by popularity score (a.k.a. demand score)
        popular_books.sort(key=lambda x: x[1], reverse=True)

        # returns top of list without the pupolarity score
        return [book for book, _ in popular_books[:10]]