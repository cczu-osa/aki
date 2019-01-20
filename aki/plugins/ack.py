import random

from nonebot import on_natural_language, NLPSession
from nonebot.helpers import render_expression as __


def EXPR_ACK(**kwargs):
    nick = kwargs.pop('nick', None) or '我'
    return (random.choice(['小主人', '你']) +
            random.choice(['好呀', '好啊']) + '，' +
            nick + random.choice(['在呢', '在的', '听着呢']))


@on_natural_language(allow_empty_message=True)
async def _(session: NLPSession):
    if not session.msg:
        # empty message body
        nicks = list(session.bot.config.NICKNAME)
        if nicks:
            nick = nicks[0]
        else:
            nick = None
        await session.send(__(EXPR_ACK, nick=nick))
