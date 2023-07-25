from aiogram.filters.callback_data import CallbackData


class OrderRespondCallback(CallbackData, prefix="respond_order"):
    order_id: int
    time: int


class OrderRespondYesNoCallback(CallbackData, prefix="order_confirm_yes"):
    order_id: int
    state: bool


class OrderRespondConfirmCallback(CallbackData, prefix="order_admin_confirm"):
    order_id: int
    user_id: int
