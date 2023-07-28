from pydantic import EmailStr
from pydantic_extra_types.phone_numbers import PhoneNumber
from pydantic_extra_types.payment import PaymentCardNumber

from app.schemas import SheetEntity

__all__ = ("Booster",)


class Booster(SheetEntity):
    name: str
    description: str
    username: str
    rub: PhoneNumber | PaymentCardNumber | None = None
    binance: EmailStr | None = None
    gold: str | None = None
    discord: str | None = None
