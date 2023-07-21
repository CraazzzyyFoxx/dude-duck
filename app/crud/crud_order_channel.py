from app.crud.base import CRUDBase
from app.db import OrderChannelModel
from app.schemas import OrderChannelCreate, OrderChannelUpdate


class CRUDOrderChannel(CRUDBase[OrderChannelModel, OrderChannelCreate, OrderChannelUpdate]):
    async def get_by_game_category(self, game: str, category: str) -> OrderChannelModel:
        return await self.model.filter(game=game, category=category).first()


OrderChannelCRUD = CRUDOrderChannel(OrderChannelModel)
