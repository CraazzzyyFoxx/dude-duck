from pydantic import BaseModel, Field
from beanie import Document, Indexed, PydanticObjectId, Link

__all__ = (
    "OrderMessageBase",
    "OrderMessage",
    "OrderMessageCreate",
    "OrderMessageUpdate"
)

from app.schemas import Order
from app.schemas.base import UpdateInterface


class OrderMessageBase(BaseModel):
    order_id: PydanticObjectId
    channel_id: int
    config_names: list[str] = Field(min_items=1)


class OrderMessage(Document, UpdateInterface):
    order_id: Link[Order]
    channel_id: int
    message_id: int

    @classmethod
    async def get_by_order_id(cls, order_id: PydanticObjectId) -> list["OrderMessage"]:
        return await cls.find(cls.order_id == order_id).to_list()


class OrderMessageCreate(OrderMessageBase):
    pass


class OrderMessageUpdate(OrderMessageBase):
    pass


