from pydantic import BaseModel


__all__ = ("SheetsOrder", "SheetsBooster")


class SheetsOrder(BaseModel):
    spreadsheet: str
    sheet_id: int
    game: str
    row: int


class SheetsBooster(BaseModel):
    spreadsheet: str
    sheet_id: int
    name: str
