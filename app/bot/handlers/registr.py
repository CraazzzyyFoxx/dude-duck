from aiogram import types, Router, Bot
from aiogram.filters import Command
from loguru import logger
from pydantic import ValidationError

from app.common.formats import format_error, format_pydantic_error
from app.services.google import GoogleSheetsServiceManager
from app.crud import BoosterCRUD
from app.schemas import BoosterCreate

router = Router()


@router.message(Command('registr'))
async def start(message: types.Message, bot: Bot):
    message._bot = bot
    user = message.from_user
    booster = await BoosterCRUD.get_by_username(user.username)
    if booster:
        await message.answer("You have already applied for registration")
    try:
        booster_sheets = await GoogleSheetsServiceManager.get().get_booster_by_cell(spreadsheet="M+",
                                                                                    sheet_id=673034649,
                                                                                    value=user.username)
    except ValidationError as e:
        return await message.answer(format_error(format_pydantic_error(e)))

    if booster_sheets is None:
        await message.answer("I can't find your details, write to @dude_duck or @thespacerat for more info")
        return

    data = BoosterCreate(user_id=user.id,
                         username=user.username,
                         name=booster_sheets.name,
                         description=booster_sheets.description,
                         rub=booster_sheets.rub,
                         binance=booster_sheets.binance,
                         gold=booster_sheets.gold,
                         discord=booster_sheets.discord
                         )

    await BoosterCRUD.create(obj_in=data)
    await message.answer("Registration was successful and you can now take orders ")
