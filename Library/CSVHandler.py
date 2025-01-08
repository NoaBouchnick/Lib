import os
import csv
from Library.Book import Book  # הנחה שמחלקת Book נמצאת בקובץ נפרד בשם Book.py


class CSVHandler:

    @staticmethod
    def load_books_from_csv(file_path=None):
        """טוען ספרים מקובץ CSV ומחזיר רשימה של ספרים."""
        books = {}
        try:
            if file_path is None:
                base_path = os.path.dirname(os.path.abspath(__file__))
                file_path = os.path.join(base_path, 'books.csv')

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
        try:
            if file_path is None:
                base_path = os.path.dirname(os.path.abspath(__file__))
                file_path = os.path.join(base_path, 'books.csv')

            directory = os.path.dirname(file_path)
            if not os.path.exists(directory):
                os.makedirs(directory)

            with open(file_path, mode='w', newline='', encoding='utf-8') as file:
                fieldnames = ['title', 'author', 'is_loaned', 'copies', 'genre', 'year']
                writer = csv.DictWriter(file, fieldnames=fieldnames)

                writer.writeheader()

                for book in books.values():
                    # שלוף את הנתונים מתוך האובייקט של הספר
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

