import tkinter as tk
from tkinter import messagebox
import hashlib
import csv
from tkinter import ttk
import os

from Error.BookDoesNotExistException import BookDoesNotExistException
from Error.CustomException import CustomException
from Error.NoCopyAvailableException import NoCopyAvailableException
from Books.Book import Book
from Library.Customer import Customer
from Library.Librarian import Librarian
from search.Search import Search
from search.SearchStrategy import TitleSearchStrategy, AuthorSearchStrategy, GenreSearchStrategy


class LibraryApp:
    def __init__(self, file_path=None):
        self.root = tk.Tk()
        self.root.title("Library Management System")
        self.root.configure(bg='#f0f8ff')

        self.root.bind("<Configure>", self.on_resize)
        self.root.protocol("WM_DELETE_WINDOW", self.close_window)

        # קביעת נתיבי ברירת מחדל אם לא התקבלו
        if file_path is None:
            base_path = os.path.dirname(os.path.abspath(__file__))
            file_path = os.path.join(base_path, 'files', 'books.csv')
            waiting_list_path = os.path.join(base_path, 'files', 'waiting_list.csv')
        else:
            base_dir = os.path.dirname(file_path)
            waiting_list_path = os.path.join(base_dir, 'files', 'waiting_list.csv')

        # יצירת אובייקט Librarian עם שני הנתיבים
        self.librarian = Librarian(books_path=file_path, waiting_list_path=waiting_list_path)

        self.main_menu = tk.Frame(self.root)
        self.login_frame = tk.Frame(self.root, bg='#f0f8ff')
        self.create_login_screen()

        # טעינת הספרים - עכשיו ישירות מה-Librarian
        self.books = self.librarian.books

    def on_resize(self, event):
        """Resize elements when window is resized"""
        new_width = event.width
        new_height = event.height
        if hasattr(self, 'tree'):
            self.tree.config(width=new_width - 20, height=new_height - 20)

    def create_login_screen(self):
        """Create a login screen with a modern design"""
        self.login_frame.pack(fill="both", expand=True, padx=30, pady=30)

        title_label = tk.Label(self.login_frame, text="Welcome to the Library", font=("Arial", 24, "bold"),
                               fg="#4b0082", bg="#f0f8ff")
        title_label.pack(pady=20)

        tk.Label(self.login_frame, text="Username", font=("Arial", 14), bg="#f0f8ff").pack(pady=10)
        self.username_entry = tk.Entry(self.login_frame, font=("Arial", 12), width=30, bd=2, relief="groove")
        self.username_entry.pack(pady=5)

        tk.Label(self.login_frame, text="Password", font=("Arial", 14), bg="#f0f8ff").pack(pady=10)
        self.password_entry = tk.Entry(self.login_frame, show="*", font=("Arial", 12), width=30, bd=2, relief="groove")
        self.password_entry.pack(pady=5)

        login_button = tk.Button(self.login_frame, text="Login", command=self.login, font=("Arial", 14), bg="#4b0082",
                                 fg="white", width=20, height=2, relief="raised", bd=3)
        login_button.pack(pady=10)

        register_button = tk.Button(self.login_frame, text="Register", command=self.register, font=("Arial", 14),
                                    bg="#32cd32", fg="white", width=20, height=2, relief="raised", bd=3)
        register_button.pack(pady=10)

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        with open("files/users.csv", mode="r", encoding='utf-8') as file:
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
        username = self.username_entry.get()
        password = self.password_entry.get()

        if not username or not password:
            messagebox.showerror("Register", "Username and password cannot be empty.")
            self.librarian.logger.log_error("Registered in fail")
            return

        hashed_password = self.hash_password(password)

        with open("files/users.csv", mode="r", encoding='utf-8') as file:
            reader = csv.reader(file)
            for row in reader:
                if row[0] == username:
                    messagebox.showerror("Register", f"User {username} already exists.")
                    self.librarian.logger.log_error("Registered in fail")
                    return

        with open("files/users.csv", mode="a", newline="", encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow([username, hashed_password])

        messagebox.showinfo("Register", f"User {username} registered successfully!")
        self.librarian.logger.log_info("Registered in successfully")
        self.login_frame.pack_forget()
        self.create_main_menu()

    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def create_main_menu(self):
        for widget in self.main_menu.winfo_children():
            widget.pack_forget()

        # Set consistent background color for the main menu
        self.main_menu.config(bg="#f0f8ff")

        self.main_menu.pack(fill="both", expand=True, padx=20, pady=20)

        title_label = tk.Label(self.main_menu, text="Library - Main Menu", font=("Arial", 18, "bold"), fg="#4b0082",
                               bg="#f0f8ff")
        title_label.pack(pady=20)

        menu_buttons = [
            ("Add Book", self.added_gui),
            ("Remove Book", self.removed_gui),
            ("Lend Book", self.loaned_gui),
            ("Return Book", self.returned_gui),
            ("View Books", self.view_books_gui),
            ("Search Books", self.search_books_gui),
            ("waiting list", self.show_waiting_lists),
            ("Logout", self.logout),
        ]

        # Set consistent background color for buttons
        for text, command in menu_buttons:
            tk.Button(self.main_menu, text=text, command=command, font=("Arial", 12), fg="green",
                      width=20).pack(fill="both", expand=True, pady=10)

    def logout(self):
        self.username_entry.delete(0, tk.END)
        self.password_entry.delete(0, tk.END)
        self.main_menu.pack_forget()
        self.login_frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)
        self.librarian.logger.log_info("log out successful")

    def close_window(self):
        self.root.quit()

    # Continue with the rest of your code...

    def added_gui(self):
        """Create Add Book window"""

        add_book_window = tk.Toplevel(self.root)
        add_book_window.title("Add Book")
        add_book_window.config(bg="#f0f8ff")  # הגדרת הרקע של חלון ה-Add Book

        # Create labels and entries for each field
        tk.Label(add_book_window, text="Title:", font=("Arial", 12), fg="#4b0082", bg="#f0f8ff").grid(row=0, column=0,
                                                                                                      padx=10, pady=5,
                                                                                                      sticky="nsew")
        title_entry = tk.Entry(add_book_window, font=("Arial", 12), width=30)
        title_entry.grid(row=0, column=1, padx=10, pady=5, sticky="nsew")

        tk.Label(add_book_window, text="Author:", font=("Arial", 12), fg="#4b0082", bg="#f0f8ff").grid(row=1, column=0,
                                                                                                       padx=10, pady=5,
                                                                                                       sticky="nsew")
        author_entry = tk.Entry(add_book_window, font=("Arial", 12), width=30)
        author_entry.grid(row=1, column=1, padx=10, pady=5, sticky="nsew")

        tk.Label(add_book_window, text="Copies:", font=("Arial", 12), fg="#4b0082", bg="#f0f8ff").grid(row=2, column=0,
                                                                                                       padx=10, pady=5,
                                                                                                       sticky="nsew")
        copies_entry = tk.Entry(add_book_window, font=("Arial", 12), width=30)
        copies_entry.grid(row=2, column=1, padx=10, pady=5, sticky="nsew")

        tk.Label(add_book_window, text="Genre:", font=("Arial", 12), fg="#4b0082", bg="#f0f8ff").grid(row=3, column=0,
                                                                                                      padx=10, pady=5,
                                                                                                      sticky="nsew")

        genres = ["Fiction", "Dystopian", "Classic", "Adventure", "Romance", "Historical Fiction",
                  "Psychological Drama", "Philosophy", "Epic Poetry", "Gothic Fiction", "Gothic Romance",
                  "Realism", "Modernism", "Satire", "Science Fiction", "Tragedy", "Fantasy"]

        genre_combobox = ttk.Combobox(add_book_window, values=genres, font=("Arial", 12), width=28)
        genre_combobox.grid(row=3, column=1, padx=10, pady=5, sticky="nsew")
        genre_combobox.set(genres[0])  # Default selection

        tk.Label(add_book_window, text="Year:", font=("Arial", 12), fg="#4b0082", bg="#f0f8ff").grid(row=4, column=0,
                                                                                                     padx=10, pady=5,
                                                                                                     sticky="nsew")
        year_entry = tk.Entry(add_book_window, font=("Arial", 12), width=30)
        year_entry.grid(row=4, column=1, padx=10, pady=5, sticky="nsew")

        def submit():
            title = title_entry.get()
            author = author_entry.get()
            copies = copies_entry.get()
            genre = genre_combobox.get()
            year = year_entry.get()

            if title and author and copies and genre and year:
                try:
                    copies = int(copies)  # Convert copies to an integer
                    year = int(year)  # Convert year to an integer
                    book = Book(title, author, copies, genre, year)  # Create book with is_loaned as "No"
                    self.librarian.added(book)  # Call added function to add the book
                    messagebox.showinfo("Success", f"Book {title} added successfully!")
                    self.books[title] = book  # עדכון המילון עם הספר החדש
                    # self.librarian.logger.log_info("Book added successfully")
                    add_book_window.destroy()
                except ValueError as e:
                    messagebox.showerror("Error", "Invalid input for copies or year.")
                    self.librarian.logger.log_error("Book added fail")
                except Exception as e:
                    messagebox.showerror("Error", f"An unexpected error occurred: {e}")
                    self.librarian.logger.log_error("Book added fail")
                add_book_window.destroy()
            else:
                messagebox.showerror("Error", "All fields are required.")

        submit_button = tk.Button(add_book_window, text="Add Book", command=submit, font=("Arial", 12), bg="#32cd32",
                                  fg="white")
        submit_button.grid(row=5, column=0, columnspan=2, pady=10)

    def removed_gui(self):
        # יצירת חלון הסרת ספר
        remove_book_window = tk.Toplevel(self.root)
        remove_book_window.title("Remove Book")
        remove_book_window.configure(bg="#f0f8ff")  # הגדרת הרקע של חלון הסרת הספר

        tk.Label(remove_book_window, text="Enter Book Title to Remove:", font=("Arial", 12), fg="#4b0082",
                 bg="#f0f8ff").pack(pady=10)
        title_entry = tk.Entry(remove_book_window, font=("Arial", 12), width=30)
        title_entry.pack(pady=5)

        def submit():
            title = title_entry.get()
            if title:
                try:
                    # אם הספר קיים במילון
                    if title in self.books:
                        book = self.books[title]
                        removal_successful = self.librarian.removed(book)  # קריאה לפונקציה removed

                        if removal_successful:
                            messagebox.showinfo("Remove Book", "Book removed successfully!")
                        else:
                            messagebox.showerror("Remove Book", "Book could not be removed.")
                    else:
                        messagebox.showerror("Remove Book", "Book not found!")
                        self.librarian.logger.log_error("Book removed fail")

                except (CustomException) as e:
                    messagebox.showerror("Remove Book", f"Error: {str(e)}")
                    self.librarian.logger.log_error("Book removed fail")

                except Exception as e:
                    # כל שגיאה לא צפויה
                    messagebox.showerror("Remove Book", f"Unexpected error: {str(e)}")
                    self.librarian.logger.log_error("Book removed fail")

                remove_book_window.destroy()

            else:
                messagebox.showerror("Remove Book", "Please enter a book title.")

        # יצירת כפתור להסרת הספר
        submit_button = tk.Button(remove_book_window, text="Remove Book", command=submit, font=("Arial", 12),
                                  bg="#32cd32", fg="white")
        submit_button.pack(pady=10)

    def loaned_gui(self):
        lend_book_window = tk.Toplevel(self.root)
        lend_book_window.title("Lend Book")
        lend_book_window.configure(bg="#f0f8ff")

        tk.Label(lend_book_window, text="Enter Book Title to Lend:", font=("Arial", 12), fg="#4b0082",
                 bg="#f0f8ff").pack(pady=10)
        title_entry = tk.Entry(lend_book_window, font=("Arial", 12), width=30)
        title_entry.pack(pady=5)

        def submit():
            title = title_entry.get()
            if title:
                try:
                    if title in self.books:
                        book = self.books[title]
                        try:
                            loaned_successful = self.librarian.loaned(book)
                            if loaned_successful:
                                messagebox.showinfo("Lend Book", f"Book '{title}' lent successfully!")
                            lend_book_window.destroy()
                        except NoCopyAvailableException:
                            ans = messagebox.askquestion("No Copies Available",
                                                         f"No copy available for '{title}'. Would you like to get on the waiting list?")
                            if ans == "yes":
                                self.request_customer_details(book)  # שימוש במתודה של המחלקה
                            lend_book_window.destroy()
                    else:
                        self.librarian.logger.log_error("Book borrowed  fail")
                        messagebox.showerror("Book not found", f"Book '{title}' not found.")
                except Exception as e:
                    messagebox.showerror("Lend Book", f"Unexpected error: {str(e)}")
                    self.librarian.logger.log_error("Book borrowed  fail")
                    lend_book_window.destroy()
            else:
                messagebox.showerror("Lend Book", "Please enter a book title.")

        submit_button = tk.Button(lend_book_window, text="Lend Book", command=submit, font=("Arial", 12), bg="#32cd32",
                                  fg="white", width=20)
        submit_button.pack(pady=10)

    def request_customer_details(self, book):
        customer_window = tk.Toplevel(self.root)
        customer_window.title("Enter Customer Details")
        customer_window.configure(bg="#f0f8ff")

        tk.Label(customer_window, text="Enter your name:", font=("Arial", 12), fg="#4b0082", bg="#f0f8ff").pack(
            pady=5)
        name_entry = tk.Entry(customer_window, font=("Arial", 12), width=30)
        name_entry.pack(pady=5)

        tk.Label(customer_window, text="Enter your phone number:", font=("Arial", 12), fg="#4b0082",
                 bg="#f0f8ff").pack(pady=5)
        phone_entry = tk.Entry(customer_window, font=("Arial", 12), width=30)
        phone_entry.pack(pady=5)

        tk.Label(customer_window, text="Enter your email:", font=("Arial", 12), fg="#4b0082", bg="#f0f8ff").pack(
            pady=5)
        email_entry = tk.Entry(customer_window, font=("Arial", 12), width=30)
        email_entry.pack(pady=5)

        def submit_customer_details():
            name = name_entry.get()
            phone = phone_entry.get()
            email = email_entry.get()

            if name and phone and email:
                try:
                    customer = Customer(name, phone, email)
                    self.librarian.waiting_for_book(book, customer)
                    messagebox.showinfo("Success", f"'{name}' added to waiting list for '{book.title}'.")
                    customer_window.destroy()
                except ValueError as e:
                    messagebox.showerror("Error", str(e))  # יציג את ההודעה שהלקוח כבר רשום
                except Exception as e:
                    messagebox.showerror("Error", f"An unexpected error occurred: {str(e)}")
            else:
                messagebox.showerror("Error", "Please fill all fields.")

        submit_button = tk.Button(customer_window, text="Submit", command=submit_customer_details,
                                  font=("Arial", 12), bg="#32cd32", fg="white", width=20)
        submit_button.pack(pady=10)

    def returned_gui(self):
        # יצירת חלון החזרת ספר
        return_book_window = tk.Toplevel(self.root)
        return_book_window.title("Return Book")
        return_book_window.configure(bg="#f0f8ff")

        tk.Label(return_book_window, text="Enter Book Title to Return:", font=("Arial", 12), fg="#4b0082",
                 bg="#f0f8ff").pack(pady=10)
        title_entry = tk.Entry(return_book_window, font=("Arial", 12), width=30)
        title_entry.pack(pady=5)

        def submit():
            title = title_entry.get()
            if title:
                try:
                    if title in self.books:
                        book = self.books[title]
                        returned_successful = self.librarian.returned(book)  # קריאה לפונקציה returned
                        if returned_successful:
                            messagebox.showinfo("Return Book", f"Book '{title}' returned successfully!")
                        else:
                            messagebox.showerror("There are no borrowed copies")
                        return_book_window.destroy()
                    else:
                        raise BookDoesNotExistException("Book not found in the system.")  # שגיאה אם הספר לא נמצא

                except CustomException as e:
                    messagebox.showerror("Return Book", f"Error: {str(e)}")
                    self.librarian.logger.log_error("Book return fail")

                except Exception as e:
                    # כל שגיאה לא צפויה
                    messagebox.showerror("Return Book", f"Unexpected error: {str(e)}")
                    self.librarian.logger.log_error("Book return fail")

                return_book_window.destroy()

            else:
                messagebox.showerror("Return Book", "Please enter a book title.")

        # יצירת כפתור להחזרת הספר
        submit_button = tk.Button(return_book_window, text="Return Book", command=submit, font=("Arial", 12),
                                  bg="#32cd32", fg="white", width=20)
        submit_button.pack(pady=10)

    def view_books_gui(self):
        view_books_window = tk.Toplevel(self.root)
        view_books_window.title("View Books")
        view_books_window.configure(bg="#f0f8ff")

        # יצירת מסגרת לכפתורים
        buttons_frame = tk.Frame(view_books_window, bg="#f0f8ff")
        buttons_frame.pack(pady=10)

        # הגדרת עמודות
        columns = ("Title", "Author", "Genre", "Year", "Copies Available", "Total Copies", "Loan Status")

        # יצירת Treeview להצגת הספרים
        tree = ttk.Treeview(view_books_window, columns=columns, show="headings")
        tree.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

        for col in columns:
            tree.heading(col, text=col)

        # הוספת frame חדש לבחירת קטגוריה
        category_frame = tk.Frame(view_books_window, bg="#f0f8ff")
        category_frame.pack(pady=5)

        genres = ["Fiction", "Dystopian", "Classic", "Adventure", "Romance", "Historical Fiction",
                  "Psychological Drama", "Philosophy", "Epic Poetry", "Gothic Fiction", "Gothic Romance",
                  "Realism", "Modernism", "Satire", "Science Fiction", "Tragedy", "Fantasy"]

        tk.Label(category_frame, text="Select Genre:", bg="#f0f8ff").pack(side=tk.LEFT, padx=5)
        genre_combobox = ttk.Combobox(category_frame, values=genres, width=20)
        genre_combobox.pack(side=tk.LEFT, padx=5)

        def show_all_books():
            tree.delete(*tree.get_children())
            for book in self.books.values():
                loan_status = "Yes" if book.is_loaned == "Yes" else "No"
                tree.insert("", "end", values=(book.title, book.author, book.genre, book.year,
                                               book.available_copies, book.total_copies, loan_status))
            self.librarian.logger.log_info("Displayed all books successfully")

        def show_available_books():
            tree.delete(*tree.get_children())
            available_books = [book for book in self.books.values() if book.available_copies > 0]
            if available_books:
                for book in available_books:
                    loan_status = "No"
                    tree.insert("", "end", values=(book.title, book.author, book.genre, book.year,
                                                   book.available_copies, book.total_copies, loan_status))
                self.librarian.logger.log_info("Displayed available books successfully")
            else:
                self.librarian.logger.log_error("Displayed available books fail")
                messagebox.showinfo("Info", "No available books found")

        def show_borrowed_books():
            tree.delete(*tree.get_children())
            borrowed_books = [book for book in self.books.values() if book.is_loaned == "Yes"]
            if borrowed_books:
                for book in borrowed_books:
                    loan_status = "Yes"
                    tree.insert("", "end", values=(book.title, book.author, book.genre, book.year,
                                                   book.available_copies, book.total_copies, loan_status))
                self.librarian.logger.log_info("Displayed borrowed books successfully")
            else:
                self.librarian.logger.log_error("Displayed borrowed books fail")
                messagebox.showinfo("Info", "No borrowed books found")

        def show_popular_books():
            tree.delete(*tree.get_children())
            popular_books = self.librarian.get_most_demanded_books()
            if popular_books:
                for title, demand, borrowed, waiting in popular_books:
                    book = self.books.get(title)
                    if book:
                        loan_status = "Yes" if book.is_loaned == "Yes" else "No"
                        tree.insert("", "end", values=(book.title, book.author, book.genre, book.year,
                                                       book.available_copies, book.total_copies, loan_status))
                self.librarian.logger.log_info("displayed successfully")
            else:
                self.librarian.logger.log_error("displayed fail")
                messagebox.showinfo("Info", "No popular books found")

        def show_books_by_category():
            selected_genre = genre_combobox.get()
            if not selected_genre:
                messagebox.showwarning("Warning", "Please select a genre first")
                return

            tree.delete(*tree.get_children())
            genre_books = [book for book in self.books.values() if book.genre == selected_genre]
            if genre_books:
                for book in genre_books:
                    loan_status = "Yes" if book.is_loaned == "Yes" else "No"
                    tree.insert("", "end", values=(book.title, book.author, book.genre, book.year,
                                                   book.available_copies, book.total_copies, loan_status))
                self.librarian.logger.log_info("Displayed book by category successfully")
            else:
                self.librarian.logger.log_error("Displayed book by category fail")
                messagebox.showinfo("Info", "No books found in this category")

        # יצירת כפתורים
        buttons = [
            ("All Books", show_all_books),
            ("Available Books", show_available_books),
            ("Borrowed Books", show_borrowed_books),
            ("Popular Books", show_popular_books),
            ("Filter by Genre", show_books_by_category)
        ]

        for text, command in buttons:
            tk.Button(buttons_frame, text=text, command=command,
                      font=("Arial", 12), bg="#32cd32", fg="white", width=15).pack(side=tk.LEFT, padx=5)

        # הצגת כל הספרים כברירת מחדל
        show_all_books()

    def search_books_gui(self):
        """יצירת חלון חיפוש ספרים"""
        search_window = tk.Toplevel(self.root)
        search_window.title("Search Books")
        search_window.configure(bg="#f0f8ff")

        # יצירת תוויות ושדות חיפוש
        tk.Label(search_window, text="Enter search query:", font=("Arial", 20), fg="#4b0082", bg="#f0f8ff").pack(
            pady=25)
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
        search_button = tk.Button(search_window, text="Search", command=search_submit, font=("Arial", 12), bg="#32cd32",
                                  fg="white", width=20)
        search_button.pack(pady=10)

    def waiting_list_gui(self):
        waiting_list_window = tk.Toplevel(self.root)
        waiting_list_window.title("Waiting List")
        waiting_list_window.configure(bg="#f0f8ff")

        tk.Label(waiting_list_window, text="Enter book title:", font=("Arial", 20), fg="#4b0082", bg="#f0f8ff").pack(
            pady=25)
        search_entry = tk.Entry(waiting_list_window, font=("Arial", 12), width=30)
        search_entry.pack(pady=5)

        def submit():
            book_title = search_entry.get()

            if book_title:
                # מניחים כאן שספר עם השם הזה כבר קיים במערכת
                book = self.books.get(book_title)

                if book:
                    self.librarian.waiting_for_book(book)
                    messagebox.showinfo("Success", f"Customer added to waiting list for '{book.title}'!")
                else:
                    messagebox.showerror("Error", f"Book '{book_title}' not found.")
            else:
                messagebox.showerror("Error", "Please enter a book title.")

        submit_button = tk.Button(waiting_list_window, text="Submit", font=("Arial", 14), command=submit, bg="#4b0082",
                                  fg="white")
        submit_button.pack(pady=10)

        cancel_button = tk.Button(waiting_list_window, text="Cancel", font=("Arial", 14),
                                  command=waiting_list_window.destroy, bg="red", fg="white")
        cancel_button.pack(pady=5)

    def show_waiting_lists(self):
        # יצירת חלון חדש לתצוגת רשימות ההמתנה
        waiting_list_window = tk.Toplevel(self.root)
        waiting_list_window.title("Waiting Lists")
        waiting_list_window.configure(bg="#f0f8ff")

        # הגדרת עמודות עבור הרשימה
        columns = ("Book Title", "Customer Name", "Customer Phone", "Customer Email")

        # יצירת Treeview להצגת רשימות ההמתנה
        tree = ttk.Treeview(waiting_list_window, columns=columns, show="headings")
        tree.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

        # הוספת כותרות לעמודות
        for col in columns:
            tree.heading(col, text=col)

        # הוספת רשימות המתנה לספרים
        for title, customers in self.librarian.waiting_list.items():
            if customers:  # רק אם יש לקוחות ברשימה
                for customer in customers:
                    tree.insert("", "end", values=(title, customer.name, customer.phone, customer.email))

    def show_most_demanded_books(self):
        """מציג חלון עם 10 הספרים המבוקשים ביותר"""
        demanded_books_window = tk.Toplevel(self.root)
        demanded_books_window.title("Most Demanded Books")
        demanded_books_window.configure(bg="#f0f8ff")

        # כותרת
        tk.Label(
            demanded_books_window,
            text="Top 10 Most Demanded Books",
            font=("Arial", 18, "bold"),
            fg="#4b0082",
            bg="#f0f8ff"
        ).pack(pady=20)

        # הגדרת עמודות
        columns = ("Title", "Total Demand", "Borrowed Copies", "Waiting List")

        # יצירת Treeview להצגת הספרים
        tree = ttk.Treeview(demanded_books_window, columns=columns, show="headings")
        tree.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

        # הגדרת כותרות העמודות
        for col in columns:
            tree.heading(col, text=col)

        # קבלת הספרים המבוקשים ביותר
        most_demanded = self.librarian.get_most_demanded_books()

        # הוספת הספרים לטבלה
        for book_data in most_demanded:
            title, total_demand, borrowed, waiting = book_data
            tree.insert("", "end", values=(
                title,
                total_demand,
                borrowed,
                waiting
            ))

if __name__ == "__main__":
    app = LibraryApp()
    app.root.mainloop()
