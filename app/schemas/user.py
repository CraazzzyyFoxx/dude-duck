import datetime

from typing import Optional

from beanie import PydanticObjectId
from fastapi_users import schemas
from fastapi_users_db_beanie import BeanieBaseUserDocument

from pydantic import BaseModel, HttpUrl, EmailStr, Field
from pydantic_core import Url
from pydantic_extra_types.payment import PaymentCardNumber
from pydantic_extra_types.phone_numbers import PhoneNumber
from pymongo import IndexModel
from pymongo.collation import Collation

__all__ = ("User", "UserRead", "UserCreate", "UserUpdate", "AdminGoogleToken")


class AdminGoogleToken(BaseModel):
    type: str
    project_id: str
    private_key_id: str
    private_key: str
    client_email: str
    client_id: str
    auth_uri: HttpUrl
    token_uri: HttpUrl
    auth_provider_x509_cert_url: HttpUrl
    client_x509_cert_url: HttpUrl
    universe_domain: str


class User(BeanieBaseUserDocument):
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)
    last_login: Optional[datetime.datetime] = None

    google: Optional[AdminGoogleToken] = None

    user_id: Optional[int] = None
    name: Optional[str] = None
    description: Optional[str] = None
    username: Optional[str] = None
    rub: Optional[str] = None
    binance: Optional[str] = None
    gold: Optional[str] = None
    discord: Optional[str] = None

    class Settings:
        email_collation = Collation("en", strength=2)
        indexes = [
            IndexModel("email", unique=True),
            IndexModel(
                "email", name="case_insensitive_email_index", collation=email_collation
            ),
        ]
        bson_encoders = {
            Url: lambda x: str(x)
        }

    @classmethod
    async def get_by_user_id(cls, user_id: int) -> "User":
        return await cls.find_one(cls.user_id == user_id)


class UserRead(schemas.BaseUser[PydanticObjectId]):
    pass


class UserCreate(schemas.BaseUserCreate):
    google: Optional[AdminGoogleToken] = None


class UserUpdate(schemas.BaseUserUpdate):
    google: Optional[AdminGoogleToken] = None

    user_id: Optional[int] = None
    name: Optional[str] = None
    description: Optional[str] = None
    username: Optional[str] = None
    rub: Optional[PhoneNumber | PaymentCardNumber] = None
    binance: Optional[EmailStr] = None
    gold: Optional[str] = None
    discord: Optional[str] = None
