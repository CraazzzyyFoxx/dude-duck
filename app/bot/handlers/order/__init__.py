from aiogram import Router

from app.bot.handlers.order import respond
from app.bot.handlers.order import close
from app.bot.handlers.order.respond import message
from app.bot.handlers.order.respond import insta

router = Router()
# router.include_router(router=respond.router)
router.include_router(router=close.router)
router.include_router(router=insta.router)
# router.include_router(router=message.router)
