from aiogram import types, exceptions
from aiogram.types import InlineKeyboardButton, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardMarkup
from beanie import PydanticObjectId
from loguru import logger

from app import config
from app.bot import bot
from app.common import render_order, render_template, utcnow_day
from app.bot.cbdata import OrderRespondCallback, OrderRespondConfirmCallback
from app.services.google import GoogleSheetsServiceManager
from app.schemas import (
    Order,
    OrderRespond,
    OrderRespondCreate,
    OrderMessage,
    OrderMessageCreate,
    OrderMessageUpdate,
    OrderSheetUpdate,
    RenderConfig,
    OrderChannel,
    User
)


class PullService:
    @classmethod
    async def pull_respond_check(cls, order_id: PydanticObjectId, user_id: PydanticObjectId) -> bool:
        return bool(await OrderRespond.find_one(OrderRespond.id == order_id, OrderRespond.user_id == user_id))

    @classmethod
    async def pull_respond_check_total(cls, user_id: int):
        pass

    @classmethod
    def get_reply_markup(cls, order_id: PydanticObjectId) -> InlineKeyboardMarkup:
        blr = InlineKeyboardBuilder()
        for i in range(1, 5):
            blr.add(InlineKeyboardButton(text=f"{i * 15} min",
                                         callback_data=OrderRespondCallback(order_id=order_id, time=i * 900).pack()))
        blr.adjust(3)
        return blr.as_markup()

    @classmethod
    async def create_message(
            cls,
            order: Order,
            tg_channels: list[int],
            message_create: OrderMessageCreate,
            *,
            reply_markup: InlineKeyboardMarkup = None
    ) -> list[OrderMessage]:
        resp = []
        configs = await RenderConfig.get_by_names(message_create.config_names)

        for ch in tg_channels:
            text = render_order(order=order, configs=configs)
            msg = await bot.send_message(chat_id=ch, text=text, reply_markup=reply_markup)
            resp.append(msg)

        return resp

    @classmethod
    async def edit_message(
            cls,
            order: Order,
            message_update: OrderMessageUpdate,
            *,
            reply_markup: InlineKeyboardMarkup = None
    ) -> types.Message | None:
        configs = await RenderConfig.get_by_names(message_update.config_names)
        text = render_order(order=order, configs=configs)
        try:
            message = await bot.edit_message_text(text,
                                                  chat_id=message_update.channel_id,
                                                  message_id=message_update.message_id,
                                                  reply_markup=reply_markup)
        except exceptions.TelegramBadRequest:
            return
        return message

    @classmethod
    async def get_pulls(cls, order: Order) -> list[OrderMessage]:
        return await OrderMessage.get_by_order_id(order.id)

    @classmethod
    async def pull_create(cls, order: Order, message_create: OrderMessageCreate):
        categories: str = order.info.get("tg_channels")
        channels_id = []
        resp = []
        messages = await OrderMessage.get_by_order_id(order.id)
        configs = await RenderConfig.get_by_names(message_create.config_names)
        sent = [msg.channel_id for msg in messages]

        if categories:
            categories: list[str] = categories.split('/')
            for category in categories:
                m = await OrderChannel.get_by_game_category(order.game, category)
                if m:
                    channels_id.append(m.channel_id)

        if not channels_id:
            channel = await OrderChannel.get_by_game_category(order.game, None)
            if not channel:
                raise ValueError(f"No channels [game={order.game}]")
            channels_id.append(channel.channel_id)

        for ch in channels_id:
            if ch not in sent:
                text = render_order(order=order, configs=configs)
                reply_markup = cls.get_reply_markup(order.id)
                msg = await bot.send_message(chat_id=ch, text=text, reply_markup=reply_markup)
                model = await OrderMessage(order_id=order, channel_id=ch, message_id=msg.message_id).create()
                resp.append(model)

        return resp

    @classmethod
    async def pull_edit(cls, order: Order, message_create: OrderMessageUpdate) -> list[OrderMessage]:
        messages = await OrderMessage.get_by_order_id(order.id)
        configs = await RenderConfig.get_by_names(message_create.config_names)
        resp = []
        for msg in messages:
            text = render_order(order=order, configs=configs)
            reply_markup = cls.get_reply_markup(order.id)
            try:
                await bot.edit_message_text(text, chat_id=msg.channel_id, message_id=msg.message_id,
                                            reply_markup=reply_markup)
                resp.append(msg)
            except exceptions.TelegramBadRequest:
                pass
        return resp

    @classmethod
    async def pull_delete(cls, order: Order) -> list[OrderMessage]:
        messages = await OrderMessage.get_by_order_id(order.id)
        for message in messages:
            try:
                await bot.delete_message(chat_id=message.channel_id, message_id=message.message_id)
            except exceptions.TelegramBadRequest:
                pass
            await message.delete()

        return [OrderMessage.model_validate(message, from_attributes=True) for message in messages]

    @classmethod
    async def pull_delete_message(cls, message: OrderMessage) -> OrderMessage:
        try:
            await bot.delete_message(chat_id=message.channel_id, message_id=message.message_id)
        except exceptions.TelegramBadRequest:
            pass
        await message.delete()
        return message

    @classmethod
    async def pull_respond(cls, data: OrderRespondCreate, message_create: OrderMessageCreate) -> OrderRespond:
        msg = await cls.pull_create_admin(data, message_create)
        data.message_id_admin = msg.message_id
        resp = OrderRespond(**data.model_dump())
        return await resp.create()

    @classmethod
    async def pull_create_admin(cls, data: OrderRespondCreate, message_create: OrderMessageCreate) -> Message:
        order = await Order.get(data.order_id)
        configs = await RenderConfig(message_create.config_names)
        message = render_order(order=order, respond=data, configs=configs)
        cb = OrderRespondConfirmCallback(order_id=order.id, user_id=data.user_id)
        builder = InlineKeyboardBuilder([[InlineKeyboardButton(text="Принять", callback_data=cb.pack())]])
        return await bot.send_message(config.app.admin_chat, text=message, reply_markup=builder.as_markup())

    @classmethod
    async def pull_close(cls, order: Order, user_id: int) -> None:
        responds = await OrderRespond.get_by_order_id(order_id=order.id)
        messages = await OrderMessage.get_by_order_id(order_id=order.id)
        names = RenderConfig.get_base_names(order)
        names.append("resp-admin")
        configs = await RenderConfig.get_by_names(names)
        for resp in responds:
            booster = await User.get_by_user_id(resp.user_id)
            if resp.user_id == user_id:
                resp.approved = True
                await resp.save()
                await cls.pull_booster_resp_yes(order, booster, resp)
            else:
                await cls.pull_booster_resp_no(order, booster)
            try:
                msg = render_order(order=order, respond=resp, configs=configs)
                await bot.edit_message_text(msg, config.app.admin_chat, resp.message_id_admin)
            except exceptions.TelegramBadRequest:
                pass
        for message in messages:
            await cls.pull_delete_message(message)

    @classmethod
    async def pull_booster_resp_yes(cls, order: Order, booster: User, resp: OrderRespond):
        data = OrderSheetUpdate(booster=booster.name, auth_date=utcnow_day())
        x = await GoogleSheetsServiceManager.get().update_order(order.spreadsheet,
                                                                order.sheet_id, order.order_id, data)
        order.update_from(x)
        await order.save()

        configs = await RenderConfig.get_by_names(['base', f"{x.game}-cd", 'eta-price'])
        data = {"order": order, "resp": resp, "rendered_order": render_order(order=x, configs=configs)}
        try:
            await bot.send_message(resp.user_id, render_template("order_response_approve.j2", data))
        except exceptions.TelegramBadRequest:
            pass

    @classmethod
    async def pull_booster_resp_no(cls, order: Order, booster: User):
        try:
            await bot.send_message(booster.user_id, render_template("order_response_decline.j2", {"order": order}))
        except exceptions.TelegramBadRequest:
            pass
