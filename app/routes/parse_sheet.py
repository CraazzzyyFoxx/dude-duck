from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from starlette import status

from app.common.enums import RouteTag
from app.schemas import OrderSheetParse, OrderSheetParseCreate, OrderSheetParseUpdate
from app.services.auth import current_active_superuser

router = APIRouter(
    prefix='/sheets/parsers',
    tags=[RouteTag.SHEETS_PARSERS],
    dependencies=[Depends(current_active_superuser)]
)


@router.get('/', response_model=list[OrderSheetParse])
async def reads_google_sheets_parser(skip: int = 0, limit: int = 100):
    models = await OrderSheetParse.find({}).skip(skip).limit(limit).to_list()

    return models


@router.get('/{spreadsheet}/{sheet_id}', response_model=OrderSheetParse)
async def read_google_sheets_parser(spreadsheet: str, sheet_id: int):
    model = await OrderSheetParse.get_spreadsheet_sheet(spreadsheet, sheet_id)

    if not model:
        raise HTTPException(status_code=404, detail="Google Sheets Parser not found")

    return model


@router.post('/', response_model=OrderSheetParse)
async def create_google_sheets_parser(model: OrderSheetParseCreate):
    data = await OrderSheetParse.get_spreadsheet_sheet(model.spreadsheet, model.sheet_id)

    if data:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Google Sheets Parser already exist")

    return await model.create()


@router.delete('/{spreadsheet}/{sheet_id}', response_model=OrderSheetParse)
async def delete_google_sheets_parser(spreadsheet: str, sheet_id: int):
    model = await OrderSheetParse.get_spreadsheet_sheet(spreadsheet, sheet_id)

    if not model:
        raise HTTPException(status_code=404, detail="Google Sheets Parser not found")
    await model.delete()
    return model


@router.put('/', response_model=OrderSheetParse)
async def update_google_sheets_parser(data: OrderSheetParseUpdate):
    model = await OrderSheetParse.get_spreadsheet_sheet(data.spreadsheet, data.sheet_id)

    if not model:
        raise HTTPException(status_code=404, detail="Google Sheets Parser not found")
    model.update_from(data)
    await model.update()
    return model
