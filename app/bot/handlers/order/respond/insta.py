from __future__ import annotations

import datetime

from aiogram import Router, F, types, exceptions
from aiogram.fsm.state import StatesGroup, State

from app import config
from app.bot import bot
from app.bot.cbdata import OrderRespondCallback
from app.schemas import OrderRespondExtra, OrderRespondCreate, Order, OrderMessageCreate, User, RenderConfig
from app.services.pull import PullService
from app.common.formats import format_err


router = Router()


class OrderRespond(StatesGroup):
    approved = State()


@router.callback_query(OrderRespondCallback.filter(F))
async def respond_order_button(call: types.CallbackQuery, callback_data: OrderRespondCallback):
    booster = await User.get_by_user_id(call.from_user.id)
    if not booster or not booster.is_verified:
        try:
            msg = format_err("121312")
            await bot.send_message(call.from_user.id, msg)
            await call.answer()
        except exceptions.TelegramBadRequest:
            me = await bot.get_me()
            await call.answer(url=f"https://t.me/{me.username}?start=Hello")
        return

    if await PullService.pull_respond_check(callback_data.order_id, booster.id):
        try:
            await bot.send_message(call.from_user.id, format_err("You have already responded to this order"))
        except exceptions.TelegramBadRequest:
            me = await bot.get_me()
            await call.answer(url=f"https://t.me/{me.username}?start=Hello")
        await call.answer()
        return

    order = await Order.get(callback_data.order_id)
    data = OrderRespondCreate(
        order_id=order.id,
        user_id=booster.id,
        channel_id_booster=0,
        message_id_booster=0,
        username=call.from_user.username,
        approved=False,
        strict=False,
        extra=OrderRespondExtra(eta=datetime.timedelta(seconds=callback_data.time)),
    )
    message_create = OrderMessageCreate(channel_id=config.app.admin_chat, order_id=order.id,
                                        config_names=RenderConfig.get_base_respond_names(order))
    await PullService.pull_respond(data, message_create)

    try:
        await bot.send_message(call.from_user.id, "Done! Order sent to admins")
    except exceptions.TelegramAPIError:
        me = await bot.get_me()
        await call.answer(url=f"https://t.me/{me.username}?start=Hello")

    await call.answer()
