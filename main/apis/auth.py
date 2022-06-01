from flask_restx import Namespace, Resource, fields

from flask import request
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    jwt_refresh_token_required,
    jwt_required,
)


from main.models.user import User
from utilities.utils import Utils, Status

from main.serializers.user import user_schema
from main.services.jwt_service import JWTService
from main.services.user_service import UserService
from main.serializers.auth import user_registration_schema
from main.serializers.error_manager import validate_fields
from main.services.blacklist_helpers import BlacklistHelper
from main.services.utils import convert_to_model_obj_from_json
from main.api_namespaces.auth import api, user_register_model, user_login_model


@api.route("/auth/register")
class UserRegister(Resource):
    """docstring for UserRegister."""

    def __init__(self, arg):
        super(UserRegister, self).__init__(arg)
        self.jwt_service = JWTService()
        self.blacklist = BlacklistHelper()
        self.utils = Utils()
        self.user_service = UserService()

    @api.doc("Creates A New User.")
    @api.expect(user_register_model, validate=True)
    def post(self):
        """Register new User"""
        validity_result = validate_fields(request.json, user_registration_schema)
        if isinstance(validity_result, User):
            new_user_info = self.user_service.add_user(request.json)
            new_user_obj: User = convert_to_model_obj_from_json(new_user_info, User)
            res = user_schema.dump(new_user_obj)
            return {
                "status": "success",
                "res": res,
                "message": "ok",
            }, Status.HTTP_201_CREATED
        return validity_result


@api.route("/auth/login")
class UserLogin(Resource):
    """docstring for UserLogin."""

    def __init__(self, arg):
        super(UserLogin, self).__init__(arg)
        self.jwt_service = JWTService()
        self.utils = Utils()
        self.user_service = UserService()

    @api.doc("Logs a user in the system")
    @api.expect(user_login_model, validate=True)
    def post(self):
        """User login API"""
        email, password = request.json["email"], request.json["password"]

        request.json["password"] = self.jwt_service.hash_password(password)

        user = self.user_service.login(email)
        if user:
            pass_match = self.jwt_service.check_password(user["password"], password)
        else:
            pass_match = None

        if pass_match:
            del user["password"]
            user["tokens"] = {
                "access": create_access_token(identity=email),
                "refresh": create_refresh_token(identity=email),
            }
            self.user_service.save_tokens(user["tokens"])
            message, status_code = "Login successful.", 200
        else:
            user = []
            message, status_code = "Email or Password is wrong.", 401

        return {"status": "success", "res": user, "message": message}, status_code


@api.route("/logout")
class UserLogout(Resource):
    """docstring for UserLogout."""

    def __init__(self, arg):
        super(UserLogout, self).__init__()
        self.blacklist = BlacklistHelper()

    @api.doc("Logs out the User from the system")
    @jwt_required
    def post(self):
        """User logout"""
        current_user = get_jwt_identity()
        code, msg = self.blacklist.revoke_token(current_user)

        return {"status": "success", "msg": msg}, code


@api.route("/refresh/token")
class TokenRefresh(Resource):
    """docstring for TokenRefresh."""

    def __init__(self, args):
        super(TokenRefresh, self).__init__()

    @api.doc("Gets a refresh token for the user")
    @jwt_refresh_token_required
    def post(self):
        """Refresh token - In Progress"""
        current_user = get_jwt_identity()
        access_token = create_access_token(identity=current_user)

        self.user_service.save_tokens(access_token)

        return {"status": "success", "access_token": access_token}, 200
