from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from starlette import status

from app.common.enums import RouteTag
from app.schemas import OrderID, SheetsOrder, AdminID
from app.services.auth import AuthService
from app.services.google import GoogleSheetsServiceManager
from app.crud import OrderCRUD

router = APIRouter(
    prefix='/sheets',
    tags=[RouteTag.SHEET],
    dependencies=[Depends(AuthService.requires_authorization_admin)]
)


@router.post('/order-move', status_code=status.HTTP_200_OK, response_model=OrderID)
async def sheets_order_move(order: SheetsOrder, admin: AdminID = Depends(AuthService.requires_authorization_admin)):
    model_pyd = await GoogleSheetsServiceManager.get(admin=admin).get_order(
        order.spreadsheet,
        order.sheet_id,
        order.row,
        apply_model=False
    )

    model = await GoogleSheetsServiceManager.get(admin=admin).create_order("M+", 0, model_pyd)
    return await OrderCRUD.create(obj_in=model)


@router.post('/order', status_code=status.HTTP_200_OK, response_model=OrderID)
async def sheets_create_order(order: SheetsOrder, admin: AdminID = Depends(AuthService.requires_authorization_admin)):
    model = await OrderCRUD.get_by_game(order.row, order.game)

    if not model:
        model_pyd = await GoogleSheetsServiceManager.get(admin=admin).get_order(
            order.spreadsheet,
            order.sheet_id,
            order.row
        )
        model = await OrderCRUD.create(obj_in=model_pyd)
        return model

    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Order already exist")


@router.put('/order', status_code=status.HTTP_200_OK, response_model=OrderID)
async def sheets_update_order(order: SheetsOrder, admin: AdminID = Depends(AuthService.requires_authorization_admin)):
    model = await OrderCRUD.get_by_game(order.row, order.game)

    if not model:
        model_pyd = await GoogleSheetsServiceManager.get(admin=admin).get_order(
            order.spreadsheet,
            order.sheet_id,
            order.row
        )
        await OrderCRUD.update(db_obj=model, obj_in=model_pyd)
        return await OrderCRUD.get_by_game(order.row, order.game)

    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Order not found")
