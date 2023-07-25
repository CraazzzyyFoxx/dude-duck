import binascii
import os

from fastapi import Depends
from fastapi.security.http import HTTPBearer, HTTPAuthorizationCredentials
from loguru import logger
from starlette import status
from starlette.requests import Request, HTTPException
from starlette.status import HTTP_403_FORBIDDEN

from app.schemas import AdminID, AdminCreate
from app.services.google import GoogleSheetsServiceManager
from app.crud import AdminCRUD

import config


class UnauthorizedError(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED,
                         detail="Not authenticated",
                         headers={'WWW-Authenticate': 'Bearer'}, )


class TelegramHTTPBearer(HTTPBearer):
    async def __call__(self, request: Request):
        authorization = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
        if not authorization:
            if self.auto_error:
                raise HTTPException(
                    status_code=HTTP_403_FORBIDDEN, detail="Not authenticated"
                )
            else:
                return None

        return HTTPAuthorizationCredentials(scheme="Bearer", credentials=authorization)


oauth2_scheme = HTTPBearer(bearerFormat="Bearer")
telegram_oauth2_scheme = TelegramHTTPBearer(bearerFormat="Bearer")


class AuthService:
    @classmethod
    async def requires_authorization(cls, token=Depends(oauth2_scheme)):
        if token.scheme != "Bearer":
            raise UnauthorizedError from None

        if token.credentials == config.app.api_token:
            return token.credentials

        raise UnauthorizedError from None

    @classmethod
    async def requires_authorization_admin(cls, token=Depends(oauth2_scheme)):
        if token.scheme != "Bearer":
            raise UnauthorizedError from None

        admin = await AdminCRUD.get_by_token(token.credentials)
        if admin is not None:
            return AdminID.model_validate(admin, from_attributes=True)

        raise UnauthorizedError from None

    @classmethod
    async def requires_authorization_telegram(cls, token=Depends(telegram_oauth2_scheme)):
        if token.credentials == config.app.api_token_bot:
            return token.credentials

        raise UnauthorizedError from None

    @classmethod
    async def registrate(cls, data: AdminCreate):
        data_admin = data.model_dump()
        data_admin["token"] = cls.generate_key()

        model = await AdminCRUD.create(obj_in=data_admin)
        admin = AdminID.model_validate(model, from_attributes=True)
        await GoogleSheetsServiceManager.admin_create(admin)
        return admin

    @classmethod
    def generate_key(cls):
        return binascii.hexlify(os.urandom(15)).decode()
