from __future__ import annotations

from aiogram import types
from fastapi import APIRouter, Depends

from starlette import status
from app.bot import bot, dp


router = APIRouter(
    prefix='/telegram',
    tags=['telegram'],
    #dependencies=[Depends(AuthService.requires_authorization_telegram)]
)


@router.post("/webhook", status_code=status.HTTP_200_OK)
async def telegram(update: dict):
    # await application.update_queue.put(
    #     Update.de_json(data=payload, bot=application.bot)
    # )
    # return Response()
    telegram_update = types.Update(**update)
    await dp.feed_update(bot=bot, update=telegram_update)
