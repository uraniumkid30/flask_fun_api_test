from flask import current_app as app

from utilities.utils import Utils
from main.services.jwt_service import JWTService
from main.databases.mongo_db import MongoDB
from main.databases.db_abstraction import Nosql
from utilities.utils import Status
from main.services.blacklist_helpers import BlacklistHelper


class UserService:
    """doc string for UserService"""

    def __init__(self):
        super(UserService, self).__init__()
        self.collection = "users"
        self.blacklist = BlacklistHelper()
        self.utils = Utils()
        self.jwt = JWTService()
        self.db_client: app.config["sql_type"] = app.config["db_engine_obj"]
        # self.db_client: Nosql = MongoDB()
        self.log = app.config["log"]

    def user_list(self):
        users = self.db_client.find_record(self.collection)
        if users:
            self.log.info(f"Found {len(users)} users")
            return users
        else:
            self.log.warning(f"Found 0 users")
            return []

    def add_user(self, user_obj):
        """user_obj - user object"""
        user = self.db_client.find_record(
            collection=self.collection, condition={"email": user_obj["email"]}
        )
        if not user:
            hashed_password = self.jwt.hash_password(user_obj["password"])
            password = user_obj["password"]
            user_obj["password"] = hashed_password
            self.log.info(f"About to add user with data {user_obj}")
            new_user_obj = self.db_client.insert_record_into_collection(
                self.collection, user_obj
            )
            new_user_obj["password"] = password
            return new_user_obj
        else:
            msg = f'User with {user_obj["email"]} already existed.'
            self.log.warning(msg)
            return msg

    def get_user(self, user_id):
        """Get User profile by id. ex _id:"""
        res = self.db_client.find_record_by_id(collection=self.collection, _id=user_id)
        if res:
            del res["password"]
            self.log.info(f"Found User {user_id}")
            return ("success", res, "ok", Status.HTTP_200_OK)
        else:
            self.log.error(f"Couldnt Find User {user_id}")
            return ("error", [], "Something went wrong.", Status.HTTP_400_BAD_REQUEST)

    def update_user(self, _id, user_obj):
        user = self.db_client.find_record(
            collection=self.collection, condition={"email": user_obj["email"]}
        )
        if not user:
            query = {"$set": user_obj}
            self.log.info(f"About to perform User Update with {_id, user_obj}")
            res, res_obj = self.db_client.update_record_by_id(
                self.collection, _id, query
            )
            if res:
                del res_obj["password"]
                self.log.info(f"Update Successful")
                return ("success", res_obj, "ok", Status.HTTP_200_OK)
            else:
                self.log.error(f"Update Failed")
                return (
                    "error",
                    "",
                    "Something went wrong.",
                    Status.HTTP_400_BAD_REQUEST,
                )
        else:
            self.log.info(
                f"Update unsuccessful because email {user_obj['email']} already exists."
            )
            return (
                "error",
                "",
                f'Email {user_obj["email"]} address already in use.',
                Status.HTTP_400_BAD_REQUEST,
            )

    def delete_user(self, user_id):
        self.log.info(f"About to delete User {user_id}")
        return self.db_client.delete_record_by_id(
            collection=self.collection, _id=user_id
        )

    def login(self, email):
        """email as input"""
        user = self.db_client.find_record(
            collection=self.collection, condition={"email": email}
        )
        if user:
            user = user[0]
            self.log.info(f"Found User with email {email} to logged in")
            return user
        else:
            return None

    def save_tokens(self, user_tokens):
        self.blacklist.add_token_to_database(
            user_tokens["access"], app.config["JWT_IDENTITY_CLAIM"]
        )
        self.blacklist.add_token_to_database(
            user_tokens["refresh"], app.config["JWT_IDENTITY_CLAIM"]
        )
