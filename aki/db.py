from gino import Gino
from nonebot import get_bot

from .log import logger


def make_table_name(plugin_name: str, table_name: str) -> str:
    return f'{plugin_name.lower()}_{table_name.lower()}'


db = Gino()


async def init() -> None:
    """
    Initialize database module.
    """
    logger.debug('Initializing database')
    bot = get_bot()
    if getattr(bot.config, 'DATABASE_URL', None):
        await db.set_bind(bot.config.DATABASE_URL)
        logger.info('Database connected')
    else:
        logger.warning('DATABASE_URL is missing, database may not work')
