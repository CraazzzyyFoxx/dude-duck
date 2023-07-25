from pydantic import BaseModel, ConfigDict

__all__ = ("BoosterOrder", "BoosterOrderID")


class BoosterOrder(BaseModel):
    order_id: int
    booster_id: int
    dollars: int


class BoosterOrderID(BoosterOrder):
    model_config = ConfigDict(from_attributes=True)

    id: int
