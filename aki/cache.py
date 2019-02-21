from aiocache import caches
from nonebot import get_bot


def init() -> None:
    """
    Initialize the cache module.
    """
    bot = get_bot()
    caches.set_config({
        'default': bot.config.AIOCACHE_DEFAULT_CONFIG
    })
