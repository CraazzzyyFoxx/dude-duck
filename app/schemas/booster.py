from pydantic import BaseModel, UrlConstraints, AnyHttpUrl, ConfigDict

from app.utils import TelegramUserUrl


__all__ = ("BoosterBase",
           "Booster",
           "BoosterCreate",
           "BoosterUpdate",
           "BoosterID")


class BoosterBase(BaseModel):
    user_id: int | None
    username: str | None
    tg_link: TelegramUserUrl | None
    verified: bool | None
    payment: str | None
    bank: str | None


class Booster(BoosterBase):
    user_id: int
    username: str
    tg_link: TelegramUserUrl
    verified: bool
    payment: str
    bank: str


class BoosterCreate(Booster):
    pass


class BoosterUpdate(Booster):
    pass


class BoosterID(Booster):
    model_config = ConfigDict(from_attributes=True)

    id: int
