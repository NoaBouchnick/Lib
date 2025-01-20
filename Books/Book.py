class Book:

    def __init__(self, title, author, copies, genre, year) -> None:
        self.title = title
        self.author = author
        self.is_loaned = "No"
        self.total_copies = copies  # המספר הכולל של עותקים
        self.available_copies = copies  # עותקים זמינים להשאלה
        self.genre = genre
        self.year = year

    def update_loan_status(self, books):
        self.is_loaned = "Yes" if self.available_copies == 0 else "No"
        from system.CSVHandler import CSVHandler
        CSVHandler.save_books_to_csv(books)  # שלח את אוסף הספרים
