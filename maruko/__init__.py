from os import path
from typing import Any

import none
from quart import Quart


def init(config_object: Any) -> Quart:
    none.init(config_object)
    none.load_builtin_plugins()
    none.load_plugins(path.join(path.dirname(__file__), 'plugins'),
                      'maruko.plugins')
    return none.get_bot().asgi
