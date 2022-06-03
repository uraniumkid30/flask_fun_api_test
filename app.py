import os, sys
from flask import Flask
import pathlib
from flask_restx import Api, Resource, fields

# from werkzeug.middleware.proxy_fix import ProxyFix

# import coloredlogs, logging as log
# coloredlogs.install()

from main.apis.user import api as User
from main.apis.template import api as Template
from main.apis.auth import api as Auth

from main import create_app

# from flask_pymongo import PyMongo

# Init app
app = Flask(__name__)

authorizations = {"token": {"type": "apiKey", "in": "header", "name": "Authorization"}}

config_name = os.getenv("FLASK_CONFIG")
app = create_app(config_name)
VERSION = "v1"

api = Api(
    app,
    authorizations=authorizations,
    version="1.0",
    title="API docs",
    description="A simple REST API with JWT authentication.",
    doc="/docs",
)

app.config["jwt"]._set_error_handler_callbacks(api)
app.config["ROOT_DIR"] = pathlib.Path(__file__).parent.absolute()

# Endpoints
api.add_namespace(Auth, path=f"/")
api.add_namespace(User, path=f"/")
api.add_namespace(Template, path=f"/")

# Run Server
if __name__ == "__main__":
    app.run()
