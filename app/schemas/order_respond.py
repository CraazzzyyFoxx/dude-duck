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
    text: str | None = Field(default="")
    price: float | None = Field(default=None)
    start_date: datetime.datetime | None = Field(default=None)
    eta: datetime.timedelta | None = Field(default=None)


class OrderRespondBase(BaseModel):
    user_id: int | None
    username: str | None

    channel_id: int | None
    message_id: int | None
    message_id_admin: int | None = Field(default=None)

    approved: bool | None
    strict: bool | None

    extra: OrderRespondExtra | None


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
