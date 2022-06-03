from bson.objectid import ObjectId

from flask import current_app as app
from main.databases.mongo_db import MongoDB
from main.databases.db_abstraction import Nosql
from utilities.utils import Status


class TemplateService:
    """doc string for templateService"""

    def __init__(self):
        super(TemplateService, self).__init__()
        self.collection = "templates"
        self.db_client: app.config["sql_type"] = app.config["db_engine_obj"]
        # self.db_client: Nosql = MongoDB()

    def add(self, template_obj):
        template = self.db_client.find_record(
            self.collection, {"template_name": template_obj["template_name"]}
        )
        if not template:
            return (
                self.db_client.insert_record_into_collection(
                    self.collection, template_obj
                ),
                "Successfully created.",
                Status.HTTP_200_OK,
            )
        else:
            return (
                "ok",
                "template already added to the library.",
                Status.HTTP_400_BAD_REQUEST,
            )

    def template_list(self):
        return self.db_client.find_record(self.collection)

    def delete_template(self, template_id):
        return self.db_client.delete_record_by_id(self.collection, template_id)

    def update_template(self, template_id, template_obj):
        condition = {"$set": template_obj}
        res, update_count = self.db_client.update_record_by_id(
            self.collection, template_id, condition
        )

        if res:
            return ("success", res, "ok", Status.HTTP_200_OK)
        return ("error", "", "Something went wrong.", Status.HTTP_400_BAD_REQUEST)

    def get_template(self, template_id):
        condition = {"_id": ObjectId(template_id)}
        return self.db_client.find_record(self.collection, condition)
