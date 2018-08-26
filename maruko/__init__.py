import logging
from os import path
from typing import Any

import none

from . import db, scheduler
from .log import logger


def init(config_object: Any) -> none.NoneBot:
    if config_object and \
            hasattr(config_object, 'APSCHEDULER_CONFIG') and \
            hasattr(config_object, 'DATABASE_URL'):
        # configure none.scheduler
        if 'apscheduler.jobstores.default' not in \
                config_object.APSCHEDULER_CONFIG:
            # use config_object.DATABASE_URL as default job store
            config_object.APSCHEDULER_CONFIG[
                'apscheduler.jobstores.default'] = {
                'type': 'sqlalchemy',
                'url': config_object.DATABASE_URL,
                'tablename': db.make_table_name('core', 'apscheduler_jobs')
            }

    none.init(config_object)
    bot = none.get_bot()

    if bot.config.DEBUG:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    db.init()
    none.load_builtin_plugins()
    none.load_plugins(path.join(path.dirname(__file__), 'plugins'),
                      'maruko.plugins')
    db.create_all()

    return bot
