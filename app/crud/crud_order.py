from loguru import logger

from app.crud.base import CRUDBase
from app.db import OrderModel
from app.schemas import OrderCreate, OrderUpdate, OrderID


class CRUDOrder(CRUDBase[OrderModel, OrderCreate, OrderUpdate]):
    async def get_by_game(self, order_id: int, game: str):
        return await self.model.filter(order_id=order_id, game=game).first()


OrderCRUD = CRUDOrder(OrderModel)
