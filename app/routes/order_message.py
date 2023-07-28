from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from starlette import status

from app.common.enums import RouteTag
from app.schemas import OrderMessageUpdate, OrderMessageCreate, OrderMessage, Order
from app.services.auth import current_active_superuser
from app.services.pull import PullService

router = APIRouter(
    prefix='/order/message',
    tags=[RouteTag.ORDER_MESSAGES],
    dependencies=[Depends(current_active_superuser)]
)


@router.get('/', response_model=list[OrderMessage])
async def reads_order_message(skip: int = 0, limit: int = 100):
    return await OrderMessage.find({}).skip(skip).limit(limit).to_list()


@router.get('/{item_id}', response_model=OrderMessage)
async def read_order_message(item_id: int):
    model = await OrderMessage.get(item_id)

    if not model:
        raise HTTPException(status_code=404, detail="Message not found")

    return model


@router.post('/', response_model=list[OrderMessage])
async def create_order_message(data: OrderMessageCreate):
    order = await Order.get_by_order_id(data.order_id)

    if not order:
        raise HTTPException(status_code=404, detail="Item not found")

    messages = await PullService.pull_create(order, data)

    if not messages:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Message already exist")

    return messages


@router.delete('/', response_model=OrderMessage)
async def delete_order_message(item_id: int):
    model = await OrderMessage.get(item_id)

    if not model:
        raise HTTPException(status_code=404, detail="Message not found")

    return await OrderMessage.remove(id=model.id)


@router.put('/{order_id}', response_model=list[OrderMessage])
async def update_order_message(order_id: str, data: OrderMessageUpdate):
    model = await Order.get_by_order_id(order_id)

    if not model:
        raise HTTPException(status_code=404, detail="Message not found")

    messages = await PullService.pull_edit(model, data)

    if not messages:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Message already exist")

    return messages
