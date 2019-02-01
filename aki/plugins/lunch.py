import asyncio
import random

from nonebot import on_command, CommandSession
from nonebot import on_natural_language, NLPSession, NLPResult
from nonebot.command.argfilter import extractors, converters
from nonebot.helpers import render_expression as expr

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

    request_answer_filters = [
        extractors.extract_text,
        str.strip,
        converters.simple_chinese_to_bool,
    ]

    if 'next1' not in session.state:
        # 先随机一个去处，问可不可以
        await session.send(expr(EXPR_WAIT))
        await asyncio.sleep(1)
        session.get('next1',
                    prompt=random.choice(where) + '吧，' + expr(EXPR_HOW),
                    arg_filters=request_answer_filters)

    if not session.state['next1']:
        # 去处被否决
        session.finish(expr(EXPR_CANCEL))

    # 去处 OK
    if 'next2' not in session.state:
        session.get('next2', prompt=expr(EXPR_REQU),
                    arg_filters=request_answer_filters)

    if not session.state['next2']:
        session.finish(expr(EXPR_CANCEL))

    await asyncio.sleep(0.8)
    await session.send('经奶茶精选，今天' + random.choice(kind) + '与你更配哦🤔')
    await asyncio.sleep(0.3)
    await session.send(expr(EXPR_EMOJI))


@on_natural_language(keywords={'吃什么', '吃啥', '哪吃', '哪儿吃', '哪里吃'})
async def _(session: NLPSession):
    return NLPResult(80.0, 'lunch')
