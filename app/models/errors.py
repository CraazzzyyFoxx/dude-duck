from fastapi import HTTPException
from starlette import status


class APIError(HTTPException):
    """Base API error"""


class UnauthorizedError(APIError):
    def __init__(self):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED,
                         detail="Not authenticated",
                         headers={'WWW-Authenticate': 'Bearer'}, )