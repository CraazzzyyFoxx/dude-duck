from pydantic import BaseModel, ConfigDict, Field

__all__ = ("OrderChannelBase",
           "OrderChannel",
           "OrderChannelCreate",
           "OrderChannelUpdate",
           "OrderChannelID")


class OrderChannelBase(BaseModel):
    game: str | None
    category: str | None = Field(default=None, min_length=1)
    channel_id: int | None


class OrderChannel(OrderChannelBase):
    game: str
    category: str | None = Field(default=None, min_length=1)
    channel_id: int


class OrderChannelCreate(OrderChannel):
    pass


class OrderChannelUpdate(OrderChannelBase):
    pass


class OrderChannelID(OrderChannel):
    model_config = ConfigDict(from_attributes=True)

    id: int
