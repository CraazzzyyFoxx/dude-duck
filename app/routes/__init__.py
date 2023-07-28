from fastapi import APIRouter

from . import (
    # orders,
    parse_sheet,
    order_channel,
    order_message,
    order_render,
    sheets,
    # booster,
    # admin,
    # order_respond

)
from app.common import RouteTag
from app.schemas import UserRead, UserCreate, UserUpdate
from app.services.auth import auth_backend, fastapi_users

router = APIRouter()
auth_router = APIRouter(prefix="/auth", tags=[RouteTag.AUTH])
api_router = APIRouter(prefix="/api")

# router.include_router(orders.router)
api_router.include_router(parse_sheet.router)
api_router.include_router(order_channel.router)
api_router.include_router(order_message.router)
api_router.include_router(order_render.router)
api_router.include_router(sheets.router)
# router.include_router(booster.router)
# router.include_router(admin.router)
# router.include_router(order_respond.router)


auth_router.include_router(fastapi_users.get_auth_router(auth_backend))
auth_router.include_router(fastapi_users.get_register_router(UserRead, UserCreate))
auth_router.include_router(fastapi_users.get_reset_password_router())
auth_router.include_router(fastapi_users.get_verify_router(UserRead))
auth_router.include_router(fastapi_users.get_users_router(UserRead, UserUpdate))

router.include_router(api_router)
router.include_router(auth_router)
