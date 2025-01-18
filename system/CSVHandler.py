import os
import csv
from Library.Book import Book
from Library.Customer import Customer


class CSVHandler:
    @staticmethod
    def load_books_from_csv(file_path=None):
        """טוען ספרים מקובץ CSV ומחזיר רשימה של ספרים."""
        books = {}
        try:
            if file_path is None:
                base_path = os.path.dirname(os.path.abspath(__file__))
                file_path = os.path.join(base_path, '../files', 'books.csv')

            with open(file_path, mode='r', newline='', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    book = Book(
                        title=row['title'],
                        author=row['author'],
                        copies=int(row['copies']),
                        genre=row['genre'],
                        year=int(row['year'])
                    )
                    # קריאת מצב השאלה
                    book.is_loaned = row['is_loaned']
                    book.available_copies = int(row['copies']) if row['is_loaned'] == "No" else 0
                    books[book.title] = book
        except FileNotFoundError:
            print(f"File not found: {file_path}, starting with empty library.")
        return books

    @staticmethod
    def save_books_to_csv(books, file_path=None):
        """שומר את הספרים לקובץ CSV."""
        try:
            if file_path is None:
                base_path = os.path.dirname(os.path.abspath(__file__))
                file_path = os.path.join(base_path, '../files', 'books.csv')

            directory = os.path.dirname(file_path)
            if not os.path.exists(directory):
                os.makedirs(directory)

            with open(file_path, mode='w', newline='', encoding='utf-8') as file:
                fieldnames = ['title', 'author', 'is_loaned', 'copies', 'genre', 'year']
                writer = csv.DictWriter(file, fieldnames=fieldnames)

                writer.writeheader()

                for book in books.values():
                    writer.writerow({
                        'title': book.title,
                        'author': book.author,
                        'is_loaned': book.is_loaned,
                        'copies': book.total_copies,
                        'genre': book.genre,
                        'year': book.year
                    })
        except Exception as e:
            print(f"Error saving books to CSV: {str(e)}")

    @staticmethod
    def load_waiting_list_from_csv(file_path=None):
        """טוען את רשימת ההמתנה מקובץ CSV."""
        waiting_list = {}
        try:
            # אם לא התקבל נתיב, משתמשים בנתיב ברירת מחדל
            if file_path is None:
                base_path = os.path.dirname(os.path.abspath(__file__))
                file_path = os.path.join(base_path, '../files', 'waiting_list.csv')

            if os.path.exists(file_path):
                with open(file_path, mode='r', newline='', encoding='utf-8') as file:
                    reader = csv.DictReader(file)
                    for row in reader:
                        book_title = row['Book Title']
                        customer = Customer(
                            name=row['Customer Name'],
                            phone=row['Customer Phone'],
                            email=row['Customer Email']
                        )
                        if book_title not in waiting_list:
                            waiting_list[book_title] = []
                        waiting_list[book_title].append(customer)
        except Exception as e:
            print(f"Error loading waiting list from {file_path}: {str(e)}")
        return waiting_list

    @staticmethod
    def save_waiting_list_to_csv(waiting_list, file_path=None):
        """שומר את רשימת ההמתנה בקובץ CSV."""
        try:
            # אם לא התקבל נתיב, משתמשים בנתיב ברירת מחדל
            if file_path is None:
                base_path = os.path.dirname(os.path.abspath(__file__))
                file_path = os.path.join(base_path, '../files', 'waiting_list.csv')

            # וידוא שהתיקייה קיימת
            directory = os.path.dirname(file_path)
            if not os.path.exists(directory):
                os.makedirs(directory)

            with open(file_path, mode='w', newline='', encoding='utf-8') as file:
                fieldnames = ['Book Title', 'Customer Name', 'Customer Phone', 'Customer Email']
                writer = csv.DictWriter(file, fieldnames=fieldnames)

                writer.writeheader()

                for book_title, customers in waiting_list.items():
                    for customer in customers:
                        writer.writerow({
                            'Book Title': book_title,
                            'Customer Name': customer.name,
                            'Customer Phone': customer.phone,
                            'Customer Email': customer.email
                        })
        except Exception as e:
            print(f"Error saving waiting list to {file_path}: {str(e)}")