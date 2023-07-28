from aiogram import Router, types, exceptions
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.schemas import OrderDB
from app.services.pull import PullService
from app.common.formats import format_err, render_order
from app.bot.cbdata import OrderRespondCallback, OrderRespondYesNoCallback
from app.bot import bot

router = Router()


@router.callback_query(OrderRespondCallback.filter())
async def entry_point(call: types.CallbackQuery, callback_data: OrderRespondCallback):
    booster = await BoosterCRUD.get_by_user_id(call.from_user.id)
    if not booster or not booster.verified:
        try:
            await bot.send_message(call.from_user.id,
                                   format_err("You can't pick orders because there is no verification or registration."))
        except exceptions.TelegramAPIError:
            me = await bot.get_me()
            await call.answer(url=f"https://t.me/{me.username}?start=Hello")
        await call.answer()
        return

    order = OrderID.model_validate(await OrderCRUD.get(callback_data.order_id), from_attributes=True)

    if await PullService.pull_respond_check(order.id, call.from_user.id):
        try:
            await bot.send_message(call.from_user.id,
                                   format_err("You have already responded to this order"))
        except exceptions.TelegramAPIError:
            me = await bot.get_me()
            await call.answer(url=f"https://t.me/{me.username}?start=Hello")
        await call.answer()
        return

    builder = InlineKeyboardBuilder()
    data = [("Accept", True), ("Decline", False)]
    for row in data:
        builder.add(InlineKeyboardButton(text=row[0],
                                         callback_data=OrderRespondYesNoCallback(
                                             order_id=callback_data.order_id, state=row[1]).pack()))

    configs = await OrderRenderCRUD.get_by_names(OrderRenderCRUD.get_base_names(order))

    try:
        await bot.send_message(call.from_user.id,
                               render_order(order=order, configs=configs),
                               reply_markup=builder.as_markup())
    except exceptions.TelegramAPIError:
        me = await bot.get_me()
        await call.answer(url=f"https://t.me/{me.username}?start=Hello")
