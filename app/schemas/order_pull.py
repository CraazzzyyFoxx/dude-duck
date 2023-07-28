from pydantic import BaseModel, Field

__all__ = (
    "OrderPull",
    "OrderPullCreate",
    "OrderPullUpdate"
)


class OrderPull(BaseModel):
    order_id: str
    config_names: list[str] = Field(min_items=1)


class OrderPullCreate(OrderPull):
    pass


class OrderPullUpdate(OrderPull):
    pass
