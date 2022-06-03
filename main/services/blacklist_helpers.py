from datetime import datetime

from flask_jwt_extended import decode_token

from flask import current_app as app
from main.databases.mongo_db import MongoDB
from main.databases.db_abstraction import Nosql
from utilities.utils import Status


class BlacklistHelper:
    """Helper file to handle the blacklist tokens."""

    def __init__(self):
        super(BlacklistHelper, self).__init__()
        self.collection = "blacklist"
        self.db_client: app.config["sql_type"] = app.config["db_engine_obj"]
        # self.db_client: Nosql = MongoDB()

    def add_token_to_database(self, encoded_access_token, identity_claim):
        """
        Adds a token to the database. It is not revoked when it is aded.
        :param identity_claim: identity_claim is user email here which we set in api/user.py:UserLogin:post
        """
        decoded_token = decode_token(encoded_access_token)
        jti = decoded_token["jti"]
        token_type = decoded_token["type"]
        user_identity = decoded_token[identity_claim]
        expires = self._epoch_utc_to_datetime(decoded_token["exp"])

        revoked = False

        token_data = {
            "jti": jti,
            "token_type": token_type,
            "user_identity": user_identity,
            "expires": expires,
            "revoked": revoked,
        }

        return self.db_client.insert_record_into_collection(self.collection, token_data)

    def revoke_token(self, user):
        condition = {"user_identity": user}
        token = self.db_client.find_record(self.collection, condition)
        if token:
            # token.revoked = True
            # make token.revoked = False and save it into database
            for t in token:
                del t["expires"]
            return (Status.HTTP_200_OK, "Successfully logged out.")
        else:
            return (Status.HTTP_404_NOT_FOUND, "Token not found.")

    def _epoch_utc_to_datetime(self, epoch_utc):
        """
        Helper function for converting epoch timestamps (as stored in JWTs) into
        python datetime objects (which are easier to use with sqlalchemy).
        """
        return datetime.fromtimestamp(epoch_utc)
