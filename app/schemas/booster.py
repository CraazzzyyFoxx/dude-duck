from pydantic import BaseModel, ConfigDict, Field, EmailStr
from pydantic_extra_types.phone_numbers import PhoneNumber
from pydantic_extra_types.payment import PaymentCardNumber

__all__ = ("BoosterBase",
           "Booster",
           "BoosterCreate",
           "BoosterUpdate",
           "BoosterID",
           )


class BoosterBase(BaseModel):
    user_id: int | None = None
    username: str | None = None
    verified: bool = Field(default=True)
    strict: bool = Field(default=False)
    max_count_orders: int = Field(default=100)

    name: str | None = None
    rub: int | None = None
    binance: EmailStr | None = None
    gold: str | None = None
    description: str | None = None
    discord: str | None = None


class Booster(BoosterBase):
    name: str
    description: str
    username: str
    rub: PhoneNumber | PaymentCardNumber | None = None
    binance: EmailStr | None = None
    gold: str | None = None
    discord: str | None = None


class BoosterCreate(Booster):
    user_id: int


class BoosterUpdate(BoosterBase):
    pass


class BoosterID(Booster):
    model_config = ConfigDict(from_attributes=True)

    id: int
