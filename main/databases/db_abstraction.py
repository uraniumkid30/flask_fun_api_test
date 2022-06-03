import logging
import coloredlogs
from utilities import utils
from abc import ABC, ABCMeta, abstractmethod
from typing import Tuple, Union, Optional, List


class Nosql(metaclass=ABCMeta):
    ENGINE_NAME = "Nosql"
    LOGGER_NAME = ""

    def __init__(
        self,
    ):
        self.set_up_logger()
        self.DATABASE_ENGINE = self.get_database_engine()
        self._CLIENT = None
        self.utils = utils.Utils()

    @abstractmethod
    def get_database_engine(self):
        pass

    @abstractmethod
    def database_engine_config(self):
        pass

    @property
    @abstractmethod
    def client(self):
        pass

    @client.setter
    @abstractmethod
    def client(self, database_engine=None):
        pass

    def set_up_logger(
        self,
    ):
        self.DB_LOG = logging.getLogger(self.LOGGER_NAME)
        coloredlogs.install(logger=self.DB_LOG)

    @abstractmethod
    def connect(self):
        # implement connection to db
        pass

    @abstractmethod
    def test_database_client_connection(self):
        # implement in db
        pass

    @abstractmethod
    def get_database_client_info(self) -> str:
        # implement in db
        pass

    @abstractmethod
    def get_database_engine_info(self) -> str:
        # implement in db
        pass

    @abstractmethod
    def find_record(
        self,
        collection: str = "",
        condition: dict = {},
    ) -> Union[bool, list]:
        # implement in db
        pass

    @abstractmethod
    def find_record_by_id(
        self,
        collection: str = "",
        _id: str = "",
    ) -> Union[List[dict], dict, None]:
        arguments = {
            "collection": collection,
            "field": "_id",
            "field_value": _id,
            "condition": None,
        }
        return self.find_record(**arguments)

    @abstractmethod
    def insert_record_into_collection(
        self,
        collection: str = "",
        payload: dict = {},
    ) -> dict:
        """
        Takes data obj as input and returns the _id after saving
        """
        # implement insert
        pass

    @abstractmethod
    def update_record_by_id(
        self,
        collection: str,
        _id: str = "",
        payload: dict = {},
    ) -> Tuple[bool, str]:
        """
        Updates the object based on _id
        Output: (error, message or payload)
        """
        # implement update
        pass

    @abstractmethod
    def delete_record_by_id(
        self,
        collection: str,
        _id: str,
    ) -> Tuple[bool, str]:
        # implement delete
        pass

    @staticmethod
    def remove_empty_keys(self, payload: dict):
        """
        Input: Take an object with key, values
        Ouput: Returns the object by removing keys which has no values
        """
        updated_payload = {}
        updated_payload["$set"] = {k: v for k, v in payload["$set"].items() if v != ""}
        return updated_payload

    def close_client_connection(
        self,
    ):
        """
        Input: Take an object with key, values
        Ouput: Returns the object by removing keys which has no values
        """
        self.client.close()

    def __str__(self):
        return f"{self.ENGINE_NAME}: {self.get_database_engine_info()} - {self.get_database_client_info()}"
