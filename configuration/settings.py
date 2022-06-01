import os
import secrets
from datetime import timedelta
from dotenv import load_dotenv


class Config(object):
    load_dotenv("../.env")
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    API_PREFIX = "/api"
    SECRET_KEY = secrets.token_hex(16)  # "57e19ea558d4967a552d03deece34a70"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CORS_HEADERS = "Content-Type"
    JWT_SECRET_KEY = secrets.token_hex(10)  # "9MZbGqQHaC47SSKyKaTK"
    JWT_BLACKLIST_ENABLED = True
    JWT_BLACKLIST_TOKEN_CHECKS = ["access", "refresh"]
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=10)
    MONGO_DBNAME = os.environ.get("MONGODB_DATABASENAME")
    MONGO_HOSTNAME = os.environ.get("MONGODB_HOSTNAME")
    MONGO_USERNAME = os.environ.get("MONGODB_USERNAME")
    MONGO_PASSWORD = os.environ.get("MONGODB_PASSWORD")


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
    MONGO_URI = "mongodb://localhost:27017/todo_db"
    # SQLALCHEMY_DATABASE_URI = 'postgresql://db_user:db_password@db-postgres:5432/flask-deploy'
    # CELERY_BROKER = 'pyamqp://rabbit_user:rabbit_password@broker-rabbitmq//'
    # CELERY_RESULT_BACKEND = 'rpc://rabbit_user:rabbit_password@broker-rabbitmq//'


class DevelopmentConfig(Config):
    ENV = "development"
    DEVELOPMENT = True
    DEBUG = True
    MONGO_URI = f"mongodb+srv://mongokid:{Config.MONGO_PASSWORD}@flask-db1.2qxth.mongodb.net/flask_test?retryWrites=true&w=majority"
    # SQLALCHEMY_DATABASE_URI = 'postgresql://db_user:db_password@db-postgres:5432/flask-deploy'
    # CELERY_BROKER = 'pyamqp://rabbit_user:rabbit_password@broker-rabbitmq//'
    # CELERY_RESULT_BACKEND = 'rpc://rabbit_user:rabbit_password@broker-rabbitmq//'


SQLALCHEMY_DATABASE_URI = "sqlite:///development_database.db"

app_config = {"dev": DevelopmentConfig, "prod": ProductionConfig}
