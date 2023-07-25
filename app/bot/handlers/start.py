from aiogram import types, Router, Bot
from aiogram.filters import Command
from loguru import logger

import config

router = Router()


@router.message(Command('start'))
async def start(message: types.Message, bot: Bot) -> None:
    message._bot = bot
    await message.answer(config.START_MESSAGE)
    logger.info(f"Started a conversation with a user {message.from_user.username} [ID: {message.from_user.id}]")
