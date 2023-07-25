from pydantic import BaseModel, ConfigDict

__all__ = ("OrderMessageBase",
           "OrderMessage",
           "OrderMessageCreate",
           "OrderMessageUpdate",
           "OrderMessageID",
           "OrderMessageMeta")


class OrderMessageMeta(BaseModel):
    order_id: int | None = None
    channel_id: int | None = None


class OrderMessageBase(OrderMessageMeta):
    order_id: int
    channel_id: int


class OrderMessage(OrderMessageBase):
    order_id: int
    message_id: int


class OrderMessageCreate(OrderMessageMeta):
    config_names: list[str]


class OrderMessageUpdate(OrderMessageMeta):
    config_names: list[str]


class OrderMessageID(OrderMessage):
    model_config = ConfigDict(from_attributes=True)

    id: int
