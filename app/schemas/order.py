import datetime

from beanie import Indexed
from pydantic import Field, BaseModel

from .base import SheetEntity, SheetEntityDB, UpdateInterface

__all__ = (
    "Order",
    "OrderBase",
    "OrderCreate",
    "OrderUpdate",
)


class OrderMeta(BaseModel):
    order_id: str | None = None
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
    screenshot: str | None = None
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


class OrderBase(OrderMeta):
    order_id: str
    date: datetime.datetime
    exchange: float
    shop: str
    shop_order_id: str | int | None = None
    boost_type: str
    character_class: str | None = None
    nickname: str | None = None
    platform: str | None = None
    game: str
    category: str
    purchase: str
    comment: str | None = None
    contact: str
    booster: str | int | None = None
    auth_date: datetime.datetime | None = None
    status: str
    screenshot: str | None = None
    end_date: datetime.datetime | None = None

    price_dollar: float
    price_booster_dollar: float
    price_booster_dollar_fee: float
    price_booster_rub: float
    profit: float
    percent: float
    status_paid: str

    info: dict = Field(default={})


class Order(SheetEntityDB, OrderBase, UpdateInterface):
    _type = OrderBase
    order_id: Indexed(str, unique=True)
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)

    class Settings:
        name = "orders"

    @classmethod
    async def get_by_order_id(cls, order_id: str) -> "Order":
        return await cls.find_one(cls.order_id == order_id)


class OrderCreate(Order, SheetEntity):
    pass


class OrderUpdate(OrderBase, SheetEntity):
    pass
