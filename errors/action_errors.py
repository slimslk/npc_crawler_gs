from errors.base_error import BaseError


class IncorrectActionValues(BaseError):
    message: str = "Incorrect action or parameters value"

