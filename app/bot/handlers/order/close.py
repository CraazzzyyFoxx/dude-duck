from aiogram import Router, types

from app.schemas import OrderID
from app.crud import OrderCRUD
from app.services.pull import PullService
from app.bot.cbdata import OrderRespondConfirmCallback
from app.bot import bot

router = Router()


@router.callback_query(OrderRespondConfirmCallback.filter())
async def close_order(call: types.CallbackQuery, callback_data: OrderRespondConfirmCallback):
    call._bot = bot

    await call.answer()

    order = OrderID.model_validate(await OrderCRUD.get(callback_data.order_id), from_attributes=True)
    await PullService.pull_close(order, callback_data.user_id)
