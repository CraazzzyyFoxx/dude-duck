from pydantic import BaseModel
from beanie import Document, Indexed

__all__ = ("SheetEntityBase", "SheetEntity", "SheetEntityDB", "UpdateInterface")


class UpdateInterface(BaseModel):
    def update_from(self, model: BaseModel):
        update_data = model.model_dump(exclude_unset=True)
        model_fields = [field[0] for field in self.model_fields.items()]
        for name, value in update_data.items():
            if name in model_fields and value is not None:
                setattr(self, name, value)


class SheetEntityBase(BaseModel):
    spreadsheet: str | None = None
    sheet_id: int | None = None
    row_id: int | None = None


class SheetEntity(BaseModel):
    spreadsheet: str
    sheet_id: int
    row_id: int


class SheetEntityDB(Document, SheetEntity):
    spreadsheet: Indexed(str)
    sheet_id: Indexed(int)
    row_id: int
