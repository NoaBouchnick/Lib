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
from search.SearchStrategy import TitleSearchStrategy, AuthorSearchStrategy, GenreSearchStrategy, YearSearchStrategy


# initialize the library manegment system application
class LibraryApp:
    #initialize the root GUI window
    def __init__(self, file_path=None):
        self.root = tk.Tk()
        self.root.title("Library Management System")
        self.root.configure(bg='#f0f8ff')

        #bind resizing event and handle window close
        self.root.bind("<Configure>", self.on_resize)
        self.root.protocol("WM_DELETE_WINDOW", self.close_window)

        # set default file paths if non are provided
        if file_path is None:
            base_path = os.path.dirname(os.path.abspath(__file__))
            file_path = os.path.join(base_path, 'files', 'books.csv')
            waiting_list_path = os.path.join(base_path, 'files', 'waiting_list.csv')
        else:
            base_dir = os.path.dirname(file_path)
            waiting_list_path = os.path.join(base_dir, 'files', 'waiting_list.csv')

        # create librarian object to manage books and waiting lists
        self.librarian = Librarian(books_path=file_path, waiting_list_path=waiting_list_path)

        #initialize main menu and login frame
        self.main_menu = tk.Frame(self.root)
        self.login_frame = tk.Frame(self.root, bg='#f0f8ff')
        self.create_login_screen()

        # load books directly from librarian object
        self.books = self.librarian.books

    #handle resizing events to adjust GUI elements dynamically
    def on_resize(self, event):
        new_width = event.width
        new_height = event.height
        #adjust the size of the tree widget if it exists
        if hasattr(self, 'tree'):
            self.tree.config(width=new_width - 20, height=new_height - 20)

    #create a login screen with a modern and user friendly design
    def create_login_screen(self):
        self.login_frame.pack(fill="both", expand=True, padx=30, pady=30)

        #title label
        title_label = tk.Label(self.login_frame, text="Welcome to the Library", font=("Arial", 24, "bold"),
                               fg="#4b0082", bg="#f0f8ff")
        title_label.pack(pady=20)

        #username field
        tk.Label(self.login_frame, text="Username", font=("Arial", 14), bg="#f0f8ff").pack(pady=10)
        self.username_entry = tk.Entry(self.login_frame, font=("Arial", 12), width=30, bd=2, relief="groove")
        self.username_entry.pack(pady=5)

        #password field
        tk.Label(self.login_frame, text="Password", font=("Arial", 14), bg="#f0f8ff").pack(pady=10)
        self.password_entry = tk.Entry(self.login_frame, show="*", font=("Arial", 12), width=30, bd=2, relief="groove")
        self.password_entry.pack(pady=5)

        #login button
        login_button = tk.Button(self.login_frame, text="Login", command=self.login, font=("Arial", 14), bg="#4b0082",
                                 fg="white", width=20, height=2, relief="raised", bd=3)
        login_button.pack(pady=10)

        #register button
        register_button = tk.Button(self.login_frame, text="Register", command=self.register, font=("Arial", 14),
                                    bg="#32cd32", fg="white", width=20, height=2, relief="raised", bd=3)
        register_button.pack(pady=10)

    #handle login process by validating the users credentials against a stored CVS file
    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        #oper and read users.cvs
        with open("files/users.csv", mode="r", encoding='utf-8') as file:
            reader = csv.reader(file)
            for row in reader:
                if len(row) >= 2:
                    #check if username and hashed password match
                    if row[0] == username and row[1] == self.hash_password(password):
                        messagebox.showinfo("Login", "Logged in successfully!")
                        self.librarian.logger.log_info("logged in successfully")
                        self.login_frame.pack_forget()
                        self.create_main_menu()
                        return
        #show error message if login fails
        messagebox.showerror("Login", "Incorrect username or password.")
        self.librarian.logger.log_error("logged in fail")

    #register a new user by storing their credentials in users.cvs
    def register(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        #ensure username and password are not empty
        if not username or not password:
            messagebox.showerror("Register", "Username and password cannot be empty.")
            self.librarian.logger.log_error("Registered in fail")
            return

        hashed_password = self.hash_password(password)

        #check if the user already exists
        with open("files/users.csv", mode="r", encoding='utf-8') as file:
            reader = csv.reader(file)
            for row in reader:
                if row[0] == username:
                    messagebox.showerror("Register", f"User {username} already exists.")
                    self.librarian.logger.log_error("Registered in fail")
                    return

        #append new user to users.cvs
        with open("files/users.csv", mode="a", newline="", encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow([username, hashed_password])

        messagebox.showinfo("Register", f"User {username} registered successfully!")
        self.librarian.logger.log_info("Registered in successfully")
        self.login_frame.pack_forget()
        self.create_main_menu()

    #hash the users password using a secure hashing algorithm
    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    #create the main menu for the application after login or registration
    def create_main_menu(self):
        #clear any existing widgets in the main menu
        for widget in self.main_menu.winfo_children():
            widget.pack_forget()

        # Set consistent background color for the main menu
        self.main_menu.config(bg="#f0f8ff")

        #pack the main menu frame to fill the window
        self.main_menu.pack(fill="both", expand=True, padx=20, pady=20)

        title_label = tk.Label(self.main_menu, text="Library - Main Menu", font=("Arial", 18, "bold"), fg="#4b0082",
                               bg="#f0f8ff")
        title_label.pack(pady=20)

        #define the buttons and their corresponding commands
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

        # create and pack each button
        for text, command in menu_buttons:
            tk.Button(self.main_menu, text=text, command=command, font=("Arial", 12), fg="green",
                      width=20).pack(fill="both", expand=True, pady=10)

    #log out the current user and return to login screen
    def logout(self):
        #clear the login entry fields
        self.username_entry.delete(0, tk.END)
        self.password_entry.delete(0, tk.END)

        #hide the main menu and show the login frame
        self.main_menu.pack_forget()
        self.login_frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)

        #log the logout function
        self.librarian.logger.log_info("log out successful")

    #close the main application window
    def close_window(self):
        self.root.quit()

    #create and display a window for adding a new book to the library
    def added_gui(self):

        add_book_window = tk.Toplevel(self.root)
        add_book_window.title("Add Book")
        add_book_window.config(bg="#f0f8ff")  # set background color of the window

        # title input
        tk.Label(add_book_window, text="Title:", font=("Arial", 12), fg="#4b0082", bg="#f0f8ff").grid(row=0, column=0,
                                                                                                      padx=10, pady=5,
                                                                                                      sticky="nsew")
        title_entry = tk.Entry(add_book_window, font=("Arial", 12), width=30)
        title_entry.grid(row=0, column=1, padx=10, pady=5, sticky="nsew")

        #author input
        tk.Label(add_book_window, text="Author:", font=("Arial", 12), fg="#4b0082", bg="#f0f8ff").grid(row=1, column=0,
                                                                                                       padx=10, pady=5,
                                                                                                       sticky="nsew")
        author_entry = tk.Entry(add_book_window, font=("Arial", 12), width=30)
        author_entry.grid(row=1, column=1, padx=10, pady=5, sticky="nsew")

        #copies input
        tk.Label(add_book_window, text="Copies:", font=("Arial", 12), fg="#4b0082", bg="#f0f8ff").grid(row=2, column=0,
                                                                                                       padx=10, pady=5,
                                                                                                       sticky="nsew")
        copies_entry = tk.Entry(add_book_window, font=("Arial", 12), width=30)
        copies_entry.grid(row=2, column=1, padx=10, pady=5, sticky="nsew")

        #genre input
        tk.Label(add_book_window, text="Genre:", font=("Arial", 12), fg="#4b0082", bg="#f0f8ff").grid(row=3, column=0,
                                                                                                      padx=10, pady=5,
                                                                                                      sticky="nsew")

        genres = ["Fiction", "Dystopian", "Classic", "Adventure", "Romance", "Historical Fiction",
                  "Psychological Drama", "Philosophy", "Epic Poetry", "Gothic Fiction", "Gothic Romance",
                  "Realism", "Modernism", "Satire", "Science Fiction", "Tragedy", "Fantasy"]

        genre_combobox = ttk.Combobox(add_book_window, values=genres, font=("Arial", 12), width=28)
        genre_combobox.grid(row=3, column=1, padx=10, pady=5, sticky="nsew")
        genre_combobox.set(genres[0])  # Default selection

        #year imput
        tk.Label(add_book_window, text="Year:", font=("Arial", 12), fg="#4b0082", bg="#f0f8ff").grid(row=4, column=0,
                                                                                                     padx=10, pady=5,
                                                                                                     sticky="nsew")
        year_entry = tk.Entry(add_book_window, font=("Arial", 12), width=30)
        year_entry.grid(row=4, column=1, padx=10, pady=5, sticky="nsew")

        #handles the submission of the new book information
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
                    self.books[title] = book  # add the book to the library
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

    #create and display a window for removing a book from the library
    def removed_gui(self):
        # create remove book window
        remove_book_window = tk.Toplevel(self.root)
        remove_book_window.title("Remove Book")
        remove_book_window.configure(bg="#f0f8ff") #set background for remove book window

        tk.Label(remove_book_window, text="Enter Book Title to Remove:", font=("Arial", 12), fg="#4b0082",
                 bg="#f0f8ff").pack(pady=10)
        title_entry = tk.Entry(remove_book_window, font=("Arial", 12), width=30)
        title_entry.pack(pady=5)

        #handles the removal of a book from the library
        def submit():
            title = title_entry.get()
            if title:
                try:
                    # if book exists in library
                    if title in self.books:
                        book = self.books[title]
                        removal_successful = self.librarian.removed(book)

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
                    # any unexpected error
                    messagebox.showerror("Remove Book", f"Unexpected error: {str(e)}")
                    self.librarian.logger.log_error("Book removed fail")

                remove_book_window.destroy()

            else:
                messagebox.showerror("Remove Book", "Please enter a book title.")

        # creating button for book removal
        submit_button = tk.Button(remove_book_window, text="Remove Book", command=submit, font=("Arial", 12),
                                  bg="#32cd32", fg="white")
        submit_button.pack(pady=10)

    # creates and displays a window for lending a book from the library
    def loaned_gui(self):
        lend_book_window = tk.Toplevel(self.root)
        lend_book_window.title("Lend Book")
        lend_book_window.configure(bg="#f0f8ff")

        tk.Label(lend_book_window, text="Enter Book Title to Lend:", font=("Arial", 12), fg="#4b0082",
                 bg="#f0f8ff").pack(pady=10)
        title_entry = tk.Entry(lend_book_window, font=("Arial", 12), width=30)
        title_entry.pack(pady=5)

        #handles the lending process
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
                                self.request_customer_details(book)
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

    #create and display a window for the user to input the costumer details to join the waiting list
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

        #handles the submission of costumer details to join the waiting list
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
                    messagebox.showerror("Error", str(e))  # error if costumer is already on the waiting list
                except Exception as e:
                    messagebox.showerror("Error", f"An unexpected error occurred: {str(e)}")
            else:
                messagebox.showerror("Error", "Please fill all fields.")

        submit_button = tk.Button(customer_window, text="Submit", command=submit_customer_details,
                                  font=("Arial", 12), bg="#32cd32", fg="white", width=20)
        submit_button.pack(pady=10)

    #creates and displays a window for returning books to the library
    def returned_gui(self):
        return_book_window = tk.Toplevel(self.root)
        return_book_window.title("Return Book")
        return_book_window.configure(bg="#f0f8ff")

        tk.Label(return_book_window, text="Enter Book Title to Return:", font=("Arial", 12), fg="#4b0082",
                 bg="#f0f8ff").pack(pady=10)
        title_entry = tk.Entry(return_book_window, font=("Arial", 12), width=30)
        title_entry.pack(pady=5)

        #handles the return process
        def submit():
            title = title_entry.get()
            if title:
                try:
                    if title in self.books:
                        book = self.books[title]
                        returned_successful = self.librarian.returned(book)  # attempt to return the book
                        if returned_successful:
                            messagebox.showinfo("Return Book", f"Book '{title}' returned successfully!")
                        else:
                            messagebox.showerror("There are no borrowed copies")
                        return_book_window.destroy()
                    else:
                        raise BookDoesNotExistException("Book not found in the system.")  # error if the book is not found

                except CustomException as e:
                    messagebox.showerror("Return Book", f"Error: {str(e)}")
                    self.librarian.logger.log_error("Book return fail")

                except Exception as e:
                    # any unexpected error
                    messagebox.showerror("Return Book", f"Unexpected error: {str(e)}")
                    self.librarian.logger.log_error("Book return fail")

                return_book_window.destroy()

            else:
                messagebox.showerror("Return Book", "Please enter a book title.")

        # creates return book button
        submit_button = tk.Button(return_book_window, text="Return Book", command=submit, font=("Arial", 12),
                                  bg="#32cd32", fg="white", width=20)
        submit_button.pack(pady=10)

    #creates and displays a window to view books
    def view_books_gui(self):
        view_books_window = tk.Toplevel(self.root)
        view_books_window.title("View Books")
        view_books_window.configure(bg="#f0f8ff")

        # create a Search object to handle book search queries
        search = Search(
            books=self.books,
            waiting_list=self.librarian.waiting_list,
            books_borrowed=self.librarian.books_borrowed
        )

        # frame to contain buttons
        buttons_frame = tk.Frame(view_books_window, bg="#f0f8ff")
        buttons_frame.pack(pady=10)

        # define the columns for the book details
        columns = ("Title", "Author", "Genre", "Year", "Copies Available", "Total Copies", "Loan Status")

        # create a treeview widget to display the list of books
        tree = ttk.Treeview(view_books_window, columns=columns, show="headings")
        tree.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

        #set the column headings in the treeview
        for col in columns:
            tree.heading(col, text=col)

        # frame for selecting a category/genre
        category_frame = tk.Frame(view_books_window, bg="#f0f8ff")
        category_frame.pack(pady=5)

        #list of genres for dropdown menu
        genres = ["Fiction", "Dystopian", "Classic", "Adventure", "Romance", "Historical Fiction",
                  "Psychological Drama", "Philosophy", "Epic Poetry", "Gothic Fiction", "Gothic Romance",
                  "Realism", "Modernism", "Satire", "Science Fiction", "Tragedy", "Fantasy"]

        #label and combobox for selecting genre
        tk.Label(category_frame, text="Select Genre:", bg="#f0f8ff").pack(side=tk.LEFT, padx=5)
        genre_combobox = ttk.Combobox(category_frame, values=genres, width=20)
        genre_combobox.pack(side=tk.LEFT, padx=5)

        #display all books in the system
        def show_all_books():
            tree.delete(*tree.get_children())   #clear the treeview before populating
            books = search.display_all_books()  # get all books using the search class
            for book in books:
                loan_status = "Yes" if book.is_loaned == "Yes" else "No"
                tree.insert("", "end", values=(book.title, book.author, book.genre, book.year,
                                               book.available_copies, book.total_copies, loan_status))

        #display all available books
        def show_available_books():
            tree.delete(*tree.get_children())
            available_books = search.display_available_books() #get available books
            if available_books:
                for book in available_books:
                    loan_status = "No"
                    tree.insert("", "end", values=(book.title, book.author, book.genre, book.year,
                                                   book.available_copies, book.total_copies, loan_status))
            else:
                messagebox.showinfo("Info", "No available books found")

        #dispaly all borrowed books
        def show_borrowed_books():
            tree.delete(*tree.get_children())
            borrowed_books = search.display_borrowed_books()  # get borrowed books
            if borrowed_books:
                for book in borrowed_books:
                    loan_status = "Yes"
                    tree.insert("", "end", values=(book.title, book.author, book.genre, book.year,
                                                   book.available_copies, book.total_copies, loan_status))
            else:
                messagebox.showinfo("Info", "No borrowed books found")

        #display popular books
        def show_popular_books():
            tree.delete(*tree.get_children())
            popular_books = search.display_popular_books()  # get popular books
            if popular_books:
                for book in popular_books:
                    loan_status = "Yes" if book.is_loaned == "Yes" else "No"
                    tree.insert("", "end", values=(book.title, book.author, book.genre, book.year,
                                                   book.available_copies, book.total_copies, loan_status))
            else:
                messagebox.showinfo("Info", "No popular books found")

        #display books filtered by genre
        def show_books_by_category():
            selected_genre = genre_combobox.get() #get genre
            if not selected_genre:
                messagebox.showwarning("Warning", "Please select a genre first")
                return

            tree.delete(*tree.get_children())
            genre_books = search.display_books_by_genre(selected_genre)  # get books by selected genre
            if genre_books:
                for book in genre_books:
                    loan_status = "Yes" if book.is_loaned == "Yes" else "No"
                    tree.insert("", "end", values=(book.title, book.author, book.genre, book.year,
                                                   book.available_copies, book.total_copies, loan_status))
            else:
                messagebox.showinfo("Info", "No books found in this category")
        # buttons to display different categories of books
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

        #display all books as default
        show_all_books()

    #creates and displays a search books window
    def search_books_gui(self):
        search_window = tk.Toplevel(self.root)
        search_window.title("Search Books")
        search_window.configure(bg="#f0f8ff")

        # creates search books window
        search = Search(
            books=self.books,
            waiting_list=self.librarian.waiting_list,
            books_borrowed=self.librarian.books_borrowed
        )

        # label and entry for entring search query
        tk.Label(search_window, text="Enter search query:", font=("Arial", 20), fg="#4b0082", bg="#f0f8ff").pack(
            pady=25)
        search_entry = tk.Entry(search_window, font=("Arial", 12), width=30)
        search_entry.pack(pady=5)

        #dropdown menu for selecting search criteria
        search_criteria = ["Title", "Author", "Genre", "Year"]  # we added the option to search by year
        search_criteria_combobox = ttk.Combobox(search_window, values=search_criteria, font=("Arial", 12), width=28)
        search_criteria_combobox.set(search_criteria[0])
        search_criteria_combobox.pack(pady=10)

        #displays search results in a new window
        def display_results(results):
            if results:
                result_window = tk.Toplevel(search_window)
                result_window.title("Search Results")

                # treeview to diaplay the search results
                treeview = ttk.Treeview(result_window,
                                        columns=("Title", "Author", "Genre", "Year", "Available Copies", "Total Copies",
                                                 "Status"),
                                        show="headings")
                treeview.pack(pady=20, padx=20)

                # set column headings
                columns = [
                    ("Title", "Title", 150),
                    ("Author", "Author", 150),
                    ("Genre", "Genre", 100),
                    ("Year", "Year", 70),
                    ("Available Copies", "Available", 70),
                    ("Total Copies", "Total", 70),
                    ("Status", "Status", 70)
                ]

                #define column properties
                for col, heading, width in columns:
                    treeview.heading(col, text=heading)
                    treeview.column(col, width=width)

                # add books to the treeview
                for book in results:
                    status = "Available" if book.available_copies > 0 else "Not Available"
                    treeview.insert("", "end", values=(
                        book.title,
                        book.author,
                        book.genre,
                        book.year,
                        book.available_copies,
                        book.total_copies,
                        status
                    ))
            else:
                messagebox.showinfo("Search Results", "No books found.")

        #handles the search button click
        def search_submit():
            query = search_entry.get()
            criterion = search_criteria_combobox.get()

            if not query:
                messagebox.showwarning("Search", "Please enter a search query")
                return

            # choose the search strategy based on the selected criteria
            if criterion == "Title":
                strategy = TitleSearchStrategy()
            elif criterion == "Author":
                strategy = AuthorSearchStrategy()
            elif criterion == "Genre":
                strategy = GenreSearchStrategy()
            elif criterion == "Year":
                strategy = YearSearchStrategy()

            #set the chosen search strategy
            search.set_strategy(strategy)
            try:
                results = search.search(query)
                display_results(results)
            except Exception as e:
                messagebox.showerror("Search Error", f"An error occurred: {str(e)}")

        # search button
        search_button = tk.Button(search_window, text="Search", command=search_submit,
                                  font=("Arial", 12), bg="#32cd32", fg="white", width=20)
        search_button.pack(pady=10)

    #creates and displays waiting list window
    def waiting_list_gui(self):
        waiting_list_window = tk.Toplevel(self.root)
        waiting_list_window.title("Waiting List")
        waiting_list_window.configure(bg="#f0f8ff")

        #label and entry for entering book title to search for
        tk.Label(waiting_list_window, text="Enter book title:", font=("Arial", 20), fg="#4b0082", bg="#f0f8ff").pack(
            pady=25)
        search_entry = tk.Entry(waiting_list_window, font=("Arial", 12), width=30)
        search_entry.pack(pady=5)

        #handles the submission of the waiting list request
        def submit():
            book_title = search_entry.get()

            if book_title:
                # assuming the book exists in the system with the given title
                book = self.books.get(book_title)

                if book:
                    self.librarian.waiting_for_book(book)  #add costumer to the waiting list
                    messagebox.showinfo("Success", f"Customer added to waiting list for '{book.title}'!")
                else:
                    messagebox.showerror("Error", f"Book '{book_title}' not found.")
            else:
                messagebox.showerror("Error", "Please enter a book title.")

        #submit button to add to the waiting list
        submit_button = tk.Button(waiting_list_window, text="Submit", font=("Arial", 14), command=submit, bg="#4b0082",
                                  fg="white")
        submit_button.pack(pady=10)

        #cancel button to close window
        cancel_button = tk.Button(waiting_list_window, text="Cancel", font=("Arial", 14),
                                  command=waiting_list_window.destroy, bg="red", fg="white")
        cancel_button.pack(pady=5)

    #displays all waiting lists
    def show_waiting_lists(self):
        waiting_list_window = tk.Toplevel(self.root)
        waiting_list_window.title("Waiting Lists")
        waiting_list_window.configure(bg="#f0f8ff")

        # define columns for displaying costumer details in the waiting list
        columns = ("Book Title", "Customer Name", "Customer Phone", "Customer Email")

        # creat treeview widget to display waiting lists
        tree = ttk.Treeview(waiting_list_window, columns=columns, show="headings")
        tree.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

        # add headings to the columns
        for col in columns:
            tree.heading(col, text=col)

        # add waiting list data to the treeview
        for title, customers in self.librarian.waiting_list.items():
            if customers:  # only display books with costumers on the waiting list
                for customer in customers:
                    tree.insert("", "end", values=(title, customer.name, customer.phone, customer.email))

    #displays top 10 most demanded books
    def show_most_demanded_books(self):
        demanded_books_window = tk.Toplevel(self.root)
        demanded_books_window.title("Most Demanded Books")
        demanded_books_window.configure(bg="#f0f8ff")

        # label for the title of the window
        tk.Label(
            demanded_books_window,
            text="Top 10 Most Demanded Books",
            font=("Arial", 18, "bold"),
            fg="#4b0082",
            bg="#f0f8ff"
        ).pack(pady=20)

        # define columns to display information about the most demanded books
        columns = ("Title", "Total Demand", "Borrowed Copies", "Waiting List")

        # create treeview widget to display the most demanded books
        tree = ttk.Treeview(demanded_books_window, columns=columns, show="headings")
        tree.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

        # set headings for each column
        for col in columns:
            tree.heading(col, text=col)

        # get the most demanded books from the librarian
        most_demanded = self.librarian.get_most_demanded_books()

        # add each books data to the treeview
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
