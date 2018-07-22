import re
import functools
from typing import Callable, Any

from none import CommandSession
from none.expression import render


def handle_cancellation(func: Callable) -> Callable:
    """
    Decorate an args parser to handle cancellation instruction
    sent by users.
    """

    @functools.wraps(func)
    async def wrapper(session: CommandSession) -> Any:
        if session.current_key:
            # we are in an interactive session, waiting for user's input
            if re.match(r'(?:算|别|不)\S{0,4}了吧?|取消了?吧?',
                        session.current_arg_text.strip()):
                session.finish(
                    render(session.bot.config.SESSION_CANCELLATION_EXPRESSION))
                return
        return await func(session)

    return wrapper
