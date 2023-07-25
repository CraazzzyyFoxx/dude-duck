from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from loguru import logger
from starlette import status

from app.common.enums import RouteTag
from app.schemas import AdminID, AdminCreate, AdminUpdate
from app.services.auth import AuthService
from app.crud import AdminCRUD


router = APIRouter(
    prefix='/admin',
    tags=[RouteTag.BOOSTERS],
    dependencies=[Depends(AuthService.requires_authorization)]
)


@router.get('/', status_code=status.HTTP_200_OK, response_model=list[AdminID])
async def reads_admin(skip: int = 0, limit: int = 100):
    models = await AdminCRUD.get_multi(skip=skip, limit=limit)
    return models


@router.get('/{admin_id}', status_code=status.HTTP_200_OK, response_model=AdminID)
async def read_admin(admin_id: int):
    model = await AdminCRUD.get(admin_id)

    if not model:
        raise HTTPException(status_code=404, detail="Order not found")

    return model


@router.post('/', status_code=status.HTTP_200_OK)
async def create_admin(order: AdminCreate):
    admin = await AuthService.registrate(order)
    return admin


# @router.delete('/', response_model=AdminID)
# async def delete_admin(order_id: int):
#     model = await OrderCRUD.get(order_id)
#
#     if not model:
#         raise HTTPException(status_code=404, detail="Order not found")
#
#     return await OrderCRUD.remove(id=model.id)


# @router.put('/{admin_id}', response_model=AdminID)
# async def update_admin(admin_id: int, data: AdminUpdate):
#     model = await OrderCRUD.get(admin_id)
#
#     if not model:
#         raise HTTPException(status_code=404, detail="Item not found")
#
#     return await OrderCRUD.update(db_obj=model, obj_in=data)
