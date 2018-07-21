import functools
from typing import Callable, Any

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from none import get_bot

from .log import logger


def make_table_name(plugin_name: str, table_name: str) -> str:
    return f'{plugin_name.lower()}_{table_name.lower()}'


Base = declarative_base()
Session = sessionmaker()

_engine = None


def init() -> None:
    """
    Initialize database module.

    This must be called before any plugins using database,
    and after initializing "none" module.
    """
    logger.debug('Initializing database')
    bot_ = get_bot()
    global _engine
    logger.debug(
        f'Creating database engine, url: {repr(bot_.config.DATABASE_URL)}')
    _engine = create_engine(bot_.config.DATABASE_URL)
    Session.configure(bind=_engine)


def _require_engine(func: Callable) -> Callable:
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        if _engine is None:
            raise ValueError('SQLAlchemy engine object not initialized yet')
        return func(*args, **kwargs)

    return wrapper


@_require_engine
def get_engine() -> Any:
    return _engine


@_require_engine
def new_session(**kwargs) -> Session:
    """
    Create a new database session.
    :param kwargs: any keyword args needed for a session
    """
    return Session(**kwargs)


@_require_engine
def create_all() -> None:
    logger.debug(f'Creating all db tables: {",".join(Base.metadata.tables)}')
    Base.metadata.create_all(_engine)
