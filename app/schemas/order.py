import datetime

from pydantic import BaseModel, ConfigDict, field_validator, Field

from app.services.time import TimeService, ConversionMode

__all__ = (
    "Order",
    "OrderTelegram",
    "OrderID",
    "OrderBase",
    "OrderCreate",
    "OrderUpdate",
    "OrderMeta"
)


class OrderMeta(BaseModel):
    order_id: int | None
    game: str | None


class OrderBase(OrderMeta):
    order_id: int | None
    date: datetime.datetime | None
    exchange: float | None
    shop: str | None
    game: str | None
    category: str | None
    purchase: str | None

    price_dollar: float | None
    price_booster_rub: float | None
    price_booster_dollar: float | None
    price_booster_dollar_fee: float | None

    info: dict | None = Field(default={})

    @field_validator('date', mode='before')
    def parse_date(cls, v: str):
        if isinstance(v, datetime.datetime):
            return v
        return TimeService.convert_time(v, conversion_mode=ConversionMode.ABSOLUTE)


class Order(OrderBase):
    order_id: int
    date: datetime.datetime
    exchange: float
    shop: str
    game: str
    category: str
    purchase: str

    price_dollar: float
    price_booster_rub: float
    price_booster_dollar: float
    price_booster_dollar_fee: float

    info: dict


class OrderUpdate(OrderBase):
    pass


class OrderID(OrderBase):
    model_config = ConfigDict(from_attributes=True)

    id: int


class OrderCreate(Order):
    pass


class OrderTelegram(BaseModel):
    spreadsheet: str
    sheet_id: int
    game: str
    row: int
