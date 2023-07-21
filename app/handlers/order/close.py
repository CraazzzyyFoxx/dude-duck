from __future__ import annotations

from telegram import Update
from telegram.ext import CallbackContext

import config
from app.models import CONFIRM_ORDER_RESPONSE_CALLBACK

from app.services.pull import PullService


async def close_order(update: Update, _: CallbackContext):
    query = update.callback_query
    await query.answer()
    if not query.data or not query.data.strip():
        return

    order_id, user_id = CONFIRM_ORDER_RESPONSE_CALLBACK.parse(query.data)
    if order_id > user_id:
        order_id, user_id = user_id, order_id

    await PullService.pull_close(order_id, user_id)
