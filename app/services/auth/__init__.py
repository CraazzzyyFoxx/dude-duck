import contextlib

from beanie import PydanticObjectId
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi_users import FastAPIUsers
from fastapi_users.authentication import AuthenticationBackend,JWTStrategy, BearerTransport
from starlette.requests import Request

from app.services.auth.manager import get_user_manager
from app.schemas import User
from app import config


__all__ = ("fastapi_users",
           "current_active_user",
           "current_active_superuser",
           "telegram_oauth2_scheme",
           "requires_authorization_telegram",
           "auth_backend")

bearer_transport = BearerTransport(tokenUrl="auth/login")


def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=config.app.secret, lifetime_seconds=3600*24)


auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)

fastapi_users = FastAPIUsers[User, PydanticObjectId](get_user_manager, [auth_backend])
current_active_user = fastapi_users.current_user(active=True)
current_active_superuser = fastapi_users.current_user(active=True, superuser=True)
get_user_manager_context = contextlib.asynccontextmanager(get_user_manager)


class TelegramHTTPBearer(HTTPBearer):
    async def __call__(self, request: Request):
        authorization = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
        if not authorization:
            if self.auto_error:
                raise HTTPException(status_code=403, detail="Not authenticated")
            else:
                return None

        return HTTPAuthorizationCredentials(scheme="Bearer", credentials=authorization)


telegram_oauth2_scheme = TelegramHTTPBearer(bearerFormat="Bearer")


async def requires_authorization_telegram(token=Depends(telegram_oauth2_scheme)):
    if token.credentials == config.app.bot_api_token:
        return token.credentials

    raise HTTPException(status_code=403, detail="Not authenticated") from None
