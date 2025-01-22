from abc import ABC, abstractmethod

#abstract base class for iterating over a collection of books, defines the interface for the iterators
class BookIterator(ABC):
    #checks if there are more books to iterate over
    @abstractmethod
    def has_next(self):
        pass

    #recieves the next book in the iteration
    @abstractmethod
    def next(self):
        pass


#specific implementations of the book iterator interface
class AllBooksIterator(BookIterator):
    #initializes thr AllBookIterator
    def __init__(self, books, logger):
        self.books = list(books.values())
        self.index = 0
        self.logger = logger

    #checks if there are more books in the collection
    def has_next(self):
        return self.index < len(self.books)

    #retrieves next book from the collection
    def next(self):
        if self.has_next():
            book = self.books[self.index]
            self.index += 1
            return book
        self.logger.log_error("Displayed all books fail")
        raise StopIteration()


#iterator for books available to loan
class AvailableBooksIterator(BookIterator):
    #initializes the availableBooksIterator
    def __init__(self, books, logger):
        self.books = [book for book in books.values() if book.available_copies > 0]
        self.index = 0
        self.logger = logger

    #checks for more available books in collection
    def has_next(self):
        return self.index < len(self.books)

    #retrieves next available book in the collection
    def next(self):
        if self.has_next():
            book = self.books[self.index]
            self.index += 1
            return book
        self.logger.log_error("Displayed available books fail")
        raise StopIteration()


#iterator for borrowed books
class BorrowedBooksIterator(BookIterator):
    #initializes borrowedBooksIterator
    def __init__(self, books, logger):
        self.books = [book for book in books.values() if book.total_copies > book.available_copies]
        self.index = 0
        self.logger = logger

    #checks for more borrowed books in collection
    def has_next(self):
        return self.index < len(self.books)

    #retrieves next borrowed book in collection
    def next(self):
        if self.has_next():
            book = self.books[self.index]
            self.index += 1
            return book
        self.logger.log_error("Displayed borrowed books fail")
        raise StopIteration()