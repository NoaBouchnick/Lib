class Book:
#represents book in library

# initializes book instance
    def __init__(self, title, author, copies, genre, year) -> None:
        self.title = title
        self.author = author
        self.is_loaned = "No" #default status, changes based on availability
        self.total_copies = copies  # total copies in the library
        self.available_copies = copies  # number of copies available to loan, initially all
        self.genre = genre
        self.year = year

#updates loan status of the books
    def update_loan_status(self, books):
        self.is_loaned = "Yes" if self.available_copies == 0 else "No"
        #save the updated list of books to books.cvs
        from system.CSVHandler import CSVHandler
        CSVHandler.save_books_to_csv(books)
