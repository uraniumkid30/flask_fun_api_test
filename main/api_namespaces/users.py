from flask_restx import Namespace, Resource, fields


api = Namespace("User", description="User related APIs")

user_model = api.model(
    "UpdateUserModel",
    {
        "first_name": fields.String(description="First Name of the user"),
        "last_name": fields.String(description="Last Name of the user"),
        "email": fields.String(description="Email address", required=True),
        "password": fields.String(description="password", required=True),
    },
)
