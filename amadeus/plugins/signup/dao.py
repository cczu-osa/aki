import functools
import string
from typing import Optional, List, Dict, Any

from none.helpers import context_id
from none.typing import Context_T

from amadeus import dt
from amadeus.db import db
from amadeus.helpers import random_string
from amadeus.log import logger
from .models import Event, Signup

ctx_id_by_user = functools.partial(context_id, mode='user')


async def start_event(ctx: Context_T,
                      title: str,
                      fields: List[Dict[str, Any]]) -> Optional[Event]:
    try:
        return await Event.create(
            context_id=ctx_id_by_user(ctx),
            title=title,
            code=random_string(8, string.ascii_uppercase + string.digits),
            fields=fields,
            start_time=dt.beijing_now().timestamp()
        )
    except Exception as e:
        logger.exception(e)
        return None


async def end_event(event: Event) -> bool:
    try:
        await event.update(end_time=dt.beijing_now().timestamp()).apply()
        return True
    except Exception as e:
        logger.exception(e)
        return False


async def get_all_events(ctx: Context_T) -> List[Event]:
    try:
        return await Event.query.where(
            Event.context_id == ctx_id_by_user(ctx)).gino.all()
    except Exception as e:
        logger.exception(e)
        return []


async def get_event(code: str) -> Optional[Event]:
    try:
        return await Event.query.where(Event.code == code).gino.first()
    except Exception as e:
        logger.exception(e)
        return None


async def get_signup(ctx: Context_T, event: Event) -> Optional[Signup]:
    try:
        return await Signup.query.where(
            (Signup.context_id == ctx_id_by_user(ctx)) &
            (Signup.event_id == event.id)
        ).gino.first()
    except Exception as e:
        logger.exception(e)
        return None


async def create_signup(ctx: Context_T,
                        event: Event,
                        field_values: List[str]) -> Optional[Signup]:
    try:
        return await Signup.create(
            context_id=ctx_id_by_user(ctx),
            event_id=event.id,
            field_values=field_values,
            qq_number=ctx.get('user_id')
        )
    except Exception as e:
        logger.exception(e)
        return None


async def get_signup_count(event: Event) -> Optional[int]:
    try:
        return await db.select([db.func.count(Signup.id)]).where(
            Signup.event_id == event.id).gino.scalar()
    except Exception as e:
        logger.exception(e)
        return None


async def get_all_signups(event: Event) -> List[Signup]:
    try:
        return await Signup.query.where(Signup.event_id == event.id).gino.all()
    except Exception as e:
        logger.exception(e)
        return []
