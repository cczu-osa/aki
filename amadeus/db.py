import asyncio

from gino import Gino
from nonebot import get_bot

from .log import logger


def make_table_name(plugin_name: str, table_name: str) -> str:
    return f'{plugin_name.lower()}_{table_name.lower()}'


db = Gino()


def init() -> None:
    """
    Initialize database module.

    This must be called before any plugins using database,
    and after initializing "none" module.
    """
    logger.debug('Initializing database')
    bot = get_bot()
    if getattr(bot.config, 'DATABASE_URL', None):
        asyncio.get_event_loop().run_until_complete(
            db.set_bind(bot.config.DATABASE_URL))
    else:
        logger.warning('DATABASE_URL is missing, database may not work')


def create_all() -> None:
    """
    Create all database tables defined by plugins.
    """
    logger.debug(f'Creating all db tables: {",".join(db.tables)}')
    asyncio.get_event_loop().run_until_complete(db.gino.create_all())
