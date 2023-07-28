from aiogram import Router, types

from app.schemas import Order
from app.services.pull import PullService
from app.bot.cbdata import OrderRespondConfirmCallback
from app.bot import bot

router = Router()


@router.callback_query(OrderRespondConfirmCallback.filter())
async def close_order(call: types.CallbackQuery, callback_data: OrderRespondConfirmCallback):
    await call.answer()

    order = await Order.get(callback_data.order_id)
    await PullService.pull_close(order, callback_data.user_id)
