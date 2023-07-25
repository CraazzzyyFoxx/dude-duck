from datetime import datetime

from aiogram import types, Router, Bot
from aiogram.filters import Command, CommandObject
from pydantic import BaseModel, HttpUrl, field_validator, ValidationError, Field

from app.common.formats import format_error, format_pydantic_error
from app.services.google import GoogleSheetsServiceManager
from app.crud import BoosterCRUD, OrderCRUD
from app.schemas import OrderBase

router = Router()


class Validation(BaseModel):
    order_id: int | str
    url: HttpUrl
    payment: str = Field(min_length=1)

    @field_validator("order_id", mode="before")
    def parse_order_id(cls, v: str):
        try:
            x = int(v)
        except ValueError:
            raise ValueError("value must be integer")
        return x


@router.message(Command('close'))
async def start(message: types.Message, command: CommandObject, bot: Bot):
    message._bot = bot

    user = message.from_user
    booster = await BoosterCRUD.get_by_username(user.username)
    if not booster or not booster.verified:
        return await message.answer(
            format_error("You can't close orders because there is no verification or registration."))

    if not command.args:
        return await message.answer(format_error("The information should be of the type: \n"
                                                 "<b>300 - https://imgur.com/LTj5W8x - $</b>"),
                                    disable_web_page_preview=True)

    args = command.args.split("-")

    if len(args) != 3:
        return await message.answer(format_error("The information should be of the type: \n"
                                                 "<b>300 - https://imgur.com/LTj5W8x - $</b>"),
                                    disable_web_page_preview=True)
    try:
        data = Validation(order_id=args[0].strip(),
                          url=args[1].strip(),
                          payment=args[2].strip())
    except ValidationError as e:
        return await message.answer(format_error(format_pydantic_error(e)))

    model = await OrderCRUD.get_by_game(data.order_id, "DF")

    if not model:
        return await message.answer(format_error("Order not found"))
    if model.booster != booster.name:
        return await message.answer(format_error("You can only close your orders"))
    if model.status == "Completed":
        return await message.answer(format_error("The order is already closed"))
    now = datetime.utcnow()
    now = datetime(year=now.year, month=now.month, day=now.day)
    await message.answer("Processing... Please wait")
    d = OrderBase(screenshot=data.url, method_payment=data.payment, status="Completed", end_date=now)
    await GoogleSheetsServiceManager.get().update_order("M+", 0, data.order_id, d)
    await OrderCRUD.update(db_obj=model, obj_in=d)

    return await message.answer("Order successfully closed")
