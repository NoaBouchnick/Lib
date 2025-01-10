from Error.CustomException import CustomException


class InvalidBookDataException(CustomException):
    """Exception raised for invalid book data."""

    def __init__(self, message="Invalid data provided for the book."):
        self.message = message
        super().__init__(self.message)


