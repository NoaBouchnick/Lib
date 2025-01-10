from Error.CustomException import CustomException


class NonIntegerValueException(CustomException):
    """Exception raised for non-integer year or copies."""
    def __init__(self, message="Year or copies must be an integer."):
        self.message = message
        super().__init__(self.message)