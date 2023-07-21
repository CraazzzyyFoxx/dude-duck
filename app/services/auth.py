from fastapi import Depends
from fastapi.security.http import HTTPAuthorizationCredentials, HTTPBearer
from starlette.requests import Request

import config
from app.models.errors import UnauthorizedError


class TelegramHTTPBearer(HTTPBearer):
    async def __call__(self, request: Request) -> str | None:
        param = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
        if not param:
            if self.auto_error:
                raise UnauthorizedError
            else:
                return None
        return param


oauth2_scheme = HTTPBearer()
telegram_oauth2_scheme = TelegramHTTPBearer()


class AuthService:
    @classmethod
    async def is_authenticated(cls, token: str):
        if token != config.app.API_TOKEN:
            raise UnauthorizedError from None
        else:
            return True

    @classmethod
    async def requires_authorization(cls, token: str = Depends(oauth2_scheme)):
        return token

    @classmethod
    async def requires_authorization_telegram(cls, token: str = Depends(telegram_oauth2_scheme)):
        return token
