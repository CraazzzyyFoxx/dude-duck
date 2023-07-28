from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from starlette import status

from app.common.enums import RouteTag
from app.schemas import Order, User, SheetEntity
from app.services.auth import current_active_superuser
from app.services.google import GoogleSheetsServiceManager

router = APIRouter(
    prefix='/sheets/getters',
    tags=[RouteTag.SHEET],
)


# @router.post('/order-move', status_code=status.HTTP_200_OK, response_model=Order)
# async def sheets_order_move(order: SheetEntity, user: User = Depends(current_active_superuser)):
#     if not user.google:
#         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Google Service account don't setup")
#
#     model_pyd = await GoogleSheetsServiceManager.get(user=user).get_order(
#         order.spreadsheet,
#         order.sheet_id,
#         order.row,
#         apply_model=False
#     )
#
#     model = await GoogleSheetsServiceManager.get(user=user).create_order("M+", 0, model_pyd)
#     return await model.create()


@router.post('/order', status_code=status.HTTP_200_OK, response_model=Order)
async def sheets_create_order(order: SheetEntity, user: User = Depends(current_active_superuser)):
    if not user.google:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Google Service account don't setup")

    model = await GoogleSheetsServiceManager.get(user=user).get_order(
        order.spreadsheet,
        order.sheet_id,
        order.row_id
    )

    if await Order.get_by_order_id(model.order_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Order already exist")

    return await model.create()


@router.put('/order', status_code=status.HTTP_200_OK, response_model=Order)
async def sheets_update_order(data: SheetEntity, user: User = Depends(current_active_superuser)):
    model = await GoogleSheetsServiceManager.get(user=user).get_order(
        data.spreadsheet,
        data.sheet_id,
        data.row
    )
    order = await Order.get_by_order_id(model.order_id)
    if not order:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Order not found")

    order.update_from(model)
    await order.save()
    return order
