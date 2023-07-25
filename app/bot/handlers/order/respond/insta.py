from __future__ import annotations

import datetime

from aiogram import Router, F, types, exceptions
from aiogram.fsm.state import StatesGroup, State

from app.bot import bot
from app.bot.cbdata import OrderRespondCallback
from app.crud import OrderCRUD, OrderRenderCRUD, BoosterCRUD
from app.schemas import OrderRespondExtra, OrderRespondCreate, OrderID, OrderMessageCreate
from app.services.pull import PullService
from app.common.formats import format_error

import config

router = Router()


class OrderRespond(StatesGroup):
    approved = State()


@router.callback_query(OrderRespondCallback.filter(F))
async def respond_order_button(call: types.CallbackQuery, callback_data: OrderRespondCallback):
    call._bot = bot

    booster = await BoosterCRUD.get_by_user_id(call.from_user.id)
    if not booster or not booster.verified:
        try:
            msg = format_error("You have not been verified. Please send your Telegram tag and payment method to the manager at @Dudeduck or @thespacerat. Then message me /register")
            await bot.send_message(call.from_user.id, msg)
            await call.answer()
        except exceptions.TelegramAPIError:
            me = await bot.get_me()
            await call.answer(url=f"https://t.me/{me.username}?start=Hello")
        return

    if await PullService.pull_respond_check(callback_data.order_id, call.from_user.id):
        try:
            await bot.send_message(call.from_user.id, format_error("You have already responded to this order"))
        except exceptions.TelegramAPIError:
            me = await bot.get_me()
            await call.answer(url=f"https://t.me/{me.username}?start=Hello")
        await call.answer()
        return

    order = OrderID.model_validate(await OrderCRUD.get(callback_data.order_id), from_attributes=True)
    extra = OrderRespondExtra(eta=datetime.timedelta(seconds=callback_data.time))
    data = OrderRespondCreate(
        order_id=callback_data.order_id,
        user_id=call.from_user.id,
        channel_id_booster=0,
        message_id_booster=0,
        username=call.from_user.username,
        approved=False,
        strict=False,
        extra=extra,
    )
    message_create = OrderMessageCreate(channel_id=config.app.admin_chat, order_id=order.id,
                                        config_names=OrderRenderCRUD.get_base_respond_names(order))
    await PullService.pull_respond(data, message_create)

    try:
        if await PullService.pull_respond_check(callback_data.order_id, call.from_user.id):
            await bot.send_message(call.from_user.id, "Done! Order sent to admins")
    except exceptions.TelegramAPIError:
        me = await bot.get_me()
        await call.answer(url=f"https://t.me/{me.username}?start=Hello")

    await call.answer()
