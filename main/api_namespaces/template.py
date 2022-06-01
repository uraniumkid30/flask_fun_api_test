from flask_restx import Namespace, fields

api = Namespace("Templates", description="Templates related APIs")

template_model = api.model(
    "TemplateModel",
    {
        "template_name": fields.String(description="Template name", required=True),
        "subject": fields.String(description="Subject of the Template", required=True),
        "body": fields.String(description="Core message of Template", required=True),
    },
)

update_template_model = api.model(
    "TemplateUpdateModel",
    {
        "template_name": fields.String(description="Template name"),
        "subject": fields.String(description="Subject of the Template"),
        "body": fields.String(description="Core message of Template"),
    },
)
