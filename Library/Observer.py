from abc import ABC, abstractmethod
from typing import List
from Books.Book import Book
from Library.Customer import Customer

class Observer(ABC):
    #abstract method to handle updates from the subject
    @abstractmethod
    def update(self, book: Book, customers: List[Customer], event_type: str):
        pass

#an abstract base class of Subject in the Observer design pattern
class Subject(ABC):
    #abstract method to attach an Observer to the Subject
    @abstractmethod
    def attach(self, observer: Observer):
        pass

    #abstract method to detach an Observer from the Subject
    @abstractmethod
    def detach(self, observer: Observer):
        pass

    #abstract method to notify all attached Observers of an event
    @abstractmethod
    def notify(self, book: Book, customers: List[Customer], event_type: str):
        pass

#a concrete implementation of the Subject class
class LibraryNotificationSubject(Subject):
    def __init__(self):
        self._observers: List[Observer] = []

    #attaches an Observer to the Subject
    def attach(self, observer: Observer):
        if observer not in self._observers:
            self._observers.append(observer)

    #detaches an Observer from the Subject
    def detach(self, observer: Observer):
        self._observers.remove(observer)

    #notifies all attached Observers of an event
    def notify(self, book: Book, customers: List[Customer], event_type: str):
        for observer in self._observers:
            observer.update(book, customers, event_type)
