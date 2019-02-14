from nonebot import on_command, CommandSession
from nonebot import on_natural_language, NLPSession, IntentCommand

from .data_source import get_joke

__plugin_name__ = '段子'


@on_command('joke', aliases=['笑话'], only_to_me=False)
async def _(session: CommandSession):
    await session.send(await get_joke(session.bot))


@on_natural_language(keywords=['笑话', '段子'])
async def _(session: NLPSession):
    miss = max(0, len(session.msg_text) - 2) * 4
    return IntentCommand(100.0 - miss, 'joke')
