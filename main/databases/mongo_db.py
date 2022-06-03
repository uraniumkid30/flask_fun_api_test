from main.databases.db_abstraction import Nosql

import sys
from functools import wraps
from utilities import utils
from pymongo import MongoClient
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from flask import current_app as app
from utilities.utils import Singleton
from typing import Tuple, Union, Optional, List


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
            if collection not in self.collection_names:
                try:
                    self.DB_LOG.info(f"About to create collection {collection}")
                    self.client.db.create_collection(collection)
                except Exception as err:  # pymongo.errors.OperationFailure
                    self.DB_LOG.error(f"Error :: {err}")
                else:
                    self.DB_LOG.info(f"Collection {collection} created")

        else:
            self.DB_LOG.info(f"Bad collection name {collection}")
        result = function(*args, **kwargs)
        return result

    return wrapper

@Singleton
class MongoDB(Nosql):
    #__metaclass__ = Singleton
    ALLOWED_CLIENT_UPDATE = 1
    CURRENT_CLIENT_UPDATE = 0
    ENGINE_NAME = "MongoDB"
    LOGGER_NAME = "mongodb"

    def __init__(self):
        super().__init__()
        self.utils = utils.Utils()
        self.connect()
        self.test_database_client_connection()

    def get_database_engine(self):
        return PyMongo #MongoClient

    def database_engine_config(self):
        if not app.config["MONGO_URI"]:
            dbname = app.config["MONGO_DBNAME"]
            username = app.config["MONGO_USERNAME"]
            password = app.config["MONGO_PASSWORD"]
            host = app.config["MONGO_HOSTNAME"]
            mongo_uri = f"mongodb://{username}:{password}@{host}:27017/{dbname}"
            app.config["MONGO_URI"] = mongo_uri
        else:
            mongo_uri = app.config["MONGO_URI"]

    @property
    def client(self):
        return self._CLIENT

    @client.setter
    def client(self, database_engine=None):
        if self.CURRENT_CLIENT_UPDATE < self.ALLOWED_CLIENT_UPDATE:
            try:
                self.database_engine_config()
                # PyMongo(app, uri=app.config["MONGO_URI"])
                db_client = self.DATABASE_ENGINE(app,app.config["MONGO_URI"])
            except Exception as err:
                self.DB_LOG.error(
                    f"{self.ENGINE_NAME} Connection Error check ./.env for details. Error: {err}"
                )
                sys.exit(1)
            else:
                self._CLIENT = db_client

                self.DB_LOG.info(f"Database connected successfully")
                self.CURRENT_CLIENT_UPDATE += 1
        else:
            self.DB_LOG.warning("Cannot set client")

    def connect(self):
        self.client = self.DATABASE_ENGINE

    def test_database_client_connection(self):
        try:
            self.get_database_engine_info()
            self.get_database_client_info()
        except Exception as e:
            self.DB_LOG.error(f"{self.ENGINE_NAME} client Tests failed. Error: {e}")
            sys.exit(1)
        else:
            self.DB_LOG.info(f"{self.ENGINE_NAME} client test passed successfully")

    def get_database_client_info(self) -> str:
        db_list = self.client.cx.list_database_names()
        self.collection_names = self.client.db.list_collection_names()
        data = f"Databases: {','.join(db_list)}. Collections: {','.join(self.collection_names)}"
        self.DB_LOG.info(data)
        return data

    def get_database_engine_info(self) -> str:
        server_info: dict = self.client.cx.server_info()
        version: str = server_info.get("version", "")
        return f"{version}"

    @get_or_create_collection
    def find_record(
        self,
        collection: str = "",
        condition: dict = {},
    ) -> Union[bool, list]:
        self.DB_LOG.info(f"Find {condition} from {collection} collection.")
        if condition:
            try:
                data = self.client.db[collection].find(condition)
            except Exception as e:
                self.DB_LOG.error(f"{e}")
                data = f"No collection found with {collection}"
            else:
                self.DB_LOG.info(f"Found {condition} from {collection} collection.")
        else:
            data = self.client.db[collection].find()
            self.DB_LOG.info(f"Found {collection} collection.")

        results: Union[bool, list] = self.id_to_str(data)

        return results

    @get_or_create_collection
    def find_record_by_id(
        self,
        collection: str = "",
        _id: str = "",
    ) -> Union[List[dict], dict, None]:
        results = None
        self.DB_LOG.info(f"Find by _id {_id} from {collection}")
        if _id:
            try:
                query = {"_id": ObjectId(_id)}
                results = self.client.db[collection].find_one(query)
                results["_id"] = str(results["_id"])
            except Exception as e:
                self.DB_LOG.error(f"Something went wrong. Error: {e}")
            else:
                self.DB_LOG.info(f"Found by _id {_id} from {collection}")
        else:
            results = self.client.db[collection].find()

        return results

    @get_or_create_collection
    def insert_record_into_collection(
        self,
        collection: str = "",
        payload: dict = {},
    ) -> dict:
        """
        Takes data obj as input and returns the _id after saving
        """
        self.DB_LOG.info(f"Insert {payload} into {collection}")
        _id = self.client.db[collection].insert_one(payload).inserted_id
        result = self.find_record_by_id(collection, _id)

        if result:
            result["_id"] = str(result["_id"])

        return result

    @get_or_create_collection
    def update_record_by_id(
        self,
        collection: str,
        _id: str = "",
        payload: dict = {},
    ) -> Tuple[bool, str]:
        """
        Updates the object based on _id
        Output: (error, message or obj)
        """
        obj = self.remove_empty_keys(payload)
        verdict = False
        self.DB_LOG.info(f"Put data {payload} into {collection} by {_id}")
        if _id:
            try:
                query = {"_id": ObjectId(_id)}
                inserted_id = self.client.db[collection].update_one(query, payload)
                verdict = True
                message = self.find_record_by_id(collection, _id)
            except Exception as e:
                self.DB_LOG.error(f"ID is not valid. err: {e}")
                message = f"{e}"
        else:
            message = "_id is required"
        return verdict, message

    @get_or_create_collection
    def delete_record_by_id(
        self,
        collection: str,
        _id: str,
    ) -> Tuple[bool, str]:
        try:
            query: dict = {"_id": ObjectId(_id)}
            self.DB_LOG.info(f"About to Delete from {collection} by _id {_id}")
            self.client.db[collection].delete_one(query)
            self.DB_LOG.info(f"Deleted {query} Successfully")
            verdict: bool = True
            message: str = "Delete Successfully"
        except Exception as err:
            self.DB_LOG.error(f"Document not deleted using {query}. error: {err}")
            verdict: bool = False
            message: str = f"Error in Deleting document using {query}"
        finally:
            return (verdict, message)

    def id_to_str(self, data: Union[str, list]) -> Union[bool, list]:
        results = []
        if type(data) == str:
            return False

        for document in data:
            document["_id"] = str(document["_id"])
            results.append(document)

        return results
