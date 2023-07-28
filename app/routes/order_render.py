from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from starlette import status

from app.common.enums import RouteTag
from app.schemas import RenderConfigUpdate, RenderConfigCreate, RenderConfig
from app.services.auth import current_active_superuser

router = APIRouter(
    prefix='/order/render',
    tags=[RouteTag.ORDER_RENDERS],
    dependencies=[Depends(current_active_superuser)]
)


@router.get('/', response_model=list[RenderConfig])
async def reads_order_render_template(skip: int = 0, limit: int = 100):
    return await RenderConfig.find({}).skip(skip).limit(limit).to_list()


@router.get('/{item_id}', response_model=RenderConfig)
async def read_order_render_template(item_id: int):
    model = await RenderConfig.get(item_id)

    if not model:
        raise HTTPException(status_code=404, detail="Order Render Template not found")

    return model


@router.post('/', response_model=RenderConfig)
async def create_order_render_template(render_config: RenderConfigCreate):
    model = await RenderConfig.get_by_name(render_config.name)

    if model:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Order Render Template already exist")

    return await render_config.create()


@router.delete('/{name}', response_model=RenderConfig)
async def delete_order_render_template(name: str):
    model = await RenderConfig.get_by_name(name)

    if not model:
        raise HTTPException(status_code=404, detail="Order Render Template not found")

    await model.delete()
    return model


@router.put('/{name}', response_model=RenderConfig)
async def update_order_render_template(name: str, data: RenderConfigUpdate):
    model = await RenderConfig.get_by_name(name)

    if not model:
        raise HTTPException(status_code=404, detail="Order Render Template not found")

    model.update_from(data)
    await model.save()
    return model
