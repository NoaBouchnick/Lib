from Error.CustomException import CustomException


class InvalidYearException(CustomException):
    """Exception raised for invalid year."""

    def __init__(self, message="Year must be a valid UNIX timestamp."):
        self.message = message
        super().__init__(self.message)

