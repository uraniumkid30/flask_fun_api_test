import os
import logging as log
from logging.config import dictConfig

import coloredlogs
from flask import Flask
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    get_jwt_identity,
    jwt_required,
)

# local imports
from configuration.directories import create_neccessary_directories, LOGS_DIR
from configuration.settings import app_config
from configuration.logging import (
    get_log_config,
    DEFAULT_COLORED_LOGS_LEVEL_STYLES,
    DEFAULT_COLORED_LOGS_FIELD_STYLES,
)
from .db import MongoDB


def create_app(config_name):
    create_neccessary_directories()
    config_name = "dev" if not config_name else config_name
    dictConfig(get_log_config(LOGS_DIR))
    coloredlogs.DEFAULT_LEVEL_STYLES = DEFAULT_COLORED_LOGS_LEVEL_STYLES
    coloredlogs.DEFAULT_FIELD_STYLES = DEFAULT_COLORED_LOGS_FIELD_STYLES
    coloredlogs.install(level="DEBUG")
    app = Flask(__name__, instance_relative_config=True)
    # app.config.from_object("configuration.settings.DevelopmentConfig")
    app.config.from_object(app_config[config_name])
    # app.config.from_pyfile("config.py")

    app.config["log"] = log

    cors = CORS(app)
    app.config["jwt"] = JWTManager(app)
    app.config["flask_bcrypt"] = Bcrypt(app)
    jwt = app.config["jwt"]

    # Swagger UI config
    app.config.SWAGGER_UI_JSONEDITOR = True
    app.config.SWAGGER_UI_DOC_EXPANSION = "none"

    with app.app_context():
        db = MongoDB()

    @jwt.token_in_blacklist_loader
    def check_if_token_in_blacklist(decrypted_token):
        blacklist = set()
        jti = decrypted_token["jti"]
        return jti in blacklist

    # @app.route("/")
    # def hello_world():
    #     # render home template
    #     # logger = logging.getLogger("apps")
    #     return "Hello, World!"

    # ensure the instance folder exists
    try:
        app.instance_path = "configuration"
        os.makedirs(app.instance_path)
    except OSError:
        pass

    return app
