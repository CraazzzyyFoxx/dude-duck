from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from loguru import logger
from starlette import status

from app.schemas import OrderMessageUpdate, OrderMessageCreate, OrderMessageID, OrderID
from app.crud import OrderCRUD, OrderMessageCRUD
from app.services.auth import AuthService
from app.services.pull import PullService

router = APIRouter(
    prefix='/order/message',
    tags=['Order Message'],
    dependencies=[Depends(AuthService.requires_authorization)]
)


@router.get('/', response_model=list[OrderMessageID])
async def read_order_message(skip: int = 0, limit: int = 100):
    models = await OrderMessageCRUD.get_multi(skip=skip, limit=limit)

    return models


@router.get('/{item_id}', response_model=OrderMessageID)
async def read_order_message(item_id: int):
    model = await OrderMessageCRUD.get(item_id)

    if not model:
        raise HTTPException(status_code=404, detail="Item not found")

    return model


@router.post('/', response_model=list[OrderMessageID])
async def create_order_message(data: OrderMessageCreate):
    order = await OrderCRUD.get(data.order_id)

    if not order:
        raise HTTPException(status_code=404, detail="Item not found")

    messages = await PullService.pull_order(OrderID.model_validate(order, from_attributes=True), data)

    if not messages:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Item already exist")

    return messages


@router.delete('/', response_model=OrderMessageID)
async def delete_order_message(item_id: int):
    model = await OrderMessageCRUD.get(item_id)

    if not model:
        raise HTTPException(status_code=404, detail="Item not found")

    return await OrderMessageCRUD.remove(id=model.id)


@router.put('/{item_id}', response_model=OrderMessageID)
async def update_order_message(item_id: int, data: OrderMessageUpdate):
    model = await OrderMessageCRUD.get(item_id)

    if not model:
        raise HTTPException(status_code=404, detail="Item not found")

    return await OrderMessageCRUD.update(db_obj=model, obj_in=data)
