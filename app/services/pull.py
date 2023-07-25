from aiogram import types, exceptions
from aiogram.types import InlineKeyboardButton, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardMarkup
from loguru import logger

from app.common.formats import OrderRender
from app.crud import OrderMessageCRUD, OrderChannelCRUD, OrderCRUD, OrderRespondCRUD, OrderRenderCRUD, BoosterCRUD
from app.bot import bot
from app.bot.cbdata import OrderRespondCallback, OrderRespondConfirmCallback
from app.db import OrderRespondModel
from app.services.google import GoogleSheetsServiceManager
from app.schemas import (
    OrderID,
    OrderMessageID,
    OrderRespondCreate,
    OrderRespondID,
    OrderMessage,
    OrderMessageCreate,
    OrderMessageUpdate,
    OrderRespondUpdate,
    BoosterID,
    OrderSheetUpdate,
)

import config


class PullService:
    @classmethod
    async def pull_respond_check(cls, order_id: int, user_id: int) -> bool:
        return bool(await OrderRespondCRUD.get_by_order_user_id(order_id=order_id, user_id=user_id))

    @classmethod
    async def pull_respond_check_total(cls, user_id: int):
        pass

    @classmethod
    def get_reply_markup(cls, order_id: int) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        builder.add(InlineKeyboardButton(text="15 min",
                                         callback_data=OrderRespondCallback(order_id=order_id, time=15*60).pack()))
        builder.add(InlineKeyboardButton(text="20 min",
                                         callback_data=OrderRespondCallback(order_id=order_id, time=20*60).pack()))
        builder.add(InlineKeyboardButton(text="60 min",
                                         callback_data=OrderRespondCallback(order_id=order_id, time=60*60).pack()))
        builder.add(InlineKeyboardButton(text="start now",
                                         callback_data=OrderRespondCallback(order_id=order_id, time=0).pack()))
        builder.adjust(3)
        return builder.as_markup()

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
        configs = await OrderRenderCRUD.get_by_names(message_create.config_names)

        for ch in tg_channels:
            text = OrderRender().render(order=order, configs=configs).__str__()
            msg = await bot.send_message(chat_id=ch, text=text, reply_markup=reply_markup)
            resp.append(msg)

        return resp

    @classmethod
    async def edit_message(
            cls,
            order: OrderID,
            message_update: OrderMessageUpdate,
            *,
            reply_markup: InlineKeyboardMarkup = None
    ) -> types.Message | None:
        configs = await OrderRenderCRUD.get_by_names(message_update.config_names)
        text = OrderRender().render(order=order, configs=configs).__str__()
        try:
            message = await bot.edit_message_text(text,
                                                  chat_id=message_update.channel_id,
                                                  message_id=message_update.message_id,
                                                  reply_markup=reply_markup)
        except exceptions.TelegramBadRequest:
            return
        return message

    @classmethod
    async def get_pulls(cls, order: OrderID) -> list[OrderMessageID]:
        messages = await OrderMessageCRUD.get_by_order_id(order.id)
        return [OrderMessageID.model_validate(message, from_attributes=True) for message in messages]

    @classmethod
    async def pull_create(cls, order: OrderID, message_create: OrderMessageCreate):
        categories: str = order.info.get("tg_channels")
        channels_id = []
        resp = []
        messages = await OrderMessageCRUD.get_by_order_id(order.id)
        configs = await OrderRenderCRUD.get_by_names(message_create.config_names)
        sent = [msg.channel_id for msg in messages]

        if categories:
            categories: list[str] = categories.split('/')
            for category in categories:
                m = await OrderChannelCRUD.get_by_game_category(order.game, category)
                if m:
                    channels_id.append(m.channel_id)

        if not channels_id:
            channel = await OrderChannelCRUD.get_by_game_category(order.game, None)
            if not channel:
                raise ValueError(f"No channels [game={order.game}]")
            channels_id.append(channel.channel_id)

        for ch in channels_id:
            if ch not in sent:
                text = OrderRender().render(order=order, configs=configs).__str__()
                reply_markup = cls.get_reply_markup(order.id)
                msg = await bot.send_message(chat_id=ch, text=text, reply_markup=reply_markup)
                obj = OrderMessage(order_id=order.id, channel_id=ch, message_id=msg.message_id)
                model = await OrderMessageCRUD.create(obj_in=obj)
                resp.append(OrderMessageID.model_validate(model, from_attributes=True))

        return resp

    @classmethod
    async def pull_edit(cls, order: OrderID, message_create: OrderMessageUpdate) -> list[OrderMessageID]:
        messages = await OrderMessageCRUD.get_by_order_id(order.id)
        configs = await OrderRenderCRUD.get_by_names(message_create.config_names)
        resp = []
        for message in messages:
            text = OrderRender().render(order=order, configs=configs).__str__()
            reply_markup = cls.get_reply_markup(order.id)
            try:
                await bot.edit_message_text(text,
                                            chat_id=message.channel_id,
                                            message_id=message.message_id,
                                            reply_markup=reply_markup)
                resp.append(OrderMessageID.model_validate(message, from_attributes=True))
            except exceptions.TelegramBadRequest:
                pass
        return resp

    @classmethod
    async def pull_delete(cls, order: OrderID) -> list[OrderMessageID]:
        messages = await OrderMessageCRUD.get_by_order_id(order.id)
        for message in messages:
            try:
                await bot.delete_message(chat_id=message.channel_id, message_id=message.message_id)
            except exceptions.TelegramBadRequest:
                pass
            await message.delete()

        return [OrderMessageID.model_validate(message, from_attributes=True) for message in messages]

    @classmethod
    async def pull_delete_message(cls, message: OrderMessageID) -> OrderMessageID:
        try:
            await bot.delete_message(chat_id=message.channel_id, message_id=message.message_id)
        except exceptions.TelegramBadRequest:
            pass
        await OrderMessageCRUD.remove(id=message.id)
        return message

    @classmethod
    async def pull_respond(cls, data: OrderRespondCreate, message_create: OrderMessageCreate) -> OrderRespondID:
        msg = await cls.pull_create_admin(data, message_create)
        data.message_id_admin = msg.message_id
        model = await OrderRespondCRUD.create(obj_in=data)
        return OrderRespondID.model_validate(model, from_attributes=True)

    @classmethod
    async def pull_create_admin(cls, data: OrderRespondCreate, message_create: OrderMessageCreate) -> Message:
        order = OrderID.model_validate(await OrderCRUD.get(data.order_id), from_attributes=True)
        configs = await OrderRenderCRUD.get_by_names(message_create.config_names)
        message = OrderRender().render(order=order, respond=data, configs=configs).__str__()

        cb = OrderRespondConfirmCallback(order_id=order.id, user_id=data.user_id)
        builder = InlineKeyboardBuilder()
        builder.add(InlineKeyboardButton(text="Принять", callback_data=cb.pack()))

        return await bot.send_message(config.app.admin_chat, text=message, reply_markup=builder.as_markup())

    @classmethod
    async def pull_close(cls, order: OrderID, user_id: int) -> None:
        responds = await OrderRespondCRUD.get_by_order_id(order_id=order.id)
        messages = await OrderMessageCRUD.get_by_order_id(order_id=order.id)
        names = OrderRenderCRUD.get_base_names(order)
        names.append("resp-admin")
        configs = await OrderRenderCRUD.get_by_names(names)
        for resp in responds:
            booster = await BoosterCRUD.get_by_user_id(resp.user_id)
            if resp.user_id == user_id:
                resp = await OrderRespondCRUD.update(db_obj=resp, obj_in=OrderRespondUpdate(approved=True))
                await cls.pull_booster_resp_yes(order, booster, resp)
            else:
                await cls.pull_booster_resp_no(order, booster)
            try:
                resp_pyd = OrderRespondID.model_validate(resp, from_attributes=True)
                msg = OrderRender().render(order=order, respond=resp_pyd, configs=configs)
                await bot.edit_message_text(msg.__str__(), config.app.admin_chat, resp.message_id_admin)
            except exceptions.TelegramBadRequest:
                pass
        for message in messages:
            await cls.pull_delete_message(OrderMessageID.model_validate(message, from_attributes=True))

    @classmethod
    async def pull_booster_resp_yes(cls, order: OrderID, booster: BoosterID, resp: OrderRespondModel):
        model = await OrderCRUD.get(order.id)
        await OrderCRUD.update(db_obj=model, obj_in=order)
        data = OrderSheetUpdate(booster=booster.name)
        x = await GoogleSheetsServiceManager.get().update_order("M+", 0, order.order_id, data)
        await OrderCRUD.update(db_obj=model, obj_in=x)

        msg = ["Hello!\n",
               f"You have been applied for Order #{order.order_id} and",
               f"selected start time in {resp.extra.eta.seconds / 60} min.",
               "Here is full order information.\n"
               ]
        names = ['base', f"{x.game}-cd", 'eta-price']
        configs = await OrderRenderCRUD.get_by_names(names)
        message = OrderRender().render(order=x, configs=configs)
        msg.append(message.__str__())
        msg.append(f"\nHere is your Discord conference invite, please join and start the order")
        try:
            await bot.send_message(booster.user_id, '\n'.join(msg))
        except exceptions.TelegramBadRequest:
            pass

    @classmethod
    async def pull_booster_resp_no(cls, order: OrderID, booster: BoosterID):
        try:
            await bot.send_message(booster.user_id, f"Sorry, order #{order.order_id} was taken by another player")
        except exceptions.TelegramBadRequest:
            pass
