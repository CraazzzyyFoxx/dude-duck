from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from starlette import status

from app.common.enums import RouteTag
from app.schemas import OrderChannelUpdate, OrderChannelCreate, OrderChannel
from app.services.auth import current_active_superuser

router = APIRouter(
    prefix='/order/channel',
    tags=[RouteTag.ORDER_CHANNELS],
    dependencies=[Depends(current_active_superuser)]
)


@router.get('/', response_model=list[OrderChannel])
async def reads_order_channel(skip: int = 0, limit: int = 100):
    models = await OrderChannel.find({}).skip(skip).limit(limit).to_list()

    return models


@router.get('/{item_id}', response_model=OrderChannel)
async def read_order_channel(item_id: int):
    model = await OrderChannel.get(item_id)

    if not model:
        raise HTTPException(status_code=404, detail="Item not found")

    return model


@router.post('/', response_model=OrderChannel)
async def create_order_channel(channel: OrderChannelCreate):
    if await OrderChannel.get_by_game_category(channel.game, channel.category):
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Item already exist")

    return await channel.create()


@router.delete('/', response_model=OrderChannel)
async def delete_order_channel(item_id: int):
    model = await OrderChannel.get(item_id)

    if not model:
        raise HTTPException(status_code=404, detail="Item not found")

    return await model.delete()


@router.put('/{item_id}', response_model=OrderChannel)
async def update_order_channel(item_id: int, data: OrderChannelUpdate):
    model = await OrderChannel.get(item_id)

    if not model:
        raise HTTPException(status_code=404, detail="Item not found")
    model.update_from(data)
    await model.update()
    return model
