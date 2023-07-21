from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from loguru import logger
from starlette import status

from app.schemas import OrderSheetParseID, OrderSheetParseCreate, OrderSheetParseUpdate
from app.crud import OrderSheetsCRUD
from app.services.auth import AuthService

router = APIRouter(
    prefix='/sheets',
    tags=['Sheets'],
    dependencies=[Depends(AuthService.requires_authorization)]
)


@router.get('/', response_model=list[OrderSheetParseID])
async def read_parse(skip: int = 0, limit: int = 100):
    models = await OrderSheetsCRUD.get_multi(skip=skip, limit=limit)

    return models


@router.get('/{item_id}', response_model=OrderSheetParseID)
async def read_parse(item_id: int):
    model = await OrderSheetsCRUD.get(item_id)

    if not model:
        raise HTTPException(status_code=404, detail="Item not found")

    return OrderSheetParseID.model_validate(model, from_attributes=True)


@router.post('/', response_model=OrderSheetParseID)
async def create_parse(order: OrderSheetParseCreate):
    model = await OrderSheetsCRUD.get_by_spreadsheet(order.spreadsheet, order.sheet_id)

    if model:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Item already exist")

    model = await OrderSheetsCRUD.create(obj_in=order)
    return model


@router.delete('/', response_model=OrderSheetParseID)
async def delete_parse(item_id: int):
    model = await OrderSheetsCRUD.get(item_id)

    if not model:
        raise HTTPException(status_code=404, detail="Item not found")

    return await OrderSheetsCRUD.remove(id=model.id)


@router.put('/{item_id}', response_model=OrderSheetParseID)
async def update_parse(item_id: int, data: OrderSheetParseUpdate):
    model = await OrderSheetsCRUD.get(item_id)

    if not model:
        raise HTTPException(status_code=404, detail="Item not found")

    return await OrderSheetsCRUD.update(db_obj=model, obj_in=data)
