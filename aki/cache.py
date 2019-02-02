from aiocache import caches, cached as raw_cached
from nonebot import get_bot


def init() -> None:
    """
    Initialize the cache module.
    """
    bot = get_bot()
    caches.set_config({
        'default': bot.config.AIOCACHE_DEFAULT_CONFIG
    })


def cached(*args, **kwargs):
    """
    Wraps aiocache.cached decorator to use "default" cache.
    """
    return raw_cached(alias='default', *args, **kwargs)
