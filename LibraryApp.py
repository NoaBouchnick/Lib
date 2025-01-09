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
from Library.Search import Search
from Library.SearchStrategy import TitleSearchStrategy, AuthorSearchStrategy, GenreSearchStrategy
from Log import Log

class LibraryApp:
    def __init__(self, file_path=None):
        # self.logger = Log()

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

        title_label = tk.Label(self.login_frame, text="Login / Register", font=("Arial", 20, "bold"))
        title_label.pack(pady=20)

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

        # self.logger = Log()

        with open("users.csv", mode="r") as file:
            reader = csv.reader(file)
            for row in reader:
                if len(row) >= 2:
                    if row[0] == username and row[1] == self.hash_password(password):
                        messagebox.showinfo("Login", "Logged in successfully!")
                        self.librarian.logger.log_info("logged in successfully")
                        self.login_frame.pack_forget()
                        self.create_main_menu()
                        return
        messagebox.showerror("Login", "Incorrect username or password.")
        self.librarian.logger.log_error("logged in fail")

    def register(self):
        """פונקציה לרישום משתמש חדש"""
        username = self.username_entry.get()
        password = self.password_entry.get()

        if not username or not password:
            messagebox.showerror("Register", "Username and password cannot be empty.")
            self.librarian.logger.log_error("Registered in fail")
            return

        # הצפנת הסיסמה
        hashed_password = self.hash_password(password)

        # בדיקה אם המשתמש קיים
        with open("users.csv", mode="r") as file:
            reader = csv.reader(file)
            for row in reader:
                if row[0] == username:
                    messagebox.showerror("Register", f"User {username} already exists.")
                    self.librarian.logger.log_error("Registered in fail")
                    return

        # שמירת המשתמש בקובץ
        with open("users.csv", mode="a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([username, hashed_password])

        messagebox.showinfo("Register", f"User {username} registered successfully!")
        self.librarian.logger.log_info("Registered in successfully")
        self.login_frame.pack_forget()
        self.create_main_menu()

    def hash_password(self, password):
        """הצפנת סיסמא"""
        return hashlib.sha256(password.encode()).hexdigest()

    def create_main_menu(self):
        """יצירת תפריט ראשי אחרי התחברות או רישום מוצלח"""
        for widget in self.main_menu.winfo_children():
            widget.pack_forget()

        self.main_menu.pack(padx=20, pady=20)

        title_label = tk.Label(self.main_menu, text="Library - Main Menu", font=("Arial", 18, "bold"))
        title_label.pack(pady=20)

        menu_buttons = [
            ("Add Book", self.added_gui),
            ("Remove Book", self.removed_gui),
            ("Lend Book", self.loaned_gui),
            ("Return Book", self.returned_gui),
            ("View Books", self.view_books_gui),
            ("Search Books", self.search_books_gui),  # כפתור חיפוש חדש
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
        self.librarian.logger.log_info("log out successfully")


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
                    book = Book(title, author, copies, genre, year)  # יצירת ספר עם is_loaned כ-"No"
                    self.librarian.added(book)  # קריאה לפונקציה added
                    messagebox.showinfo("Add Book", f"Book '{title}' added successfully!")
                    add_book_window.destroy()
                except ValueError:
                    messagebox.showerror("Add Book", "Copies and year must be integers.")
            else:
                messagebox.showerror("Add Book", "All fields must be filled!")

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
                removal_successful = self.librarian.removed(book)  # קריאה לפונקציה removed

                if removal_successful:
                    messagebox.showinfo("Remove Book", "Book removed successfully!")
                    remove_book_window.destroy()
                else:
                    messagebox.showerror("Remove Book", "Book could not be removed.")
            else:
                messagebox.showerror("Remove Book", "Book not found!")

        # יצירת כפתור להסרת הספר
        submit_button = tk.Button(remove_book_window, text="Remove Book", command=submit, font=("Arial", 12))
        submit_button.pack(pady=10)

    # בדוק שהפונקציה `removed_gui` נקראת במקום מתאים בקוד כדי לפתוח את החלון

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
                self.librarian.loaned(book,)  # קריאה לפונקציה loaned
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

        # הגדרת עמודות כולל עותקים זמינים וכוללים וסטטוס השאלה
        columns = ("Title", "Author", "Genre", "Year", "Copies Available", "Total Copies", "Loan Status")

        # יצירת Treeview להצגת הספרים
        tree = ttk.Treeview(view_books_window, columns=columns, show="headings")
        tree.pack(padx=10, pady=10)

        # הוספת כותרות לעמודות
        for col in columns:
            tree.heading(col, text=col)

        # הוספת ספרים לרשימה, כולל כמות העותקים הכוללת וסטטוס השאלה
        for book in self.books.values():
            loan_status = "Yes" if book.is_loaned == "Yes" else "No"  # קביעת סטטוס השאלה
            tree.insert("", "end", values=(book.title, book.author, book.genre, book.year,
                                           book.available_copies, book.total_copies, loan_status))

        tree.pack(padx=10, pady=10)

    import tkinter as tk
    from tkinter import ttk, messagebox

    def search_books_gui(self):
        """יצירת חלון חיפוש ספרים"""
        search_window = tk.Toplevel(self.root)
        search_window.title("Search Books")

        # יצירת תוויות ושדות חיפוש
        tk.Label(search_window, text="Enter search query:", font=("Arial", 20)).pack(pady=25)
        search_entry = tk.Entry(search_window, font=("Arial", 12), width=30)
        search_entry.pack(pady=5)

        search_criteria = ["Title", "Author", "Genre"]
        search_criteria_combobox = ttk.Combobox(search_window, values=search_criteria, font=("Arial", 12), width=28)
        search_criteria_combobox.set(search_criteria[0])  # ברירת מחדל
        search_criteria_combobox.pack(pady=10)

        def search_submit():
            query = search_entry.get()
            criterion = search_criteria_combobox.get()

            # יצירת אסטרטגיה חיפוש חדשה בהתאם למפתח
            if criterion == "Title":
                strategy = TitleSearchStrategy()
            elif criterion == "Author":
                strategy = AuthorSearchStrategy()
            else:
                strategy = GenreSearchStrategy()

            search = Search(self.books)
            search.set_strategy(strategy)

            results = search.search(query)

            # הצגת תוצאות החיפוש בחלון חדש או הודעה
            if results:
                result_window = tk.Toplevel(search_window)
                result_window.title("Search Results")

                # יצירת Treeview להצגת התוצאות בצורה מסודרת
                treeview = ttk.Treeview(result_window, columns=("Title", "Author", "Genre", "Year", "Available Copies"),
                                        show="headings")
                treeview.pack(pady=20, padx=20)

                # הגדרת כותרות העמודות
                treeview.heading("Title", text="Title")
                treeview.heading("Author", text="Author")
                treeview.heading("Genre", text="Genre")
                treeview.heading("Year", text="Year")
                treeview.heading("Available Copies", text="Available Copies")

                # הוספת נתונים ל-Treeview
                for book in results:
                    treeview.insert("", "end",
                                    values=(book.title, book.author, book.genre, book.year, book.available_copies))

            else:
                messagebox.showinfo("Search Results", "No books found.")

        # כפתור לשליחת חיפוש
        search_button = tk.Button(search_window, text="Search", command=search_submit, font=("Arial", 12), width=20)
        search_button.pack(pady=10)


if __name__ == "__main__":
    app = LibraryApp()
    app.root.mainloop()