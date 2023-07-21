from aiogram import types
from loguru import logger

from app.models.bot import bot


async def start(message: types.Message) -> None:
    me = await bot.me()
    url = f"https://t.me/{me.username}?start=Hello"
    await message.reply_html(text=url)
    logger.info(f"Started a conversation with a user {message.from_user.username} [ID: {message.from_user.id}]")
