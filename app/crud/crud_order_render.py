from app.crud.base import CRUDBase
from app.db import OrderRenderModel
from app.schemas import RenderConfigCreate, RenderConfigUpdate, OrderID


class CRUDOrderRender(CRUDBase[OrderRenderModel, RenderConfigCreate, RenderConfigUpdate]):
    async def get_by_name(self, name: str) -> OrderRenderModel:
        return await self.model.filter(name=name).first()

    async def get_by_names(self, names: list[str]) -> list[OrderRenderModel]:
        data = []
        models = await self.model.filter(name__in=names)
        for name in names:
            for model in models:
                if name == model.name:
                    data.append(model)
        return data

    @staticmethod
    def get_base_names(order: OrderID):
        return ['base', order.game, 'eta-price']

    @staticmethod
    def get_base_respond_names(order: OrderID):
        return ['base', order.game, 'eta-price', 'resp']


OrderRenderCRUD = CRUDOrderRender(OrderRenderModel)
