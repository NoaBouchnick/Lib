from Error.CustomException import CustomException


class RemovingBorrowedBookException(CustomException):
    """Exception raised for non-integer year or copies."""
    def __init__(self, message="A borrowed book cannot be removed."):
        self.message = message
        super().__init__(self.message)