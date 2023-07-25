import datetime

from tortoise import fields
from tortoise.models import Model

from app.schemas import OrderRespondExtra, OrderSheetParseItemList, RenderFieldConfigList


class OrderModel(Model):
    id: int = fields.IntField(pk=True, generated=True)

    order_id: int = fields.IntField()
    date: datetime.datetime = fields.DatetimeField()
    exchange: float = fields.FloatField()
    shop: str = fields.TextField()
    shop_order_id: str | int | None = fields.TextField(null=True)
    boost_type: str = fields.TextField()
    region_fraction: str = fields.TextField()
    server: str | None = fields.TextField(null=True)
    character_class: str | None = fields.TextField(null=True)
    nickname: str | None = fields.TextField(null=True)
    game: str = fields.TextField()
    purchase: str = fields.TextField()
    comment: str | None = fields.TextField(null=True)
    battle_tag: str | None = fields.TextField(null=True)
    contact: str | None = fields.TextField(null=True)
    booster: str | None = fields.TextField(null=True)
    auth_date: str | None = fields.TextField(null=True)
    status: str = fields.TextField()
    screenshot: str | None = fields.TextField(null=True)
    end_date: datetime.datetime | None = fields.DatetimeField(null=True)

    price_dollar: float = fields.FloatField()
    price_booster_dollar: float = fields.FloatField()
    price_booster_dollar_fee: float = fields.FloatField()
    price_booster_rub: float = fields.FloatField()
    price_booster_gold: float = fields.FloatField()
    method_payment: str | None = fields.TextField(null=True)
    profit: float = fields.FloatField()
    share: float = fields.FloatField()

    info: dict = fields.JSONField()

    # message: fields.ReverseRelation['OrderTelegramMessageModel']
    # responds: fields.ReverseRelation['OrderRespondModel']

    class Meta:
        table = "order"


class OrderTelegramMessageModel(Model):
    id: int = fields.IntField(pk=True, generated=True)
    order: fields.ForeignKeyRelation[OrderModel] = fields.ForeignKeyField(model_name='main.OrderModel',
                                                                          on_delete=fields.CASCADE,
                                                                          related_name='order',
                                                                          to_field='id')
    channel_id: int = fields.BigIntField()
    message_id: int = fields.BigIntField()

    class Meta:
        table = "order_tg_message"


class OrderRespondModel(Model):
    id: int = fields.IntField(pk=True, generated=True)
    user_id: int = fields.BigIntField()
    username: str = fields.TextField()

    channel_id_booster: int = fields.BigIntField()
    message_id_booster: int = fields.BigIntField()
    message_id_admin: int = fields.BigIntField()

    approved: bool = fields.BooleanField()
    strict: bool = fields.BooleanField()

    extra: OrderRespondExtra = fields.JSONField(decoder=OrderRespondExtra.model_validate_json)

    order: fields.ForeignKeyRelation['OrderModel'] = fields.ForeignKeyField(model_name='main.OrderModel',
                                                                            on_delete=fields.CASCADE,
                                                                            related_name='responds',
                                                                            to_field='id')

    class Meta:
        table = "order_respond"


class OrderSheetParseModel(Model):
    id: int = fields.IntField(pk=True, generated=True)
    spreadsheet: str = fields.CharField(max_length=30)
    sheet_id: int = fields.IntField()
    extra: OrderSheetParseItemList = fields.JSONField(decoder=OrderSheetParseItemList.model_validate_json)

    class Meta:
        table = "order_parse_sheet"


class OrderChannelModel(Model):
    id: int = fields.IntField(pk=True, generated=True)
    game: str = fields.TextField()
    category: str | None = fields.TextField(null=True)
    channel_id: int = fields.BigIntField()

    class Meta:
        table = "order_channel"


class OrderRenderModel(Model):
    name: str = fields.CharField(max_length=20)
    separator: str = fields.CharField(max_length=20)
    separator_field: str = fields.CharField(max_length=20)
    fields: RenderFieldConfigList = fields.JSONField(decoder=RenderFieldConfigList.model_validate_json)

    class Meta:
        table = "order_render"
