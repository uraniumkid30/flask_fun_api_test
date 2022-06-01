from flask import current_app as app

from utilities.utils import Utils
from main.db import MongoDB
from main.services.blacklist_helpers import BlacklistHelper


class UserService:
    """doc string for UserService"""

    def __init__(self):
        super(UserService, self).__init__()
        self.collection = "users"
        self.blacklist = BlacklistHelper()
        self.utils = Utils()
        self.mongo = MongoDB()
        self.log = app.config["log"]

    def user_list(self):
        users = self.mongo.find(self.collection)
        if users:
            for user in users:
                del user["password"]
            self.log.info(f"Found {len(users)} users")
            return users
        else:
            self.log.warning(f"Found 0 users")
            return []

    def add_user(self, user_obj):
        """user_obj - user object"""
        user = self.mongo.find(
            collection=self.collection, condition={"email": user_obj["email"]}
        )
        if not user:
            self.log.info(f"About to add user with data {user_obj}")
            return self.mongo.save(self.collection, user_obj)
        else:
            msg = f'User with {user_obj["email"]} already existed.'
            self.log.warning(msg)
            return msg

    def get_user(self, user_id):
        """Get User profile by id. ex _id:"""
        res = self.mongo.find_by_id(collection=self.collection, _id=user_id)
        if res:
            del res["password"]
            self.log.info(f"Found User {user_id}")
            return ("success", res, "ok", 200)
        else:
            self.log.error(f"Couldnt Find User {user_id}")
            return ("error", [], "Something went wrong.", 400)

    def update_user(self, _id, user_obj):
        user = self.mongo.find(
            collection=self.collection, condition={"email": user_obj["email"]}
        )
        if not user:
            query = {"$set": user_obj}
            self.log.info(f"About to perform User Update with {_id, user_obj}")
            res, res_obj = self.mongo.update(self.collection, _id, query)
            if res:
                del res_obj["password"]
                self.log.info(f"Update Successful")
                return ("success", res_obj, "ok", 200)
            else:
                self.log.error(f"Update Failed")
                return ("error", "", "Something went wrong.", 400)
        else:
            self.log.info(
                f"Update unsuccessful because email {user_obj['email']} already exists."
            )
            return (
                "error",
                "",
                f'Email {user_obj["email"]} address already in use.',
                400,
            )

    def delete_user(self, user_id):
        self.log.info(f"About to delete User {user_id}")
        return self.mongo.delete(collection=self.collection, _id=user_id)

    def login(self, email):
        """email as input"""
        user = self.mongo.find(collection=self.collection, condition={"email": email})
        if user:
            user = user[0]
            self.log.info(f"User {email} has logged in")
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
