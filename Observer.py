from abc import ABC, abstractmethod
from typing import List
from Library.Book import Book
from Library.Customer import Customer


class Observer(ABC):
    @abstractmethod
    def update(self, book: Book, customers: List[Customer], event_type: str):
        pass


class Subject(ABC):
    @abstractmethod
    def attach(self, observer: Observer):
        pass

    @abstractmethod
    def detach(self, observer: Observer):
        pass

    @abstractmethod
    def notify(self, book: Book, customers: List[Customer], event_type: str):
        pass


class LibraryNotificationSubject(Subject):
    def __init__(self):
        self._observers: List[Observer] = []

    def attach(self, observer: Observer):
        if observer not in self._observers:
            self._observers.append(observer)

    def detach(self, observer: Observer):
        self._observers.remove(observer)

    def notify(self, book: Book, customers: List[Customer], event_type: str):
        for observer in self._observers:
            observer.update(book, customers, event_type)
