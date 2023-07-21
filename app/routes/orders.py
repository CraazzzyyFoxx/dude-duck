from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from loguru import logger
from starlette import status

from app.schemas import OrderID, OrderTelegram, OrderCreate, OrderUpdate
from app.services.auth import AuthService
from app.services.google import GoogleSheetsService
from app.crud import OrderCRUD

router = APIRouter(
    prefix='/order',
    tags=['order'],
    dependencies=[Depends(AuthService.requires_authorization)]
)


@router.get('/', status_code=status.HTTP_200_OK, response_model=list[OrderID])
async def reads_order(skip: int = 0, limit: int = 100):
    models = await OrderCRUD.get_multi(skip=skip, limit=limit)
    return models


@router.get('/{order_id}', status_code=status.HTTP_200_OK, response_model=OrderID)
async def read_order(order_id: int):
    model = await OrderCRUD.get(order_id)

    if not model:
        raise HTTPException(status_code=404, detail="Order not found")

    return model


@router.post('/', status_code=status.HTTP_200_OK)
async def create_order(order: OrderCreate):
    model = await OrderCRUD.get_by_spreadsheet(order.spreadsheet, order.sheet_id)

    if model:
       raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Order already exist")

    model = await OrderCRUD.create(obj_in=order)
    return model


@router.delete('/', response_model=OrderID)
async def delete_parse(order_id: int):
    model = await OrderCRUD.get(order_id)

    if not model:
        raise HTTPException(status_code=404, detail="Order not found")

    return await OrderCRUD.remove(id=model.id)


@router.put('/{order_id}', response_model=OrderID)
async def update_parse(order_id: int, data: OrderUpdate):
    model = await OrderCRUD.get(order_id)

    if not model:
        raise HTTPException(status_code=404, detail="Item not found")

    return await OrderCRUD.update(db_obj=model, obj_in=data)


@router.post('/sheets', status_code=status.HTTP_200_OK, response_model=OrderID)
async def telegram_order(order: OrderTelegram):
    model = await OrderCRUD.get_by_game(order.row, order.game)

    if not model:
        model_pyd = await GoogleSheetsService.get_order(order.spreadsheet, order.sheet_id, order.row)
        model = await OrderCRUD.create(obj_in=model_pyd)
        return model

    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Order already exist")

    # logger.info(f"Received order [{order_model.id}], sent to channels [{order.tg_channels}]")
