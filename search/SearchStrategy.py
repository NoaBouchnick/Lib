from abc import ABC, abstractmethod


# base class for search strategies
class SearchStrategy(ABC):
    #abstract method to search for books based on the strategy
    @abstractmethod
    def search(self, query: str, books: dict):
        pass

#search strategy for finding books by their title
class TitleSearchStrategy(SearchStrategy):
    #searches for books whose titles contain the query
    def search(self, query: str, books: dict):
        query = query.lower()
        return [book for book in books.values() if query in book.title.lower()]

    def get_search_type(self) -> str:
        return "name"

#search strategy for finding books by their author
class AuthorSearchStrategy(SearchStrategy):
    #searches for books whose authors contain the query
    def search(self, query: str, books: dict):
        query = query.lower()
        return [book for book in books.values() if query in book.author.lower()]

    def get_search_type(self) -> str:
        return "author name"

#search strategy for finding books based on their genre
class GenreSearchStrategy(SearchStrategy):
    #searches for books whose genre contains the query
    def search(self, query: str, books: dict):
        query = query.lower()
        return [book for book in books.values() if query in book.genre.lower()]

    def get_search_type(self) -> str:
        return "genre"

#search strategy for finding books based on their publication year
class YearSearchStrategy(SearchStrategy):
    #searches for books published in a specific year
    def search(self, query: str, books: dict):
        query = query.lower()
        return [book for book in books.values() if query in str(book.year).lower()]

    def get_search_type(self) -> str:
        return "year"

#search strategy for finding books based on the total number of copies
class CopiesSearchStrategy(SearchStrategy):
    #searches for books with a specific number of total copies
    def search(self, query: str, books: dict):
        query = query.lower()
        return [book for book in books.values() if query in str(book.total_copies).lower()]

    def get_search_type(self) -> str:
        return "copies"