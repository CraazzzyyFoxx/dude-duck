from typing import cast

from telegram import Update, User, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.constants import ParseMode
from telegram.ext import CallbackContext
from telegram.error import Forbidden

import config
from app.db import UserModel
from app.models import (
    RESPOND_ORDER_CALLBACK,
    ORDER_CONFIRM_YES_CALLBACK,
    ORDER_CONFIRM_NO_CALLBACK,
    ORDER_CONFIRM_NO_ARBITRARY_CALLBACK,
    ORDER_CONFIRM_YES_ARBITRARY_CALLBACK
)
from app.schemas import OrderID
from app.crud import OrderCRUD
from app.services.pull import PullService
from app.utils import format_error, OrderRender


async def entry_point(update: Update, context: CallbackContext):
    query = update.callback_query
    if not query.data or not query.data.strip():
        return

    user = cast(User, update.effective_user)

    order_id = RESPOND_ORDER_CALLBACK.parse(query.data)
    order = OrderID.model_validate(await OrderCRUD.get(order_id), from_attributes=True)

    # if not order:
    #     await user.send_message(format_error("The order has already been picked up by someone else"),
    #                             parse_mode=ParseMode.HTML)
    #     return

    if await PullService.pull_respond_check(order.id, user.id):
        await user.send_message(format_error("You have already responded to this order!"), parse_mode=ParseMode.HTML)
        return

    context.user_data["order_confirm"] = order

    user_model = await UserModel.filter(user_id=user.id).first()

    if user_model and user_model.respond_mode:
        markup = InlineKeyboardMarkup([[
            InlineKeyboardButton("Accept", callback_data=ORDER_CONFIRM_YES_CALLBACK.compile(order_id=order.id)),
            InlineKeyboardButton("Decline", callback_data=ORDER_CONFIRM_NO_CALLBACK.compile(order_id=order.id)),
        ]])
    else:
        markup = InlineKeyboardMarkup([[
            InlineKeyboardButton("Accept",
                                 callback_data=ORDER_CONFIRM_YES_ARBITRARY_CALLBACK.compile(order_id=order.id)),
            InlineKeyboardButton("Decline",
                                 callback_data=ORDER_CONFIRM_NO_ARBITRARY_CALLBACK.compile(order_id=order.id)),
        ]])
    try:
        await user.send_message(OrderRender().render(order=order).__str__(),
                                parse_mode=ParseMode.HTML,
                                reply_markup=markup)
    except Forbidden:
        await query.answer(url=config.START_ALERT)
