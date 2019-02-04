import asyncio
from .Calculation import get_relation
from . import expressions as e
from nonebot import on_command, CommandSession
from nonebot.command.argfilter import extractors, converters
from nonebot import on_natural_language, NLPSession, IntentCommand
from nonebot.helpers import render_expression as expr


@on_command('relationship')
async def _(session: CommandSession):
    while 1:
        text = session.state.get('text')

        s = 1 if session.ctx['sender']['sex'] == 'male' or 'unknown' else 0  # 若获取不到性别(默认性别为“男”)
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
        result = '、'.join(get_relation({'text': text, 'sex': s, 'reverse': r, 'type': t}))

        # 输入格式不正确
        if result == '':
            session.state.pop('text')
            await session.send(expr(e.FAULT_INSERT))
            await asyncio.sleep(0.8)
            continue

        # 返回结果
        retu = expr(e.NAME) + result + expr(e.RE_ASK)
        session.get('con',
                    prompt=retu,
                    arg_filters=request_answer_filters)

        # 直接结束
        if not session.state['con']:
            session.finish(expr(e.MD_END_TASK))

        # 继续计算
        else:
            session.state.pop('text')
            session.state.pop('con')


@on_natural_language(keywords={'亲戚', '关系', '称呼', '关系推算'})
async def _(session: NLPSession):
    return IntentCommand(80.0, 'relationship')