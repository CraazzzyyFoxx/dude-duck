from loguru import logger

from app.crud.base import CRUDBase
from app.db import BoosterModel
from app.schemas import BoosterUpdate, BoosterCreate


class CRUDBooster(CRUDBase[BoosterModel, BoosterCreate, BoosterUpdate]):
    async def get_by_name(self, name):
        return await self.model.filter(name=name).first()

    async def get_by_username(self, name):
        return await self.model.filter(username=name).first()

    async def get_by_user_id(self, user_id: int):
        return await self.model.filter(user_id=user_id).first()


BoosterCRUD = CRUDBooster(BoosterModel)
