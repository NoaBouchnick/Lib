import tkinter as tk
from tkinter import messagebox, simpledialog
import hashlib
import csv
from tkinter import ttk
import os
from Library.Book import Book
from Library.Customer import Customer
from Library.Librarian import Librarian
from Library.CSVHandler import CSVHandler  # ודא שהייבוא הזה נכון
from Log import Log

class LibraryApp:
    def __init__(self, file_path=None):
        self.logger = Log()

        # יצירת חלון ראשי
        self.root = tk.Tk()
        self.root.title("Library Management System")
        self.root.geometry("800x600")

        # מנגנון סגירת חלון רגיל (X)
        self.root.protocol("WM_DELETE_WINDOW", self.close_window)

        # יצירת אובייקט של Librarian
        self.librarian = Librarian()

        # יצירת תפריט ראשי
        self.main_menu = tk.Frame(self.root)

        # יצירת דף התחברות
        self.login_frame = tk.Frame(self.root)
        self.create_login_screen()

        # קריאת ספרים
        if file_path is None:
            base_path = os.path.dirname(os.path.abspath(__file__))
            file_path = os.path.join(base_path, 'Library', 'books.csv')

        # בדוק אם הקובץ קיים
        if not os.path.exists(file_path):
            self.books = {}  # אם הקובץ לא קיים, יתחיל עם ספריה ריקה
        else:
            self.books = CSVHandler.load_books_from_csv(file_path)

        # CSVHandler.save_books_to_csv(self.books)  # שומר את השינויים בקובץ CSV


    def create_login_screen(self):
        """יצירת מסך התחברות עם אפשרות לרישום"""
        self.login_frame.pack(padx=20, pady=20)

        tk.Label(self.login_frame, text="Username", font=("Arial", 12)).pack(pady=10)
        self.username_entry = tk.Entry(self.login_frame, font=("Arial", 12), width=30)
        self.username_entry.pack(pady=5)

        tk.Label(self.login_frame, text="Password", font=("Arial", 12)).pack(pady=10)
        self.password_entry = tk.Entry(self.login_frame, show="*", font=("Arial", 12), width=30)
        self.password_entry.pack(pady=5)

        tk.Button(self.login_frame, text="Login", command=self.login, font=("Arial", 12), width=20).pack(pady=10)
        tk.Button(self.login_frame, text="Register", command=self.register, font=("Arial", 12), width=20).pack(pady=10)

    def login(self):
        """פונקציה לחיבור למערכת"""
        username = self.username_entry.get()
        password = self.password_entry.get()

        with open("users.csv", mode="r") as file:
            reader = csv.reader(file)
            for row in reader:
                if len(row) >= 2:
                    if row[0] == username and row[1] == self.hash_password(password):
                        messagebox.showinfo("Login", "Logged in successfully!")
                        self.login_frame.pack_forget()
                        self.create_main_menu()
                        return
        messagebox.showerror("Login", "Incorrect username or password.")

    def register(self):
        """פונקציה לרישום משתמש חדש"""
        username = self.username_entry.get()
        password = self.password_entry.get()

        if not username or not password:
            messagebox.showerror("Register", "Username and password cannot be empty.")
            return

        # הצפנת הסיסמה
        hashed_password = self.hash_password(password)

        # בדיקה אם המשתמש קיים
        with open("users.csv", mode="r") as file:
            reader = csv.reader(file)
            for row in reader:
                if row[0] == username:
                    messagebox.showerror("Register", f"User {username} already exists.")
                    return

        # שמירת המשתמש בקובץ
        with open("users.csv", mode="a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([username, hashed_password])

        messagebox.showinfo("Register", f"User {username} registered successfully!")
        self.login_frame.pack_forget()
        self.create_main_menu()

    def hash_password(self, password):
        """הצפנת סיסמא"""
        return hashlib.sha256(password.encode()).hexdigest()

    def create_main_menu(self):
        """יצירת תפריט ראשי אחרי התחברות או רישום מוצלח"""
        self.main_menu.pack(padx=20, pady=20)

        menu_buttons = [
            ("Add Book", self.added_gui),
            ("Remove Book", self.removed_gui),
            ("Lend Book", self.loaned_gui),
            ("Return Book", self.returned_gui),
            ("View Books", self.view_books_gui),
            ("Logout", self.logout),
        ]

        for text, command in menu_buttons:
            tk.Button(self.main_menu, text=text, command=command, font=("Arial", 12), width=20).pack(pady=10)

    def logout(self):
        """פונקציה להתנתקות"""
        self.username_entry.delete(0, tk.END)
        self.password_entry.delete(0, tk.END)
        self.main_menu.pack_forget()
        self.login_frame.pack(padx=20, pady=20)

    def close_window(self):
        """סגירת התוכנית בצורה תקינה"""
        self.root.quit()  # סוגר את התוכנית

    def added_gui(self):
        # יצירת חלון הוספת ספר
        add_book_window = tk.Toplevel(self.root)
        add_book_window.title("Add Book")

        # יצירת תוויות וכניסות לכל שדה
        tk.Label(add_book_window, text="Title:", font=("Arial", 12)).grid(row=0, column=0, padx=10, pady=5)
        title_entry = tk.Entry(add_book_window, font=("Arial", 12), width=30)
        title_entry.grid(row=0, column=1, padx=10, pady=5)

        tk.Label(add_book_window, text="Author:", font=("Arial", 12)).grid(row=1, column=0, padx=10, pady=5)
        author_entry = tk.Entry(add_book_window, font=("Arial", 12), width=30)
        author_entry.grid(row=1, column=1, padx=10, pady=5)

        tk.Label(add_book_window, text="Copies:", font=("Arial", 12)).grid(row=2, column=0, padx=10, pady=5)
        copies_entry = tk.Entry(add_book_window, font=("Arial", 12), width=30)
        copies_entry.grid(row=2, column=1, padx=10, pady=5)

        tk.Label(add_book_window, text="Genre:", font=("Arial", 12)).grid(row=3, column=0, padx=10, pady=5)

        genres = ["Fiction", "Dystopian", "Classic", "Adventure", "Romance", "Historical Fiction",
                  "Psychological Drama", "Philosophy", "Epic Poetry", "Gothic Fiction", "Gothic Romance",
                  "Realism", "Modernism", "Satire", "Science Fiction", "Tragedy", "Fantasy"]

        genre_combobox = ttk.Combobox(add_book_window, values=genres, font=("Arial", 12), width=28)
        genre_combobox.grid(row=3, column=1, padx=10, pady=5)
        genre_combobox.set(genres[0])  # ברירת מחדל

        tk.Label(add_book_window, text="Year:", font=("Arial", 12)).grid(row=4, column=0, padx=10, pady=5)
        year_entry = tk.Entry(add_book_window, font=("Arial", 12), width=30)
        year_entry.grid(row=4, column=1, padx=10, pady=5)

        def submit():
            title = title_entry.get()
            author = author_entry.get()
            copies = copies_entry.get()
            genre = genre_combobox.get()
            year = year_entry.get()

            if title and author and copies and genre and year:
                try:
                    copies = int(copies)  # המרת copies למספר שלם
                    year = int(year)  # המרת year למספר שלם
                    book = Book(title, author, copies, genre, year)
                    self.librarian.added(book)  # קריאה לפונקציה added
                    messagebox.showinfo("Add Book", f"Book '{title}' added successfully!")
                    add_book_window.destroy()
                except ValueError:
                    messagebox.showerror("Add Book", "Copies and year must be integers.")
            else:
                messagebox.showerror("Add Book", "All fields must be filled!")
            # CSVHandler.save_books_to_csv(self.books)  # שומר את השינויים בקובץ CSV

        submit_button = tk.Button(add_book_window, text="Add Book", command=submit, font=("Arial", 12), width=20)
        submit_button.grid(row=5, columnspan=2, pady=10)

    def removed_gui(self):
        # יצירת חלון הסרת ספר
        remove_book_window = tk.Toplevel(self.root)
        remove_book_window.title("Remove Book")

        tk.Label(remove_book_window, text="Enter Book Title to Remove:", font=("Arial", 12)).pack(pady=10)
        title_entry = tk.Entry(remove_book_window, font=("Arial", 12), width=30)
        title_entry.pack(pady=5)

        def submit():
            title = title_entry.get()
            if title in self.books:
                book = self.books[title]
                self.librarian.removed(book)  # קריאה לפונקציה remove_book
                messagebox.showinfo("Remove Book", f"Book '{title}' removed successfully!")
                remove_book_window.destroy()
            else:
                messagebox.showerror("Remove Book", "Book not found!")
            # CSVHandler.save_books_to_csv(self.books)  # שומר את השינויים בקובץ CSV

        submit_button = tk.Button(remove_book_window, text="Remove Book", command=submit, font=("Arial", 12), width=20)
        submit_button.pack(pady=10)

    def loaned_gui(self):
        # יצירת חלון השאלת ספר
        lend_book_window = tk.Toplevel(self.root)
        lend_book_window.title("Lend Book")

        tk.Label(lend_book_window, text="Enter Book Title to Lend:", font=("Arial", 12)).pack(pady=10)
        title_entry = tk.Entry(lend_book_window, font=("Arial", 12), width=30)
        title_entry.pack(pady=5)

        def submit():
            title = title_entry.get()
            if title in self.books:
                book = self.books[title]
                self.librarian.loaned(book)  # קריאה לפונקציה loaned
                messagebox.showinfo("Lend Book", f"Book '{title}' lent successfully!")
                lend_book_window.destroy()
            else:
                messagebox.showerror("Lend Book", "Book not found!")
            # CSVHandler.save_books_to_csv(self.books)  # שומר את השינויים בקובץ CSV

        submit_button = tk.Button(lend_book_window, text="Lend Book", command=submit, font=("Arial", 12), width=20)
        submit_button.pack(pady=10)

    def returned_gui(self):
        # יצירת חלון החזרת ספר
        return_book_window = tk.Toplevel(self.root)
        return_book_window.title("Return Book")

        tk.Label(return_book_window, text="Enter Book Title to Return:", font=("Arial", 12)).pack(pady=10)
        title_entry = tk.Entry(return_book_window, font=("Arial", 12), width=30)
        title_entry.pack(pady=5)

        def submit():
            title = title_entry.get()
            if title in self.books:
                book = self.books[title]
                self.librarian.returned(book)  # קריאה לפונקציה returned
                messagebox.showinfo("Return Book", f"Book '{title}' returned successfully!")
                return_book_window.destroy()
            else:
                messagebox.showerror("Return Book", "Book not found!")
            # CSVHandler.save_books_to_csv(self.books)  # שומר את השינויים בקובץ CSV

        submit_button = tk.Button(return_book_window, text="Return Book", command=submit, font=("Arial", 12), width=20)
        submit_button.pack(pady=10)

    def view_books_gui(self):
        # יצירת חלון תצוגת ספרים
        view_books_window = tk.Toplevel(self.root)
        view_books_window.title("View Books")

        # הגדרת עמודות כולל עותקים זמינים וכוללים
        columns = ("Title", "Author", "Genre", "Year", "Copies Available", "Total Copies")

        # יצירת Treeview להצגת הספרים
        tree = ttk.Treeview(view_books_window, columns=columns, show="headings")
        tree.pack(padx=10, pady=10)

        # הוספת כותרות לעמודות
        for col in columns:
            tree.heading(col, text=col)

        # הוספת ספרים לרשימה, כולל כמות העותקים הכוללת
        for book in self.books.values():
            tree.insert("", "end", values=(book.title, book.author, book.genre, book.year,
                                           book.available_copies, book.total_copies))

        tree.pack(padx=10, pady=10)


if __name__ == "__main__":
    app = LibraryApp()
    app.root.mainloop()
