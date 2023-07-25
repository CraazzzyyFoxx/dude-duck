from aiogram import Router

from app.bot.handlers import start
from app.bot.handlers import order
from app.bot.handlers import registr
from app.bot.handlers import close_order

router = Router()
router.include_router(router=start.router)
router.include_router(router=order.router)
router.include_router(router=registr.router)
router.include_router(router=close_order.router)
