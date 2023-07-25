from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from starlette import status

from app.common.enums import RouteTag
from app.schemas import RenderConfigUpdate, RenderConfigCreate, RenderConfigID
from app.crud import OrderRenderCRUD
from app.services.auth import AuthService

router = APIRouter(
    prefix='/order/render',
    tags=[RouteTag.ORDER_RENDERS],
    dependencies=[Depends(AuthService.requires_authorization_admin)]
)


@router.get('/', response_model=list[RenderConfigID])
async def reads_order_render_template(skip: int = 0, limit: int = 100):
    return await OrderRenderCRUD.get_multi(skip=skip, limit=limit)


@router.get('/{item_id}', response_model=RenderConfigID)
async def read_order_render_template(item_id: int):
    model = await OrderRenderCRUD.get(item_id)

    if not model:
        raise HTTPException(status_code=404, detail="Order Render Template not found")

    return model


@router.post('/', response_model=RenderConfigID)
async def create_order_render_template(render_config: RenderConfigCreate):
    model = await OrderRenderCRUD.get_by_name(render_config.name)

    if model:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Order Render Template already exist")

    return await OrderRenderCRUD.create(obj_in=render_config)


@router.delete('/', response_model=RenderConfigID)
async def delete_order_render_template(item_id: int):
    model = await OrderRenderCRUD.get(item_id)

    if not model:
        raise HTTPException(status_code=404, detail="Order Render Template not found")

    return await OrderRenderCRUD.remove(id=model.id)


@router.put('/{item_id}', response_model=RenderConfigID)
async def update_order_render_template(item_id: int, data: RenderConfigUpdate):
    model = await OrderRenderCRUD.get(item_id)

    if not model:
        raise HTTPException(status_code=404, detail="Order Render Template not found")

    return await OrderRenderCRUD.update(db_obj=model, obj_in=data)
