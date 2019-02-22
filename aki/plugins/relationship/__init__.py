import asyncio

from nonebot import on_command, CommandSession
from nonebot import on_natural_language, NLPSession, IntentCommand
from nonebot.command.argfilter import extractors, converters
from nonebot.helpers import render_expression as expr

from . import expressions as e
from .relationship import get_relation

__plugin_name__ = '亲戚关系计算器'


@on_command('relationship')
async def _(session: CommandSession):
    session.finish('本功能正在维护，暂时不可用咯')
    while True:
        text = session.state.get('text')

        if session.ctx['sender']['sex'] == 'male' or 'unknown':
            # 若获取不到性别(默认性别为“男”)
            s = 1
        else:
            s = 0
        r = False
        t = 'default'

        request_answer_filters = [
            extractors.extract_text,
            str.strip,
            converters.simple_chinese_to_bool,
        ]

        # 输入关系
        if 'text' not in session.state:
            session.get('text', prompt=expr(e.INPPUT_MESSAGE))

        # 计算结果
        result = '、'.join(
            get_relation({'text': text, 'sex': s, 'reverse': r, 'type': t})
        )

        # 输入格式不正确
        if result == '':
            session.state.pop('text')
            await session.send(expr(e.FAULT_INSERT))
            await asyncio.sleep(0.8)
            continue

        # 返回结果
        reply = f'{expr(e.NAME)}{result}，{expr(e.RE_ASK)}'
        session.get('con',
                    prompt=reply,
                    arg_filters=request_answer_filters)

        # 直接结束
        if not session.state['con']:
            session.finish(expr(e.MD_END_TASK))
        # 继续计算
        else:
            session.state.pop('text')
            session.state.pop('con')


@on_natural_language(keywords={'亲戚', '称呼', '关系推算', '关系计算'})
async def _(session: NLPSession):
    return IntentCommand(80.0, 'relationship')
