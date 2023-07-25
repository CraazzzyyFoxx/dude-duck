from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from starlette import status

from app.common.enums import RouteTag
from app.schemas import OrderID, OrderCreate, OrderUpdate
from app.services.auth import AuthService
from app.crud import OrderCRUD


router = APIRouter(
    prefix='/booster',
    tags=[RouteTag.BOOSTERS],
    dependencies=[Depends(AuthService.requires_authorization_admin)]
)


@router.get('/', status_code=status.HTTP_200_OK, response_model=list[OrderID])
async def reads_booster(skip: int = 0, limit: int = 100):
    models = await OrderCRUD.get_multi(skip=skip, limit=limit)
    return models


@router.get('/{booster_id}', status_code=status.HTTP_200_OK, response_model=OrderID)
async def read_booster(booster_id: int):
    model = await OrderCRUD.get(booster_id)

    if not model:
        raise HTTPException(status_code=404, detail="Order not found")

    return model


@router.post('/', status_code=status.HTTP_200_OK)
async def create_booster(order: OrderCreate):
    model = await OrderCRUD.get_by_spreadsheet(order.spreadsheet, order.sheet_id)

    if model:
       raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Order already exist")

    model = await OrderCRUD.create(obj_in=order)
    return model


@router.delete('/', response_model=OrderID)
async def delete_booster(order_id: int):
    model = await OrderCRUD.get(order_id)

    if not model:
        raise HTTPException(status_code=404, detail="Order not found")

    return await OrderCRUD.remove(id=model.id)


@router.put('/{booster_id}', response_model=OrderID)
async def update_booster(booster_id: int, data: OrderUpdate):
    model = await OrderCRUD.get(booster_id)

    if not model:
        raise HTTPException(status_code=404, detail="Item not found")

    return await OrderCRUD.update(db_obj=model, obj_in=data)
