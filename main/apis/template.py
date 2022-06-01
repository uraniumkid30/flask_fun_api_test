from attr import validate
from flask_restx import Namespace, Resource, fields
from flask import request
from flask_jwt_extended import jwt_required

from utilities.utils import Utils
from main.services.template_service import TemplateService
from main.api_namespaces.template import api, template_model, update_template_model


@api.route("/template")
class NewTemplate(Resource):
    """docstring for NewTemplate."""

    def __init__(self, arg):
        super(NewTemplate, self).__init__(arg)
        self.utils = Utils()
        self.template_service = TemplateService()

    @jwt_required
    @api.expect(template_model, validate=True)
    def post(self):
        """Save new template object into database"""

        res, msg, code = self.template_service.add(request.json)

        return {
            "status": self.utils.http_status(code),
            "res": res,
            "message": msg,
        }, code

    @jwt_required
    @api.doc(parser=None)
    def get(self):
        """Get list of templates"""
        templates = self.template_service.template_list()
        return {"status": "success", "res": templates}, 200


@api.route("/template/<string:template_id>")
class Template(Resource):
    """docstring for Template."""

    def __init__(self, arg):
        super(Template, self).__init__(arg)
        self.template_service = TemplateService()

    # @jwt_required
    @api.expect(update_template_model)
    def put(self, template_id):
        """Update template based on template_id. 5e86d84da011b26c2082e0c9"""
        if not template_id:
            api.abort(400, "template_id is missing.", status="error")

        status, obj, msg, code = self.template_service.update_template(
            template_id, request.json
        )

        return {"status": status, "data": obj, "message": msg}, code

    @jwt_required
    def get(self, template_id):
        """Get template object based on template_id"""
        template = self.template_service.get_template(template_id)

        return {"status": "success", "res": template}, 200

    @jwt_required
    def delete(self, template_id):
        """Delete a template object based on ID."""
        if not template_id:
            api.abort(400, f"template_id is required.", status="error")

        res, msg = self.template_service.delete_template(template_id)

        if res:
            return {"status": "success", "data": res, "message": msg}, 200
        else:
            return api.abort(400, msg, status="error")
