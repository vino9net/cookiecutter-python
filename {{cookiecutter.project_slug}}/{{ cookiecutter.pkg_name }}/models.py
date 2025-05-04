from tortoise import fields
from tortoise.models import Model


class User(Model):
    id = fields.IntField(pk=True)
    login_name = fields.CharField(max_length=32)
    alias = fields.CharField(max_length=32, default="007")

    class Meta:
        table = "users"
