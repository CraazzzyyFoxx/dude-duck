from fastapi import APIRouter

from . import (
    orders,
    parse_sheet,
    order_channel,
    order_message,
    order_render,
    sheets,
    booster,
    admin,
order_respond

)

router = APIRouter(prefix="/api")

router.include_router(orders.router)
router.include_router(parse_sheet.router)
router.include_router(order_channel.router)
router.include_router(order_message.router)
router.include_router(order_render.router)
router.include_router(sheets.router)
# router.include_router(booster.router)
router.include_router(admin.router)
router.include_router(order_respond.router)
