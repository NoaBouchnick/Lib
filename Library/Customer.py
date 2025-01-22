import re
from typing import Optional

#represents a costumer with: name. phone number, email address
class Customer:

    # Regular expressions for validation
    PHONE_PATTERN = r'^(?:\+972|0)(?:[23489]|5[0-689]|7[0-9])[0-9]{7}$'  # Israeli phone format
    EMAIL_PATTERN = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'  # Email format

    #initializes a costumer instance
    def __init__(self, name: str, phone: str, email: str):
        self.name = name
        if not self.validate_phone(phone):
            raise ValueError("Invalid phone number format. Please use Israeli phone format (e.g., 0501234567 or +972501234567)")
        self.phone = phone

        if not self.validate_email(email):
            raise ValueError("Invalid email format. Please use a valid email address (e.g., example@domain.com)")
        self.email = email

    #validates Israeli phone number format
    @classmethod
    def validate_phone(cls, phone: str) -> bool:
        """Validates Israeli phone number format"""
        return bool(re.match(cls.PHONE_PATTERN, phone))

    #validates email address format
    @classmethod
    def validate_email(cls, email: str) -> bool:
        """Validates email format"""
        return bool(re.match(cls.EMAIL_PATTERN, email))

    #returns a string representation of the costumer object
    def __str__(self) -> str:
        return f"Customer(name: {self.name}, phone: {self.phone}, email: {self.email})"