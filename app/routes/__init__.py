from fastapi import APIRouter

from . import (
    # orders,
    telegram,
    # parse_sheet,
    # order_channel,
    # order_message,
    # order_render,

)

router = APIRouter(prefix="/api")


@router.get("/")
async def main():
    return {"message": "Hello World"}

# router.include_router(orders.router)
router.include_router(telegram.router)
# router.include_router(parse_sheet.router)
# router.include_router(order_channel.router)
# router.include_router(order_message.router)
# router.include_router(order_render.router)
# router.include_router(users.router)