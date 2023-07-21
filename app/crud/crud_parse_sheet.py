from app.crud.base import CRUDBase
from app.db import OrderSheetParseModel
from app.schemas import OrderSheetParseUpdate, OrderSheetParseCreate


class CRUDOrderSheets(CRUDBase[OrderSheetParseModel, OrderSheetParseCreate, OrderSheetParseUpdate]):
    async def get_by_spreadsheet(self, spreadsheet: str, sheet_id: int) -> OrderSheetParseModel:
        return await self.model.filter(spreadsheet=spreadsheet, sheet_id=sheet_id).first()


OrderSheetsCRUD = CRUDOrderSheets(OrderSheetParseModel)
