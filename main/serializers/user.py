from marshmallow import Schema, fields
from marshmallow_mongoengine import ModelSchema

from main.models.user import User

# class UserSchema(Schema):
#     name = fields.Str()
#     location = fields.Str()


class UserSchema(ModelSchema):
    class Meta:
        model = User
        exclude = [
            "id",
        ]


user_schema = UserSchema()
