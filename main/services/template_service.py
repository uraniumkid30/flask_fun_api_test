from bson.objectid import ObjectId

from main.db import MongoDB


class TemplateService:
    """doc string for templateService"""

    def __init__(self):
        super(TemplateService, self).__init__()
        self.collection = "templates"
        self.mongo = MongoDB()

    def add(self, template_obj):
        template = self.mongo.find(
            self.collection, {"template_name": template_obj["template_name"]}
        )
        if not template:
            return (
                self.mongo.save(self.collection, template_obj),
                "Successfully created.",
                200,
            )
        else:
            return ("ok", "template already added to the library.", 400)

    def template_list(self):
        return self.mongo.find(self.collection)

    def delete_template(self, template_id):
        return self.mongo.delete(self.collection, template_id)

    def update_template(self, template_id, template_obj):
        condition = {"$set": template_obj}
        res, update_count = self.mongo.update(self.collection, template_id, condition)

        if res:
            return ("success", res, "ok", 200)
        return ("error", "", "Something went wrong.", 400)

    def get_template(self, template_id):
        condition = {"_id": ObjectId(template_id)}
        return self.mongo.find(self.collection, condition)
