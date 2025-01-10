from Error.CustomException import CustomException


class NoBorrowedCopiesException(CustomException):
    """Exception raised for invalid year."""

    def __init__(self, message="There are no borrowed copies."):
        self.message = message
        super().__init__(self.message)