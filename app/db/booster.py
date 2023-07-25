from tortoise import fields
from tortoise.models import Model


class BoosterModel(Model):
    id: int = fields.IntField(pk=True)
    user_id: int = fields.IntField()
    username: str = fields.TextField()
    verified: bool = fields.BooleanField()
    strict: bool = fields.BooleanField()
    max_count_orders: int = fields.IntField()
    name: str = fields.TextField()
    rub: str | None = fields.TextField(null=True)
    binance: str | None = fields.TextField(null=True)
    gold: str | None = fields.TextField(null=True)
    description: str = fields.TextField()
    discord: str | None = fields.TextField(null=True)

    class Meta:
        table = "booster"
