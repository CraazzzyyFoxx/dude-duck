import datetime

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


__all__ = (
    "Order",
    "OrderID",
    "OrderBase",
    "OrderCreate",
    "OrderUpdate",
)


class OrderBase(BaseModel):
    order_id: int | None = None
    date: datetime.datetime | None = None
    exchange: float | None = None
    shop: str | None = None
    shop_order_id: str | int | None = None
    boost_type: str | None = None
    region_fraction: str | None = None
    server: str | None = None
    character_class: str | None = None
    nickname: str | None = None
    game: str | None = None
    purchase: str | None = None
    comment: str | None = None
    battle_tag: str | None = None
    contact: str | None = None
    booster: str | int | None = None
    auth_date: datetime.datetime | None = None
    status: str | None = None
    screenshot: HttpUrl | None = None
    end_date: datetime.datetime | None = None

    price_dollar: float | None = None
    price_booster_dollar: float | None = None
    price_booster_dollar_fee: float | None = None
    price_booster_rub: float | None = None
    price_booster_gold: float | None = None
    method_payment: str | None = None
    profit: float | None = None
    share: float | None = None

    info: dict = Field(default={})


class Order(OrderBase):
    order_id: int
    date: datetime.datetime
    exchange: float
    shop: str
    shop_order_id: str | int | None = None
    boost_type: str
    region_fraction: str
    server: str | None = None
    character_class: str | None = None
    nickname: str | None = None
    game: str
    purchase: str
    comment: str | None = None
    battle_tag: str | None = None
    contact: str | None = None
    booster: str | int | None = None
    auth_date: datetime.datetime | None = None
    status: str
    screenshot: HttpUrl | None = None
    end_date: datetime.datetime | None = None

    price_dollar: float
    price_booster_dollar: float
    price_booster_dollar_fee: float
    price_booster_rub: float
    price_booster_gold: float
    method_payment: str | None = None
    profit: float
    share: float

    info: dict = Field(default={})


class OrderCreate(Order):
    pass


class OrderUpdate(OrderBase):
    pass


class OrderID(Order):
    model_config = ConfigDict(from_attributes=True)

    id: int
