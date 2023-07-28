import typing

from pydantic import BaseModel, Field
from beanie import Document, Indexed


__all__ = ("OrderChannelBase",
           "OrderChannel",
           "OrderChannelCreate",
           "OrderChannelUpdate"
           )

from app.schemas.base import UpdateInterface


class OrderChannelBase(BaseModel):
    game: str | None = None
    category: str | None = Field(default=None, min_length=1)
    channel_id: int | None = None


class OrderChannel(Document, OrderChannelBase, UpdateInterface):
    game: Indexed(str)
    category: str | None = Field(default=None, min_length=1)
    channel_id: int

    @classmethod
    async def get_by_game_category(cls, game: str, category: str | None) -> "OrderChannel":
        return await cls.find_one(cls.game == game, cls.category == category)


class OrderChannelCreate(OrderChannel):
    game: str
    channel_id: int


class OrderChannelUpdate(OrderChannelBase):
    game: str
