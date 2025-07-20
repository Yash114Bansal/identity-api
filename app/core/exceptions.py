from fastapi import HTTPException, status

class AppException(HTTPException):
    def __init__(self, detail: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        super().__init__(status_code=status_code, detail=detail)

class InvalidContactInput(AppException):
    def __init__(self, detail: str = "Invalid contact input. Provide at least email or phoneNumber."):
        super().__init__(detail=detail, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY) 