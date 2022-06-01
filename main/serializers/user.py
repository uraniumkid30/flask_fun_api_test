from marshmallow import Schema, fields, post_load, pre_load, pre_dump
from marshmallow_mongoengine import ModelSchema

from main.models.user import User
import json

# class UserSchema(Schema):
#     name = fields.Str()
#     location = fields.Str()


class UserSchema(ModelSchema):
    # @post_load
    # def refine_output(self, data, **kwargs):
    #     object_dict = json.loads(data.to_json())
    #     if object_dict.get("password"):
    #         object_dict.pop("password")

    #     return data.from_json(json.dumps(object_dict))

    class Meta:
        model = User
        exclude = [
            "password",
        ]


class UserRegistrationSchema(ModelSchema):
    class Meta:
        model = User
        exclude = [
            "_id",
        ]


user_schema = UserSchema()
user_registration_schema = UserRegistrationSchema()
