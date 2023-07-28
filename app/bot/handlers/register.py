from aiogram import types, Router
from aiogram.filters import Command
from loguru import logger
from pydantic import ValidationError

from app.services.google import GoogleSheetsServiceManager
from app.schemas import User
from app.common import format_err, format_pydantic_err, render_template

router = Router()


@router.message(Command('register'))
async def register(message: types.Message):
    user = message.from_user
    booster = await User.get_by_user_id(user.id)
    if booster:
        return await message.answer("You have already applied for registration")

    msg = await message.answer("Fetching data... Please wait")
    try:
        mn = GoogleSheetsServiceManager.get()
        booster_sh = await mn.get_booster_by_cell(spreadsheet="Copy of B2B order", sheet_id=6585526817, value=user.username)
    except ValidationError as e:
        return await message.answer(format_err(format_pydantic_err(e)))
    if booster_sh is None:
        return await message.answer(render_template("error_register.j2"))

    data = BoosterCreate(user_id=user.id,
                         username=user.username,
                         name=booster_sh.name,
                         description=booster_sh.description,
                         rub=booster_sh.rub,
                         binance=booster_sh.binance,
                         gold=booster_sh.gold,
                         discord=booster_sh.discord
                         )

    await BoosterCRUD.create(obj_in=data)
    await msg.edit_text("\n".join([msg.text, render_template("register.j2")]))
    logger.info(f"Booster [username={user.username} id={user.id}] completed registration]")
