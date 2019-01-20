import asyncio
import random

from nonebot import on_command, CommandSession
from nonebot import on_natural_language, NLPSession, NLPResult
from nonebot.helpers import render_expression as __

from aki.command import allow_cancellation
from aki.nlp import check_confirmation

__plugin_name__ = '吃什么'

EXPR_WAIT = (
    '等会儿，让奶茶先想想去哪儿吃',
    '等等啊，容奶茶思考片刻，去哪儿呢🙄',
)

EXPR_HOW = (
    '可还行？', '怎样？', '咋样？', '怎么样？', '可以嘛？',
)

EXPR_REQU = (
    '需要我帮你决定吃点什么吗',
)

EXPR_CANCEL = (
    '那小主人你自己决定吧～',
)

EXPR_EMOJI = (
    '🥙 🌮 🌯 🥗 🥘',
    '🍤 🍙 🍚 🍘 🍥',
    '🍰 🎂 🍮 🍭 🍬',
    '🍇 🍗 🍖 🌭 🍔',
    '🥂 🍷 🥃 🍸 🍹',
)


@on_command('lunch')
async def lunch(session: CommandSession):
    where = ['去一食堂', '去二食堂', '吃日夜', '点外卖', '出去吃']
    kind = ['面条', '饭', '炒饭', '早点', '砂锅']

    next1 = session.get_optional('next1')
    next2 = session.get_optional('next2')

    if next1 is None:
        # 先随机一个去处，问可不可以
        await session.send(__(EXPR_WAIT))
        await asyncio.sleep(1)
        session.get('next1',
                    prompt=random.choice(where) + '吧，' + __(EXPR_HOW))

    if next2 is None and check_confirmation(next1) is not True:
        # 去处被否决
        session.finish(__(EXPR_CANCEL))

    # 去处 OK
    if next2 is None:
        session.get('next2', prompt=__(EXPR_REQU))

    if check_confirmation(next2) is not True:
        session.finish(__(EXPR_CANCEL))

    await asyncio.sleep(0.8)
    await session.send('经奶茶精选，今天' + random.choice(kind) + '与你更配哦🤔')
    await asyncio.sleep(0.3)
    await session.send(__(EXPR_EMOJI))


@lunch.args_parser
@allow_cancellation
async def _(session: CommandSession):
    if session.is_first_run:
        return
    session.args[session.current_key] = session.current_arg_text.strip()


@on_natural_language(keywords={'吃什么', '吃啥', '哪吃', '哪儿吃', '哪里吃'})
async def _(session: NLPSession):
    return NLPResult(80.0, 'lunch')
