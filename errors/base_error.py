class BaseError(Exception):
    message: str = None
    details: dict[str, str] = None

    def __init__(self, message: str = None, details: dict[str, str] | None = None) -> None:
        self.message = message
        self.details = details
        super().__init__(self.message)

    def to_dict(self) -> dict[str, str]:
        return {
            "message": self.message,
            "details": self.details
        }