import os
import json
import logging
import requests

debug = eval(os.environ.get("DEBUG", "False"))


class HTTPSlackHandler(logging.Handler):
    def emit(self, record):
        log_entry = self.format(record)
        json_text = json.dumps({"text": log_entry})
        url = "https://hooks.slack.com/services/<org_id>/<api_key>"
        return requests.post(
            url, json_text, headers={"Content-type": "application/json"}
        ).content


def get_log_config(LOGS_DIR):
    LOG_CONFIG = {
        "version": 1,
        "disable_existing_loggers": True,
        # "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "[%(asctime)s] %(levelname)s in %(module)s: %(message)s",
            },
            "access": {
                "format": "%(message)s",
            },
            "standard": {
                "format": "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s - %(pathname)s",
                "datefmt": "%d/%b/%Y %H:%M:%S",
            },
        },
        "handlers": {
            "default": {
                "level": "DEBUG",
                "class": "logging.handlers.RotatingFileHandler",
                "filename": os.path.join(LOGS_DIR, "default.log"),
                "formatter": "standard",
                "maxBytes": 104857600,
            },
            "mongodb": {
                "level": "DEBUG",
                "class": "logging.handlers.RotatingFileHandler",
                "filename": os.path.join(LOGS_DIR, "mongodb.log"),
                "formatter": "standard",
                "maxBytes": 104857600,
            },
            "handler_error": {
                "level": "ERROR",
                "class": "logging.FileHandler",
                "filename": os.path.join(LOGS_DIR, "error.log"),
            },
            "daily_error": {
                "level": "ERROR",
                "class": "logging.handlers.TimedRotatingFileHandler",
                "filename": os.path.join(LOGS_DIR, "daily_error.log"),
                "when": "midnight",
                "backupCount": 7,
                "formatter": "standard",
            },
            "console": {
                "level": "INFO",
                "class": "logging.StreamHandler",
                "formatter": "default",
                "stream": "ext://sys.stdout",
            },
            "email": {
                "class": "logging.handlers.SMTPHandler",
                "formatter": "default",
                "level": "ERROR",
                "mailhost": ("smtp.example.com", 587),
                "fromaddr": "devops@example.com",
                "toaddrs": ["receiver@example.com", "receiver2@example.com"],
                "subject": "Error Logs",
                "credentials": ("username", "password"),
            },
            # "slack": {
            #     "class": "app.HTTPSlackHandler",
            #     "formatter": "default",
            #     "level": "ERROR",
            # },
            "gunicorn_error_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "formatter": "default",
                "filename": "/var/log/gunicorn.error.log",
                "maxBytes": 10000,
                "backupCount": 10,
                "delay": "True",
            },
            "gunicorn_access_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "formatter": "access",
                "filename": "/var/log/gunicorn.access.log",
                "maxBytes": 10000,
                "backupCount": 10,
                "delay": "True",
            },
        },
        "loggers": {
            "gunicorn.error": {
                "handlers": ["console"]
                if debug
                else ["console", "gunicorn_error_file"],
                "level": "INFO",
                "propagate": False,
            },
            "flask": {
                "handlers": ["handler_error"],
                "level": "ERROR",
                "propagate": True,
            },
            "mongodb": {
                "handlers": [
                    "mongodb",
                    "default",
                    "console",
                ],
                "level": "DEBUG",
                "propagate": True,
            },
            "gunicorn.access": {
                "handlers": ["console"]
                if debug
                else ["console", "gunicorn_access_file"],
                "level": "INFO",
                "propagate": False,
            },
            # "": {
            #     "handlers": ["default"],
            #     "level": "INFO",
            #     "propagate": True,
            # },
        },
        "root": {
            "level": "DEBUG" if debug else "INFO",
            "handlers": ["console"] if debug else ["console", "default"],
        },
    }
    return LOG_CONFIG


DEFAULT_COLORED_LOGS_LEVEL_STYLES = {
    "info": {},
    "notice": {"color": "magenta"},
    "verbose": {"color": "green"},
    "success": {"color": "green", "bold": True},
    "spam": {"color": "cyan"},
    "critical": {"color": "red", "bold": True},
    "error": {"color": "red"},
    "debug": {"color": "blue"},
    "warning": {"color": "yellow"},
}

DEFAULT_COLORED_LOGS_FIELD_STYLES = {
    "hostname": {"color": "cyan"},  # magenta
    "programname": {"color": "cyan"},
    "name": {"color": "blue"},
    "levelname": {"color": "black", "bold": True},
    "asctime": {"color": "green"},
}
