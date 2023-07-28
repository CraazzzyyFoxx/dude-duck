from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from app import config

storage = MemoryStorage()
bot = Bot(token=config.app.bot_token, parse_mode="HTML")
dp = Dispatcher(storage=storage)
