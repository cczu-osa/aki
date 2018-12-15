from aiocache import caches, cached as raw_cached
from none import get_bot


def init() -> None:
    """
    Initialize the cache module.

    This must be called before any plugins using cache,
    and after initializing "none" module.
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
