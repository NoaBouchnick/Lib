from Error.CustomException import CustomException


class NoCopyAvailableException(CustomException):
    """Exception raised for non-integer year or copies."""
    def __init__(self, message="Cannot be loaned, no copy available."):
        self.message = message
        super().__init__(self.message)