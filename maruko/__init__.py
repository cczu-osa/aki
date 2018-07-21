import logging
from os import path
from typing import Any

import none
from quart import Quart

from . import db
from .log import logger


def init(config_object: Any) -> Quart:
    none.init(config_object)
    bot_ = none.get_bot()

    if bot_.config.DEBUG:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    db.init()
    none.load_builtin_plugins()
    none.load_plugins(path.join(path.dirname(__file__), 'plugins'),
                      'maruko.plugins')
    db.create_all()

    return bot_.asgi
