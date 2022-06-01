from marshmallow import Schema, fields, post_load, pre_load, pre_dump
from marshmallow_mongoengine import ModelSchema

from main.models.user import User
import json


class UserRegistrationSchema(ModelSchema):
    class Meta:
        model = User
        exclude = [
            "_id",
        ]


user_registration_schema = UserRegistrationSchema()
