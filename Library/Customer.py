

class Customer:
    def __init__(self, name: str, phone: str, email: str):
        self.name = name
        self.phone = phone
        self.email = email

    def __str__(self) -> str:
        return f"Customer(name: {self.name}, phone: {self.phone}, email: {self.email})"

