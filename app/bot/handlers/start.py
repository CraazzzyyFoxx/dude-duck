from aiogram import types, Router
from aiogram.filters import Command
from loguru import logger

import config

start_router = Router()


@start_router.message(Command('start'))
async def start(message: types.Message) -> None:
    await message.answer(config.START_MESSAGE)
    logger.info(f"Started a conversation with a user {message.from_user.username} [ID: {message.from_user.id}]")
