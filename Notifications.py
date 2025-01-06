## לפי שם מייל וטלפון
from Library import Book, Customer


class Notifications:
    def __init__(self) -> None:
        self.notifications = []

    def send_notification(self, customer: Customer):
        # שליחה של הודעה ללקוח
        print(f"Notifying customer: {customer.name}, {customer.phone}, {customer.email}")

    def notify_waiting_list(self, book: Book):
        # אם הספר הוחזר או הגיעו עותקים חדשים, נודיע ללקוחות ברשימת ההמתנה
        if book.title in self.waiting_list:
            # מספר העותקים הפנויים
            available_copies = book.available_copies

            # נשלח הודעה רק למספר המתאים של לקוחות ברשימה
            waiting_customers = self.waiting_list[book.title]

            # שלח הודעה ללקוחות על פי מספר העותקים הפנויים
            for i in range(min(available_copies, len(waiting_customers))):
                self.send_notification(waiting_customers[i])

            # נעדכן את רשימת ההמתנה, נמחק את הלקוחות שנעשתה להם הודעה
            self.waiting_list[book.title] = waiting_customers[min(available_copies, len(waiting_customers)):]

            # אחרי שליחת ההודעה, ננקה את רשימת ההמתנה (או עדכון של הלקוחות שעדיין מחכים)
            print(
                f"Notified and removed {min(available_copies, len(waiting_customers))} customers from the waiting list.")
