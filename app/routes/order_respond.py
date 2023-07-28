from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from app.common.enums import RouteTag
from app.schemas import OrderRespondID
from app.crud import OrderRespondCRUD
from app.services.auth import current_active_superuser

router = APIRouter(
    prefix='/order/respond',
    tags=[RouteTag.ORDER_RESPOND],
    dependencies=[Depends(current_active_superuser)]
)


@router.get('/', response_model=list[OrderRespondID])
async def reads_order_response(skip: int = 0, limit: int = 100):
    return await OrderRespondCRUD.get_multi(skip=skip, limit=limit)


@router.get('/{item_id}', response_model=OrderRespondID)
async def read_order_response(item_id: int):
    model = await OrderRespondCRUD.get(item_id)

    if not model:
        raise HTTPException(status_code=404, detail="Order Respond not found")

    return model


@router.delete('/', response_model=OrderRespondID)
async def delete_order_response(item_id: int):
    model = await OrderRespondCRUD.get(item_id)

    if not model:
        raise HTTPException(status_code=404, detail="Order Respond not found")

    return await OrderRespondCRUD.remove(id=model.id)
