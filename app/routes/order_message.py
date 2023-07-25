from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from starlette import status

from app.common.enums import RouteTag
from app.schemas import OrderMessageUpdate, OrderMessageCreate, OrderMessageID, OrderID
from app.crud import OrderCRUD, OrderMessageCRUD
from app.services.auth import AuthService
from app.services.pull import PullService

router = APIRouter(
    prefix='/order/message',
    tags=[RouteTag.ORDER_MESSAGES],
    dependencies=[Depends(AuthService.requires_authorization_admin)]
)


@router.get('/', response_model=list[OrderMessageID])
async def reads_order_message(skip: int = 0, limit: int = 100):
    models = await OrderMessageCRUD.get_multi(skip=skip, limit=limit)

    return models


@router.get('/{item_id}', response_model=OrderMessageID)
async def read_order_message(item_id: int):
    model = await OrderMessageCRUD.get_by_order_id(item_id)

    if not model:
        raise HTTPException(status_code=404, detail="Item not found")

    return model


@router.post('/', response_model=list[OrderMessageID])
async def create_order_message(data: OrderMessageCreate):
    order = await OrderCRUD.get_by_game(data.order_id, "DF")

    if not order:
        raise HTTPException(status_code=404, detail="Item not found")

    messages = await PullService.pull_create(OrderID.model_validate(order, from_attributes=True), data)

    if not messages:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Item already exist")

    return messages


@router.delete('/', response_model=OrderMessageID)
async def delete_order_message(item_id: int):
    model = await OrderMessageCRUD.get(item_id)

    if not model:
        raise HTTPException(status_code=404, detail="Item not found")

    return await OrderMessageCRUD.remove(id=model.id)


@router.put('/{order_id}', response_model=list[OrderMessageID])
async def update_order_message(order_id: int, data: OrderMessageUpdate):
    model = await OrderCRUD.get_by_game(order_id, "DF")

    if not model:
        raise HTTPException(status_code=404, detail="Item not found")

    messages = await PullService.pull_edit(OrderID.model_validate(model, from_attributes=True), data)

    if not messages:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Item already exist")

    return messages
