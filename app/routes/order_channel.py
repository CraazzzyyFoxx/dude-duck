from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from starlette import status

from app.common.enums import RouteTag
from app.schemas import OrderChannelUpdate, OrderChannelCreate, OrderChannelID
from app.crud import OrderChannelCRUD
from app.services.auth import AuthService

router = APIRouter(
    prefix='/order/channel',
    tags=[RouteTag.ORDER_CHANNELS],
    dependencies=[Depends(AuthService.requires_authorization_admin)]
)


@router.get('/', response_model=list[OrderChannelID])
async def reads_order_channel(skip: int = 0, limit: int = 100):
    models = await OrderChannelCRUD.get_multi(skip=skip, limit=limit)

    return models


@router.get('/{item_id}', response_model=OrderChannelID)
async def read_order_channel(item_id: int):
    model = await OrderChannelCRUD.get(item_id)

    if not model:
        raise HTTPException(status_code=404, detail="Item not found")

    return model


@router.post('/', response_model=OrderChannelID)
async def create_order_channel(order: OrderChannelCreate):
    model = await OrderChannelCRUD.get_by_game_category(order.game, order.category)

    if model:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Item already exist")

    model = await OrderChannelCRUD.create(obj_in=order)
    return model


@router.delete('/', response_model=OrderChannelID)
async def delete_order_channel(item_id: int):
    model = await OrderChannelCRUD.get(item_id)

    if not model:
        raise HTTPException(status_code=404, detail="Item not found")

    return await OrderChannelCRUD.remove(id=model.id)


@router.put('/{item_id}', response_model=OrderChannelID)
async def update_order_channel(item_id: int, data: OrderChannelUpdate):
    model = await OrderChannelCRUD.get(item_id)

    if not model:
        raise HTTPException(status_code=404, detail="Item not found")

    return await OrderChannelCRUD.update(db_obj=model, obj_in=data)
