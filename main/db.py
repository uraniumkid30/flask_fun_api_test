import os
import sys
import pymongo
import logging
import coloredlogs
from functools import wraps
from utilities import utils
from pymongo import MongoClient
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from flask import current_app as app


def get_or_create_collection(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        self = args[0]
        if len(args) > 1:
            collection = args[1]
        else:
            collection = kwargs.get("collection")
        log = app.config["log"]
        if collection:
            if collection in self.collection_names:
                try:
                    self.db_log.info(f"About to create collection{collection}")
                    self.mongo_db.db.create_collection(collection)
                except Exception as err:  # pymongo.errors.OperationFailure
                    self.db_log.error(f"Error :: {err}")
                else:
                    self.db_log.info(f"Collection {collection} created")

        else:
            self.db_log.info(f"Bad collection name {collection}")
        result = function(*args, **kwargs)
        return result

    return wrapper


class MongoDB:
    def __init__(self):
        self.log = app.config["log"]
        self.db_log = logging.getLogger("mongodb")
        coloredlogs.install(logger=self.db_log)
        self.utils = utils.Utils()
        self.db_config()
        self.connect()

    def connect(self):
        self.mongo = PyMongo(app, uri=app.config["MONGO_URI"])
        self.mongo_db = MongoClient(app.config["MONGO_URI"])
        self.collection_names = self.mongo_db.db.list_collection_names()

    def db_config(self):
        if not app.config["MONGO_URI"]:
            dbname = app.config["MONGO_DBNAME"]
            username = app.config["MONGO_USERNAME"]
            password = app.config["MONGO_PASSWORD"]
            host = app.config["MONGO_HOSTNAME"]
            mongo_uri = f"mongodb://{username}:{password}@{host}:27017/{dbname}"
            app.config["MONGO_URI"] = mongo_uri
        else:
            mongo_uri = app.config["MONGO_URI"]

        try:
            client = MongoClient(
                mongo_uri,
            )
            client.server_info()
        except Exception as e:
            self.db_log.error(
                f"MongoDB Connection Error check ./.env for details. Error: {e}"
            )
            sys.exit(1)
        else:
            self.db_log.info(f"Database connected successfully")
        finally:
            client.close()

    @get_or_create_collection
    def find(self, collection="", condition=None):
        self.log.info(f"Find {condition} from {collection} collection.")
        if condition:
            try:
                data = self.mongo.db[collection].find(condition)
            except Exception as e:
                self.db_log.error(f"{e}")
                data = f"No collection found with {collection}"
            else:
                self.db_log.info(f"Found {condition} from {collection} collection.")
        else:
            data = self.mongo.db[collection].find()
            self.db_log.info(f"Found {collection} collection.")

        results = self.mongo_id_to_str(data)

        return results

    @get_or_create_collection
    def find_by_id(self, collection="", _id=""):
        results = None
        self.db_log.info(f"Find by _id {_id} from {collection}")
        if _id:
            try:
                results = self.mongo.db[collection].find_one({"_id": ObjectId(_id)})
                results["_id"] = str(results["_id"])
            except Exception as e:
                self.db_log.error(f"Something went wrong. Error: {e}")
            else:
                self.db_log.info(f"Found by _id {_id} from {collection}")
        else:
            results = self.mongo.db[collection].find()

        return results

    @get_or_create_collection
    def save(self, collection="", obj=None):
        """
        Takes data obj as input and returns the _id after saving
        """
        # print(self.mongo.list_databases())
        self.db_log.info(f"Insert {obj} into {collection}")
        # print(self.mongo_db.list_database_names())
        # print(self.mongo_db.list_databases())
        _id = self.mongo.db[collection].insert_one(obj).inserted_id
        result = self.find_by_id(collection, _id)

        if result:
            result["_id"] = str(result["_id"])

        return result

    @get_or_create_collection
    def update(self, collection="", _id="", obj=None):
        """
        Updates the object based on _id
        Output: (error, message or obj)
        """
        obj = self.remove_empty_keys(obj)
        self.db_log.info(f"Update {obj} into {collection} by {_id}")
        if _id:
            try:
                inserted_id = self.mongo.db[collection].update_one(
                    {"_id": ObjectId(_id)}, obj
                )
                result = (True, self.find_by_id(collection, _id))
            except Exception as e:
                self.db_log.error(f"ID is not valid. err: {e}")
                result = (False, f"{e}")

            return result
        else:
            return (False, "_id is required")

    @get_or_create_collection
    def delete(self, collection="", _id=""):
        self.db_log.info(f"Delete from {collection} by {_id}")
        try:
            self.mongo.db[collection].delete_one({"_id": ObjectId(_id)})
            return (True, "Delete Successfully")
        except Exception as e:
            self.db_log.error(f"Document not deleted using {_id}. err: {e}")
            return (False, f"Error in Deleting document using {_id}")

    def remove_empty_keys(self, obj):
        """
        Input: Take an object with key, values
        Ouput: Returns the object by removing keys which has no values
        """
        new_obj = {}
        new_obj["$set"] = {k: v for k, v in obj["$set"].items() if v != ""}
        return new_obj

    def mongo_id_to_str(self, data):
        results = []
        if type(data) == str:
            return False

        for document in data:
            document["_id"] = str(document["_id"])
            results.append(document)

        return results
