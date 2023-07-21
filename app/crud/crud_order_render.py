from app.crud.base import CRUDBase
from app.db import OrderRenderModel
from app.schemas import RenderConfigCreate, RenderConfigUpdate


class CRUDOrderRender(CRUDBase[OrderRenderModel, RenderConfigCreate, RenderConfigUpdate]):
    async def get_by_name(self, name: str) -> OrderRenderModel:
        return await self.model.filter(name=name).first()

    async def get_by_names(self, name: list[str]) -> list[OrderRenderModel]:
        return await self.model.filter(name__in=name)


OrderRenderCRUD = CRUDOrderRender(OrderRenderModel)
