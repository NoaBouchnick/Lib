from Error.CustomException import CustomException


class UseDoesNotExistException(CustomException):
    """Exception raised for invalid year."""

    def __init__(self, message="User does not exist in the system."):
        self.message = message
        super().__init__(self.message)