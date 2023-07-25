import datetime

from pydantic import BaseModel, ConfigDict, Field

__all__ = (
    "OrderRespond",
    "OrderRespondID",
    "OrderRespondCreate",
    "OrderRespondUpdate",
    "OrderRespondBase",
    "OrderRespondExtra"

)


class OrderRespondExtra(BaseModel):
    text: str | None = Field(default=None)
    price: float | None = Field(default=None)
    start_date: datetime.datetime | None = Field(default=None)
    eta: datetime.timedelta | None = Field(default=None)


class OrderRespondBase(BaseModel):
    user_id: int | None = None
    username: str | None = None

    channel_id: int | None = None
    message_id: int | None = None
    message_id_admin: int | None = None

    approved: bool | None = None
    strict: bool | None = None

    extra: OrderRespondExtra | None = None


class OrderRespond(BaseModel):
    order_id: int
    user_id: int
    username: str

    channel_id_booster: int
    message_id_booster: int
    message_id_admin: int | None = Field(default=None)

    approved: bool
    strict: bool

    extra: OrderRespondExtra


class OrderRespondCreate(OrderRespond):
    pass


class OrderRespondUpdate(OrderRespondBase):
    pass


class OrderRespondID(OrderRespond):
    model_config = ConfigDict(from_attributes=True)

    id: int
