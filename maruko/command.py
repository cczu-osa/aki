import re
import functools
import atexit
from typing import Callable, Any

from none import CommandSession
from none.expression import render

from .nlp import ExampleSentence, calc_sentence_similarity

_cancellation_eg_sentences = [
    ExampleSentence('算了，不用了'),
    ExampleSentence('那不要了吧'),
    ExampleSentence('那别了吧'),
    ExampleSentence('那取消吧'),
]


@atexit.register
def _save_example_sentences() -> None:
    pass


async def handle_cancellation(session: CommandSession) -> None:
    """
    Handle cancellation instructions.

    If the current arg text is a cancellation instruction,
    the command session will be made finished, so that
    the command will no long be run.

    This function is present for manually calling through
    the process of a command's args parser, which means
    the args parser can do something before handle cancellation.
    On contrary, @allow_cancellation decorator will handle
    cancellation at the very beginning of the args parser.

    :param session: command session to handle
    """
    text = session.current_arg_text.strip()
    is_possible_cancellation = False
    for kw in ('算', '别', '不', '取消'):
        if kw in text:
            is_possible_cancellation = True
            break
    if not session.is_first_run and is_possible_cancellation:
        # we are in an interactive session, waiting for user's input
        if re.match(r'[算别不]\S{0,3}了吧?', text) or \
                re.match(r'取消了?吧?', text):
            match = True
        else:
            _, match = await calc_sentence_similarity(
                text, _cancellation_eg_sentences)
        if match:
            session.finish(
                render(session.bot.config.SESSION_CANCELLATION_EXPRESSION))


def allow_cancellation(func: Callable) -> Callable:
    """
    Decorate an args parser to handle cancellation instruction
    sent by users.
    """

    @functools.wraps(func)
    async def wrapper(session: CommandSession) -> Any:
        await handle_cancellation(session)
        return await func(session)

    return wrapper
