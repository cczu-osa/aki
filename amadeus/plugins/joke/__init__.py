from nonebot import on_command, CommandSession
from nonebot import on_natural_language, NLPSession, NLPResult

from .data_source import get_joke


@on_command('joke', aliases=['笑话'])
async def _(session: CommandSession):
    await session.send(await get_joke(session.bot))


@on_natural_language(keywords=['笑话', '段子'])
async def _(session: NLPSession):
    miss = max(0, len(session.msg_text) - 2) * 4
    return NLPResult(100.0 - miss, 'joke')
