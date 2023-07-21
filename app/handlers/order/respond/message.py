from __future__ import annotations

from typing import cast

from telegram import Update, User
from telegram.error import BadRequest
from telegram.constants import ParseMode
from telegram.ext import (
    ConversationHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    CommandHandler,
    CallbackContext
)

from app.schemas import OrderRespondExtra, OrderRespondCreate, OrderID
from app.services.pull import PullService
from app.models import ORDER_CONFIRM_YES_ARBITRARY_CALLBACK
from app.utils import OrderRender

DONE = range(1)


async def respond_order_yes_button(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    if not query.data or not query.data.strip():
        return

    user = cast(User, update.effective_user)
    context.chat_data["order"] = context.user_data.pop("order_confirm")
    context.chat_data["user"] = user
    context.chat_data["choice"] = DONE
    context.chat_data["message"] = update.effective_message

    order = cast(OrderID, context.chat_data["order"])
    await update.effective_message.edit_text(
        OrderRender().render(order=order).__str__(), parse_mode=ParseMode.HTML
    )
    await user.send_message("Enter the price, how long you will start in, and how long it will take to complete")
    return DONE


async def respond_order_no_button_message(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    if not query.data or not query.data.strip():
        return

    await update.effective_message.delete()
    context.chat_data.clear()


async def respond_done_order(update: Update, context: CallbackContext):
    order = cast(OrderID, context.chat_data["order"])
    user = cast(User, context.chat_data["user"])
    message = context.chat_data["message"]
    extra = OrderRespondExtra(text=update.message.text)

    data = OrderRespondCreate(
        order_id=order.id,
        user_id=user.id,
        channel_id_booster=context.chat_data["message"].chat_id,
        message_id_booster=context.chat_data["message"].id,
        username=user.name,
        approved=False,
        strict=False,
        extra=extra,
    )

    try:
        await message.edit_text(OrderRender().render(order=order, respond=data).__str__(),
                                parse_mode=ParseMode.HTML)
    except BadRequest:
        pass

    await PullService.pull_respond(data)
    await update.effective_user.send_message("Done! Order sent to admins")

    context.chat_data.clear()
    return ConversationHandler.END


async def stop(update: Update, context: CallbackContext) -> int:
    await update.effective_user.send_message("Submit order canceled!")
    context.chat_data.clear()
    return ConversationHandler.END


order_conversation_message = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(respond_order_yes_button, ORDER_CONFIRM_YES_ARBITRARY_CALLBACK.regex())
    ],
    states={
        DONE: [
            MessageHandler(filters.TEXT & ~(filters.COMMAND | filters.Regex("^Done$")), respond_done_order)
        ],

    },
    fallbacks=[CommandHandler("stop", stop)],
    conversation_timeout=300,
)
