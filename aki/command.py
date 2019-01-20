import functools
import re
from typing import Callable, Any

from nonebot import CommandSession
from nonebot.helpers import render_expression as __

from .log import logger
from .nlp import ExampleSentence, sentence_similarity_ex

_cancellation_eg_sentences = [
    ExampleSentence('算了，不用了'),
    ExampleSentence('那不要了吧'),
    ExampleSentence('那别了吧'),
    ExampleSentence('那取消吧'),
]


async def is_cancellation(sentence: str) -> bool:
    for kw in ('算', '别', '不', '取消'):
        if kw in sentence:
            # a keyword matches
            break
    else:
        # no keyword matches
        return False

    if re.match(r'^那?[算别不]\w{0,3}了吧?$', sentence) or \
            re.match(r'^那?(?:[给帮]我)?取消了?吧?$', sentence):
        match = True
    else:
        _, match = await sentence_similarity_ex(
            sentence, _cancellation_eg_sentences)
    return match


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
    if session.is_first_run:
        return

    # we are in an interactive session, waiting for user's input
    # handle possible cancellation

    # use current_arg_text, we don't mind losing rich text parts of message
    text = session.current_arg_text.strip()
    small_sentences = re.split(r'\W+', text)
    logger.debug(f'Split small sentences: {small_sentences}')

    should_cancel = False
    new_ctx_message = None
    for i, sentence in enumerate(filter(lambda x: x.strip(), small_sentences)):
        if await is_cancellation(sentence):
            logger.debug(f'Sentence "{sentence}" is a cancellation, continue')
            should_cancel = True
            continue

        # this small sentence is not a cancellation, we split before this
        new_ctx_message = '，'.join(small_sentences[i:]).strip()
        break

    if should_cancel:
        if not new_ctx_message:
            session.finish(__(session.bot.config.SESSION_CANCEL_EXPRESSION))
        else:
            session.switch(new_ctx_message)


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
