from flask import current_app as app, jsonify
from utilities.utils import Status

# from app.auth.blacklist_helper import is_token_revoked


class JWTService:
    """doc str"""

    def __init__(self):
        super(JWTService, self).__init__()
        self.__jwt_init()

    def hash_password(self, pass_string):
        return app.config["flask_bcrypt"].generate_password_hash(pass_string)

    def check_password(self, pass_hash, pass_string):
        return app.config["flask_bcrypt"].check_password_hash(pass_hash, pass_string)

    def __jwt_init(self):
        jwt = app.config["jwt"]

        # @jwt.token_in_blacklist_loader
        # def check_if_token_revoked(decrypted_token):
        #     return is_token_revoked(decrypted_token)

        @jwt.expired_token_loader
        def expired_token_callback():
            return (
                jsonify({"msg": "The token has expired", "error": "token_expired"}),
                Status.HTTP_401_UNAUTHORIZED,
            )

        @jwt.invalid_token_loader
        def invalid_token_callback(error):
            return (
                jsonify(
                    {"msg": "Signature verification failed", "error": "invalid_token"}
                ),
                Status.HTTP_401_UNAUTHORIZED,
            )

        @jwt.unauthorized_loader
        def missing_token_callback(error):
            return (
                jsonify(
                    {
                        "msg": "Request does not contain an access token",
                        "error": "authorization_required",
                    }
                ),
                Status.HTTP_401_UNAUTHORIZED,
            )

        @jwt.needs_fresh_token_loader
        def token_not_fresh_callback():
            return (
                jsonify(
                    {"msg": "The token is not fresh", "error": "fresh_token_required"}
                ),
                Status.HTTP_401_UNAUTHORIZED,
            )

        @jwt.revoked_token_loader
        def revoked_token_callback():
            return (
                jsonify(
                    {"msg": "The token has been revoked", "error": "token_revoked"}
                ),
                Status.HTTP_401_UNAUTHORIZED,
            )


# class UserInJWT():
#     def __init__(self, user_obj, args=None):
#         self.user = user_obj
#         self.args = args

#     @jwt.user_claims_loader
#     def add_claims_to_access_token(user):
#         """
#         # Create a function that will be called whenever create_access_token
#         # is used. It will take whatever object is passed into the
#         # create_access_token method, and lets us define what custom claims
#         # should be added to the access token.
#         """
#         return {'roles': user.roles}

#     @jwt.user_identity_loader
#     def user_identity_lookup(user):
#         """
#         # Create a function that will be called whenever create_access_token
#         # is used. It will take whatever object is passed into the
#         # create_access_token method, and lets us define what the identity
#         # of the access token should be.
#         """
#         return user.name
