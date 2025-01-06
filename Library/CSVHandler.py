import os
import csv
from .Book import Book  # הנחה שמחלקת Book נמצאת בקובץ נפרד בשם Book.py

class CSVHandler:

    @staticmethod
    def load_books_from_csv(file_path=None):
        """טוען ספרים מקובץ CSV ומחזיר רשימה של ספרים."""
        books = {}
        try:
            # אם לא צויין נתיב, מחשבים את הנתיב המלא
            if file_path is None:
                # אם לא עבר נתיב, מחשבים את הנתיב המלא
                base_path = os.path.dirname(os.path.abspath(__file__))
                file_path = os.path.join(base_path, 'Library', 'books.csv')

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
                    books[book.title] = book
        except FileNotFoundError:
            print(f"File not found: {file_path}, starting with empty library.")
        return books

    @staticmethod
    def save_books_to_csv(books, file_path=None):
        try:
            # אם לא צויין נתיב, מחשבים את הנתיב המלא
            if file_path is None:
                base_path = os.path.dirname(os.path.abspath(__file__))
                file_path = os.path.join(base_path, 'Library', 'books.csv')

            # וודא שהתיקייה קיימת, אם לא צור אותה
            directory = os.path.dirname(file_path)
            if not os.path.exists(directory):
                os.makedirs(directory)

            with open(file_path, mode='w', newline='', encoding='utf-8') as file:
                fieldnames = ['title', 'author', 'is_loaned', 'copies', 'genre', 'year']
                writer = csv.DictWriter(file, fieldnames=fieldnames)

                # כתיבת כותרת
                writer.writeheader()

                for book in books.values():
                    # אם כל העותקים מושאלים, הסטטוס יהיה "Yes", אחרת "No"
                    is_loaned = "Yes" if book.available_copies == 0 else "No"
                    # כותבים את הספר עם העותקים הכוללים והסטטוס המחשב
                    writer.writerow({
                        'title': book.title,
                        'author': book.author,
                        'is_loaned': is_loaned,
                        'copies': book.total_copies,
                        'genre': book.genre,
                        'year': book.year
                    })
                # print("Books saved successfully")
        except Exception as e:
            print(f"Error saving books to CSV: {str(e)}")
