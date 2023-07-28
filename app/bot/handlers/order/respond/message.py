from __future__ import annotations

from typing import cast

from aiogram import Router, F, types, exceptions
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message
from loguru import logger

from app import config
from app.bot import bot
from app.bot.cbdata import OrderRespondYesNoCallback
from app.crud import OrderCRUD, OrderRenderCRUD
from app.schemas import OrderRespondExtra, OrderRespondCreate, OrderID, OrderMessageCreate
from app.services.pull import PullService
from app.common.formats import render_order


router = Router()


class OrderRespond(StatesGroup):
    approved = State()


@router.callback_query(OrderRespondYesNoCallback.filter(F.state == True))
async def respond_order_yes_button(call: types.CallbackQuery, state: FSMContext, callback_data: OrderRespondYesNoCallback):

    order = OrderID.model_validate(await OrderCRUD.get(callback_data.order_id), from_attributes=True)
    configs = await OrderRenderCRUD.get_by_names(OrderRenderCRUD.get_base_names(order))
    text = render_order(order=order, configs=configs)
    await bot.edit_message_text(text, call.from_user.id, call.message.message_id, reply_markup=None)
    await bot.send_message(call.from_user.id,
                           "Enter the price, how long you will start in, and how long it will take to complete")
    await state.set_state(OrderRespond.approved)
    await state.update_data(order=order, message=call.message)


@router.callback_query(OrderRespondYesNoCallback.filter(F.state is False))
async def respond_order_no_button_message(call: types.CallbackQuery, callback_data: OrderRespondYesNoCallback):
    await call.answer()
    await bot.delete_message(call.message.chat.id, call.message.message_id)


@router.message(OrderRespond.approved, F.text)
async def respond_done_order(message: Message, state: FSMContext):
    data = await state.get_data()
    order = cast(OrderID, data.get("order"))
    msg: Message = data.get("message")
    extra = OrderRespondExtra(text=message.text)

    data = OrderRespondCreate(
        order_id=order.id,
        user_id=message.from_user.id,
        channel_id_booster=msg.chat.id,
        message_id_booster=msg.message_id,
        username=message.from_user.username,
        approved=False,
        strict=False,
        extra=extra,
    )

    configs = await OrderRenderCRUD.get_by_names(OrderRenderCRUD.get_base_respond_names(order))
    text = render_order(order=order, respond=data, configs=configs)
    try:
        await bot.edit_message_text(text, message.from_user.id, msg.message_id)
    except exceptions.TelegramBadRequest:
        pass

    message_create = OrderMessageCreate(channel_id=config.app.admin_chat, order_id=order.id,
                                        config_names=OrderRenderCRUD.get_base_respond_names(order))
    await PullService.pull_respond(data, message_create)
    await message.answer("Done! Order sent to admins")
    await state.clear()
