import logging
from os import path
from typing import Any

import nonebot as nb

from . import cache, db, scheduler
from .log import logger


def init(config_object: Any) -> nb.NoneBot:
    if config_object and \
            hasattr(config_object, 'APSCHEDULER_CONFIG') and \
            getattr(config_object, 'DATABASE_URL', None):
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

    nb.init(config_object)
    bot = nb.get_bot()

    if bot.config.DEBUG:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    cache.init()

    db.init()
    nb.load_builtin_plugins()
    nb.load_plugins(path.join(path.dirname(__file__), 'plugins'),
                    'aki.plugins')
    # use alembic instead
    # db.create_all()

    return bot
