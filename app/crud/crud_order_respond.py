from app.crud.base import CRUDBase
from app.db import OrderRespondModel
from app.schemas.order_respond import OrderRespondCreate, OrderRespondUpdate


class CRUDOrderRespond(CRUDBase[OrderRespondModel, OrderRespondCreate, OrderRespondUpdate]):
    async def get_by_order_id(self, order_id: int) -> list[OrderRespondModel]:
        return await self.model.filter(order_id=order_id)

    async def get_by_order_user_id(self, order_id: int, user_id: int) -> OrderRespondModel:
        return await self.model.filter(order_id=order_id, user_id=user_id).first()


OrderRespondCRUD = CRUDOrderRespond(OrderRespondModel)
