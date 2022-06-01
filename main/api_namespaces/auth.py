from flask_restx import Namespace, fields

api = Namespace("Authentication", description="Authentication related APIs")


user_register_model = api.model(
    "SignupModel",
    {
        "first_name": fields.String(
            description="First Name of the user", required=True
        ),
        "last_name": fields.String(description="Last Name of the user", required=True),
        "email": fields.String(description="Email address", required=True),
        "password": fields.String(description="password", required=True),
    },
)


user_login_model = api.model(
    "LoginModel",
    {
        "email": fields.String(description="Email address", required=True),
        "password": fields.String(description="Password", required=True),
    },
)
