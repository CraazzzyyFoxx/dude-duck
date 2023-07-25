from app.crud.base import CRUDBase
from app.db import AdminModel
from app.schemas import AdminCreate, AdminUpdate


class CRUDAdmin(CRUDBase[AdminModel, AdminCreate, AdminUpdate]):
    async def get_by_token(self, token):
        return await self.model.filter(token=token).first()


AdminCRUD = CRUDAdmin(AdminModel)
