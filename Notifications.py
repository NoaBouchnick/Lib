from Library.Book import Book
from Library.Customer import Customer
# from Library.Librarian import Librarian


class Notifications:
    def __init__(self) -> None:
        self.notifications = []
        # self.librarian = Librarian()

    def send_notification(self, customer: Customer):
        # שליחה של הודעה ללקוח
        print(f"Notifying customer: {customer.name}, {customer.phone}, {customer.email}")

    def notify_waiting_list(self, book: Book):
        # אם הספר הוחזר או הגיעו עותקים חדשים, נודיע ללקוחות ברשימת ההמתנה
        if book.title in self.librarian.waiting_list:
            # מספר העותקים הפנויים
            available_copies = book.available_copies

            # נשלח הודעה רק למספר המתאים של לקוחות ברשימה
            waiting_customers = self.librarian.waiting_list[book.title]

            # שלח הודעה ללקוחות על פי מספר העותקים הפנויים
            for i in range(min(available_copies, len(waiting_customers))):
                self.send_notification(waiting_customers[i])

            # נעדכן את רשימת ההמתנה, נמחק את הלקוחות שנעשתה להם הודעה
            self.librarian.waiting_list[book.title] = waiting_customers[min(available_copies, len(waiting_customers)):]  # תיקון כאן

            # אחרי שליחת ההודעה, ננקה את רשימת ההמתנה (או עדכון של הלקוחות שעדיין מחכים)
            print(f"Notified and removed {min(available_copies, len(waiting_customers))} customers from the waiting list.") 

    # דקורטור לדחיפת לוג לפעולות שונות:
    # def log_action(func):
    #     def wrapper(self, *args, **kwargs):
    #         try:
    #             result = func(self, *args, **kwargs)
    #             self.logger.log_info(f"Action {func.__name__} succeeded.")
    #             return result
    #         except Exception as e:
    #             self.logger.log_error(f"Action {func.__name__} failed: {e}")
    #             raise
    #     return wrapper