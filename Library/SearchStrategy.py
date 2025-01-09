from abc import ABC, abstractmethod

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
