from aiogram import types, Router
from aiogram.filters import Command
from loguru import logger


from app.common.templates import render_template

router = Router()


@router.message(Command('start'))
async def start(message: types.Message) -> None:
    await message.answer(render_template("start.j2"))
    logger.info(f"Started a conversation with a user {message.from_user.username} [ID: {message.from_user.id}]")
