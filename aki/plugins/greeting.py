import random

from nonebot import on_natural_language, NLPSession, IntentCommand
from nonebot import permission as perm
from nonebot.helpers import render_expression as expr


@on_natural_language(keywords={'打个招呼', '打招呼'}, permission=perm.SUPERUSER)
async def _(session: NLPSession):
    if '大家' in session.msg_text:
        return IntentCommand(100.0, 'echo', args={'message': '大家好～'})


@on_natural_language(allow_empty_message=True)
async def _(session: NLPSession):
    if not session.msg.strip():
        # empty message body
        nicks = list(session.bot.config.NICKNAME)
        if nicks:
            nick = nicks[0]
        else:
            nick = None
        return IntentCommand(100.0, 'echo',
                             args={'message': expr(expr_ack, nick=nick)})


def expr_ack(**kwargs):
    nick = kwargs.pop('nick', None) or '我'
    return (random.choice(['小主人', '你']) +
            random.choice(['好呀', '好啊']) + '，' +
            nick + random.choice(['在呢', '在的', '听着呢']))
