from datetime import datetime

from aiogram import types, Router, Bot
from aiogram.filters import Command, CommandObject
from pydantic import BaseModel, HttpUrl, field_validator, ValidationError, Field

from app import config
from app.common import format_err, format_pydantic_err, render_template
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
    booster = await BoosterCRUD.get_by_username(message.from_user.username)
    if not booster or not booster.verified:
        return await message.answer(format_err(render_template("no_verify.j2")))
    if not command.args:
        return await message.answer(format_err(render_template("error_close_order.j2")), disable_web_page_preview=True)
    args = command.args.split("-")
    if len(args) != 3:
        return await message.answer(format_err(render_template("error_close_order.j2")), disable_web_page_preview=True)
    try:
        data = Validation(order_id=args[0].strip(), url=args[1].strip(), payment=args[2].strip())
    except ValidationError as e:
        return await message.answer(format_err(format_pydantic_err(e)))

    model = await OrderCRUD.get_by_order_id(data.order_id)

    if not model:
        return await message.answer(format_err("Order not found"))
    if model.booster != booster.name:
        return await message.answer(format_err("You can close only your orders"))
    if model.status == "Completed":
        return await message.answer(format_err("The order is already closed"))
    now = datetime.utcnow()
    now = datetime(year=now.year, month=now.month, day=now.day)
    msg = await message.answer("Processing... Please wait")
    d = OrderBase(screenshot=data.url, method_payment=data.payment, status="Completed", end_date=now)
    await GoogleSheetsServiceManager.get().update_order("M+", 0, data.order_id, d)
    await OrderCRUD.update(db_obj=model, obj_in=d)
    await bot.send_message(config.app.admin_chat, render_template("close_order_admin.j2", {"order": model}))
    return await msg.edit_text('\n'.join([msg.text, "Order successfully closed"]))
