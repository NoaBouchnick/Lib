from Error.CustomException import CustomException


class UserExistsInTheSystemException(CustomException):
    """Exception raised for invalid year."""

    def __init__(self, message="User exists in the system."):
        self.message = message
        super().__init__(self.message)