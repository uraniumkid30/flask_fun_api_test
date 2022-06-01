from marshmallow import Schema, fields
from marshmallow_mongoengine import ModelSchema

from main.models.template import Template


class TemplateSchema(ModelSchema):
    class Meta:
        model = Template
        exclude = [
            "_id",
        ]


template_schema = TemplateSchema()
