import datetime

from pydantic import BaseModel, Field
from beanie import Document, PydanticObjectId, Link

__all__ = (
    "OrderRespond",
    "OrderRespondCreate",
    "OrderRespondUpdate",
    "OrderRespondBase",
    "OrderRespondExtra"

)

from app.schemas import User
from app.schemas.base import UpdateInterface


class OrderRespondExtra(BaseModel):
    text: str | None = Field(default=None)
    price: float | None = Field(default=None)
    start_date: datetime.datetime | None = Field(default=None)
    eta: datetime.timedelta | None = Field(default=None)


class OrderRespondBase(BaseModel):
    order_id: str | None = None
    user_id: PydanticObjectId | None = None
    username: str | None = None

    channel_id: int | None = None
    message_id: int | None = None
    message_id_admin: int | None = None

    approved: bool = Field(default=False)
    strict: bool | None = None

    extra: OrderRespondExtra | None = None


class OrderRespond(OrderRespondBase, UpdateInterface, Document):
    order_id: PydanticObjectId
    user_id: Link[User]
    username: str

    channel_id_booster: int
    message_id_booster: int
    message_id_admin: int

    approved: bool
    strict: bool

    extra: OrderRespondExtra

    @classmethod
    async def get_by_order_id(cls, order_id: PydanticObjectId) -> list["OrderRespond"]:
        return await cls.find(cls.order_id == order_id).to_list()


class OrderRespondCreate(BaseModel):
    order_id: str
    user_id: PydanticObjectId
    username: str

    channel_id: int
    message_id: int
    message_id_admin: int | None = None

    approved: bool = Field(default=False)
    strict: bool

    extra: OrderRespondExtra


class OrderRespondUpdate(OrderRespondBase):
    pass
