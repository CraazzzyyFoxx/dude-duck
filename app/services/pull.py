from loguru import logger
from telegram import InlineKeyboardMarkup, InlineKeyboardButton, Message
from telegram.constants import ParseMode
from telegram.error import BadRequest

import config
from app.db import OrderTelegramMessageModel

from app.utils import OrderRender
from app.models import CONFIRM_ORDER_RESPONSE_CALLBACK, RESPOND_ORDER_CALLBACK
from app.schemas import OrderID, OrderMessageID, OrderRespondCreate, OrderRespondID, OrderMessage, OrderMessageCreate
from app.crud import OrderMessageCRUD, OrderChannelCRUD, OrderCRUD, OrderRespondCRUD, OrderRenderCRUD
from app.models.bot import application


class PullService:
    @classmethod
    async def pull_respond_check(cls, order_id: int, user_id: int) -> bool:
        return bool(await OrderRespondCRUD.get_by_order_user_id(order_id=order_id, user_id=user_id))

    @classmethod
    def get_reply_markup(cls, order_id: int):
        markup = InlineKeyboardMarkup(
            [[
                InlineKeyboardButton("Откликнуться",
                                     callback_data=RESPOND_ORDER_CALLBACK.compile(order_id=order_id)),
            ]]
        )
        return markup

    @classmethod
    async def create_message(
            cls,
            order: OrderID,
            tg_channels: list[int],
            message_create: OrderMessageCreate,
            *,
            reply_markup: InlineKeyboardMarkup = None
    ) -> list[OrderMessageID]:
        resp = []
        messages = await OrderMessageCRUD.get_by_order_id(order.id)
        configs = await OrderRenderCRUD.get_by_names(message_create.config_names)
        sent = [msg.channel_id for msg in messages]

        for ch in tg_channels:
            if ch not in sent:
                text = OrderRender().render(order=order, configs=configs).__str__()
                if not reply_markup:
                    reply_markup = cls.get_reply_markup(order.id)
                msg = await application.bot.send_message(chat_id=ch, text=text, reply_markup=reply_markup)
                obj = OrderMessage(order_id=order.id, channel_id=ch, message_id=msg.message_id)
                model = await OrderMessageCRUD.create(obj_in=obj)
                resp.append(OrderMessageID.model_validate(model, from_attributes=True))

        return resp

    @classmethod
    async def edit_message(cls, order: OrderID) -> list[OrderMessageID]:
        messages = await OrderMessageCRUD.get_by_order_id(order.id)
        configs = await OrderRenderCRUD.get_by_names(["Base"])
        resp = []
        for message in messages:
            text = OrderRender().render(order=order, configs=configs).__str__()
            reply_markup = cls.get_reply_markup(order.id)
            await application.bot.edit_message_text(chat_id=message.channel_id,
                                                    message_id=message.message_id,
                                                    text=text,
                                                    reply_markup=reply_markup)
            resp.append(OrderMessageID.model_validate(message, from_attributes=True))
        return resp

    @classmethod
    async def get_messages(cls, order: OrderID) -> list[OrderMessageID]:
        messages = await OrderMessageCRUD.get_by_order_id(order.id)
        return [OrderMessageID.model_validate(message, from_attributes=True) for message in messages]

    @classmethod
    async def delete_messages(cls, order: OrderID) -> list[OrderMessageID]:
        messages = await OrderMessageCRUD.get_by_order_id(order.id)
        for message in messages:
            await application.bot.delete_message(chat_id=message.channel_id, message_id=message.message_id)
            await message.delete()

        return [OrderMessageID.model_validate(message, from_attributes=True) for message in messages]

    @classmethod
    async def delete_message(cls, message: OrderTelegramMessageModel) -> OrderMessageID:
        await application.bot.delete_message(chat_id=message.channel_id, message_id=message.message_id)
        await message.delete()
        return OrderMessageID.model_validate(message, from_attributes=True)

    @classmethod
    async def pull_order(cls, order: OrderID, message_create: OrderMessageCreate):
        categories: str = order.info.get("tg_channels")
        channels_id = []

        if categories:
            categories: list[str] = categories.split('/')
            for category in categories:
                m = await OrderChannelCRUD.get_by_game_category(order.game, category)
                if m:
                    channels_id.append(m.channel_id)

        if not channels_id:
            channel = await OrderChannelCRUD.get_by_game_category(order.game, None)
            channels_id.append(channel.channel_id)

        resp = await cls.create_message(order, channels_id, message_create)
        return resp

    @classmethod
    async def pull_respond(cls, data: OrderRespondCreate, message_create: OrderMessageCreate) -> OrderRespondID:
        msg = await cls.pull_send_admins(data, message_create)
        data.message_id_admin = msg.message_id
        model = await OrderRespondCRUD.create(obj_in=data)
        return OrderRespondID.model_validate(model, from_attributes=True)

    @classmethod
    async def pull_send_admins(cls, data: OrderRespondCreate, message_create: OrderMessageCreate) -> Message:
        order = OrderID.model_validate(await OrderCRUD.get(data.order_id), from_attributes=True)
        configs = await OrderRenderCRUD.get_by_names(message_create.config_names)
        message = OrderRender().render(order=order, respond=data, configs=configs).__str__()

        cb = CONFIRM_ORDER_RESPONSE_CALLBACK.compile(order_id=order.id, user_id=data.user_id)
        keyboard = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("Принять", callback_data=cb)]
            ]
        )

        return await application.bot.send_message(config.app.ADMIN_CHAT,
                                                  text=message,
                                                  reply_markup=keyboard,
                                                  parse_mode=ParseMode.HTML)

    @classmethod
    async def pull_close(cls, order_id: int, user_id: int) -> None:
        order = await OrderService.get_order_by_id(order_id)
        responds = await OrderRespondModel.filter(order_id=order_id)
        messages = await OrderTelegramMessageModel.filter(order_id=order_id)
        total = len(responds)
        for respond in responds:
            msg = OrderRender().render(order=order, respond=OrderRespond.model_validate(respond))
            if respond.user_id == user_id:
                respond.approved = True
                await respond.save()
                msg = msg.approved(True, total)
            else:
                msg.approved(False, total)
            await application.bot.edit_message_text(msg.__str__(),
                                                    config.app.ADMIN_CHAT,
                                                    respond.message_id_admin,
                                                    parse_mode=ParseMode.HTML)
        for message in messages:
            try:
                await application.bot.delete_message(message.channel_id, message.message_id)
            except BadRequest:
                pass
