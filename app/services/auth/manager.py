import datetime
from typing import Optional

from fastapi.security import OAuth2PasswordRequestForm
from loguru import logger
from beanie import PydanticObjectId
from fastapi import Depends, Request
from fastapi_users import BaseUserManager
from fastapi_users_db_beanie import ObjectIDIDMixin, BeanieUserDatabase
from starlette.responses import Response

from app import config
from app.schemas import User


class UserManager(ObjectIDIDMixin, BaseUserManager[User, PydanticObjectId]):
    reset_password_token_secret = config.app.secret
    verification_token_secret = config.app.secret

    async def on_after_register(self, user: User, request: Optional[Request] = None):
        logger.info(f"User {user.id} has registered.")

    async def on_after_forgot_password(
            self, user: User, token: str, request: Optional[Request] = None
    ):
        logger.info(f"User {user.id} has forgot their password. Reset token: {token}")

    async def on_after_request_verify(
            self, user: User, token: str, request: Optional[Request] = None
    ):
        logger.info(f"Verification requested for user {user.id}. Verification token: {token}")

    async def on_after_login(
            self, user: User, request: Optional[Request] = None, response: Optional[Response] = None,
    ) -> None:
        pass

    async def authenticate(self, credentials: OAuth2PasswordRequestForm) -> Optional[User]:
        user: User = await super().authenticate(credentials)

        if user:
            user.last_login = datetime.datetime.utcnow()
            await user.save()

        return user


async def get_user_db():
    yield BeanieUserDatabase(User)


async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)
