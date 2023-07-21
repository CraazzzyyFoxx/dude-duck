from app.crud.base import CRUDBase
from app.db import OrderTelegramMessageModel
from app.schemas import OrderMessageCreate, OrderMessageUpdate


class CRUDOrderMessage(CRUDBase[OrderTelegramMessageModel, OrderMessageCreate, OrderMessageUpdate]):
    async def get_by_order_id(self, order_id: int) -> list[OrderTelegramMessageModel]:
        return await self.model.filter(order_id=order_id)


OrderMessageCRUD = CRUDOrderMessage(OrderTelegramMessageModel)
