from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

import config
from app.bot.handlers.start import start_router
from app.bot.middlewares.config import ConfigMiddleware

storage = MemoryStorage()
bot = Bot(token=config.app.TOKEN, parse_mode="HTML")
dp = Dispatcher(storage=storage)
