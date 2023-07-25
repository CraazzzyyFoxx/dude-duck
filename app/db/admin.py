from tortoise import fields
from tortoise.models import Model

from app.schemas import AdminGoogleToken


class AdminModel(Model):
    id: int = fields.IntField(pk=True)
    token: str = fields.CharField(max_length=256)
    name: str = fields.CharField(max_length=20)
    google: AdminGoogleToken = fields.JSONField(decoder=AdminGoogleToken.model_validate_json)

    class Meta:
        table = "admin"
