from aiogram.filters.callback_data import CallbackData
from beanie import PydanticObjectId


class OrderRespondCallback(CallbackData, prefix="respond_order"):
    order_id: PydanticObjectId
    time: int


class OrderRespondYesNoCallback(CallbackData, prefix="order_confirm_yes"):
    order_id:  PydanticObjectId
    state: bool


class OrderRespondConfirmCallback(CallbackData, prefix="order_admin_confirm"):
    order_id:  PydanticObjectId
    user_id: int
